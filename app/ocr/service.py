import io
import base64
import logging
from datetime import datetime, timedelta, timezone

from PIL import Image

from app.models.modele   import Modele
from app.models.piece_ref import PieceRef
from app.models.user     import User
from app.integrations    import mistral
from app.utils.fuzzy     import fuzzy_machine, fuzzy_piece
from app.utils.dates     import normaliser_date_ocr
from app.utils.strings   import normaliser_ref

logger = logging.getLogger(__name__)

PROMPT_JSON = """Voici le texte extrait d'une fiche de réparation de moulin à café ou d'une machine à café:


TEXTE OCR EXTRAIT :
{texte_ocr}


RÉFÉRENCES PIÈCES CONNUES (utilise-les en priorité pour corriger les refs) :
{refs_connues}


Réponds UNIQUEMENT en JSON strict, sans texte autour, sans balises markdown :
{{
  "nom": "...",
  "date": "JJ/MM/AA",
  "numero": "...",
  "machine": "...",
  "pieces": [
    {{"ref": "...", "designation": "...", "quantite": 1}}
  ]
}}

Règles strictes :
- "nom" : texte manuscrit après "NOM:" — retourne la valeur brute même si étrange
- "date" : date manuscrite après "DATE:", format JJ/MM/AA strict
- "numero" : chiffres après "NUMERO:" ou "N°", sans espaces ni caractères spéciaux
- "machine" : modèle pré-imprimé en gras, centré, en majuscules (ex: "MOULIN SANTOS 40AN")
- "pieces" : uniquement les lignes où QUANTITE contient un chiffre manuscrit ou cerclé
- "ref" : conserve les espaces et lettres tels quels
- Si un champ est illisible ou absent, retourne "" (jamais null)"""

_cache: dict = {}
_CACHE_TTL = timedelta(minutes=5)


def _get_cached(key: str, loader):
    now = datetime.now(timezone.utc)
    if key not in _cache or (now - _cache[key]["ts"]) > _CACHE_TTL:
        _cache[key] = {"data": loader(), "ts": now}
    return _cache[key]["data"]


def _pieces_connues() -> dict:
    return _get_cached(
        "pieces",
        lambda: {p.ref_piece.upper(): p.designation for p in PieceRef.query.all()}
    )


def _labels_machines() -> list:
    """Labels = 'type_machine marque nom' pour chaque modèle."""
    return _get_cached(
        "machines",
        lambda: [m.label.upper() for m in Modele.query.all()]
    )


def _prenoms_techniciens() -> list:
    return _get_cached(
        "techniciens",
        lambda: [u.first_name.upper() for u in User.query.all()]
    )


def _deduire_machine_depuis_pieces(pieces: list, labels_machines: list) -> str:
    """Fallback : déduit le modèle depuis les refs pièces détectées."""
    if not pieces or not labels_machines:
        return ""

    refs_fiche = {p["ref_piece"] for p in pieces}
    meilleur_label = ""
    meilleur_score = 0

    for modele in Modele.query.all():
        refs_modele = {pr.ref_piece.upper() for pr in modele.pieces}
        if not refs_modele:
            continue
        score = len(refs_fiche & refs_modele)
        if score > meilleur_score:
            meilleur_score = score
            meilleur_label = modele.label.upper()

    if meilleur_score >= 2:
        logger.info(f"Machine déduite depuis les pièces : '{meilleur_label}' (score={meilleur_score})")
        return meilleur_label

    logger.warning(f"Impossible de déduire la machine (meilleur score={meilleur_score})")
    return ""


def _compresser_image(file_bytes: bytes, qualite: int = 85, max_dim: int = 1920) -> str:
    image = Image.open(io.BytesIO(file_bytes))
    if max(image.size) > max_dim:
        image.thumbnail((max_dim, max_dim), Image.LANCZOS)
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=qualite, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    del image, buf
    return b64


def _safe_int(val, default: int = 0) -> int:
    try:
        return max(0, int(float(str(val).strip())))
    except (ValueError, TypeError):
        return default


def _resoudre_technicien(nom_brut: str, techniciens: list,
                         fallback_user_id: int | None = None) -> str:
    from difflib import get_close_matches
    if nom_brut and techniciens:
        matches = get_close_matches(nom_brut.upper(), techniciens, n=1, cutoff=0.6)
        if matches:
            return matches[0]
    if fallback_user_id:
        from app.extensions import db
        user = db.session.get(User, fallback_user_id)
        if user:
            return user.first_name.upper()
    return nom_brut.upper() if nom_brut else ""


def analyser_fiche(file_bytes: bytes, fallback_user_id: int | None = None) -> dict:
    try:
        b64 = _compresser_image(file_bytes)
        del file_bytes

        pieces_dict   = _pieces_connues()
        labels_mach   = _labels_machines()
        techniciens   = _prenoms_techniciens()
        refs_connues  = list(pieces_dict.keys())

        prompt = PROMPT_JSON.format(
            texte_ocr="(image fournie directement)",
            refs_connues=", ".join(refs_connues[:80])
        )

        raw = mistral.analyser_image_json(b64, ", ".join(refs_connues[:80]), prompt)
        if not raw or "erreur" in raw:
            return {"erreur": raw.get("erreur", "Réponse Mistral invalide"),
                    "pieces": [], "nb_pieces_total": 0}

        # ── Résolution machine ────────────────────────────────
        machine_brute = raw.get("machine", "").strip().upper()
        machine_corrigee, score_machine = fuzzy_machine(machine_brute, labels_mach)
        if not machine_corrigee:
            pieces_brutes = [
                {"ref_piece": normaliser_ref(p.get("ref", ""))}
                for p in raw.get("pieces", []) if p.get("ref")
            ]
            machine_corrigee = _deduire_machine_depuis_pieces(pieces_brutes, labels_mach)

        # ── Résolution technicien ─────────────────────────────
        nom_brut    = raw.get("nom", "").strip()
        technicien  = _resoudre_technicien(nom_brut, techniciens, fallback_user_id)

        # ── Résolution pièces ─────────────────────────────────
        pieces_out = []
        for p in raw.get("pieces", []):
            ref_brute   = normaliser_ref(p.get("ref", ""))
            quantite    = _safe_int(p.get("quantite", 1), default=1)
            if not ref_brute or quantite < 1:
                continue
            ref_corrigee, designation, score = fuzzy_piece(
                ref_brute, pieces_dict, cutoff=0.75
            )
            pieces_out.append({
                "ref_piece":   ref_corrigee,
                "designation": designation or p.get("designation", ""),
                "quantite":    quantite,
                "is_new":      ref_corrigee not in pieces_dict,
                "score_ocr":   round(score, 2),
            })

        date_norm = normaliser_date_ocr(raw.get("date", ""))

        return {
            "technicien":      technicien,
            "date":            date_norm,
            "numero_serie":    raw.get("numero", "").strip(),
            "machine_type":    machine_corrigee,
            "is_new_machine":  machine_corrigee not in labels_mach,
            "pieces":          pieces_out,
            "nb_pieces_total": sum(p["quantite"] for p in pieces_out),
        }

    except Exception as exc:
        logger.exception("Erreur analyser_fiche")
        return {"erreur": str(exc), "pieces": [], "nb_pieces_total": 0}
