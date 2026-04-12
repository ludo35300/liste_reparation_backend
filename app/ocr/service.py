# app/ocr/service.py
import io, base64
from PIL import Image

from app.models.reference  import MachineTypeRef, PieceRef
from app.models.user       import User
from app.integrations      import mistral
from app.utils.fuzzy       import fuzzy_machine, fuzzy_piece
from app.utils.dates       import normaliser_date_ocr
from app.utils.strings     import normaliser_ref

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
- "nom"     : prénom ou nom manuscrit après "NOM:" — retourne UNIQUEMENT le texte manuscrit
- "date"    : date manuscrite après "DATE:", format JJ/MM/AA strict
- "numero"  : chiffres manuscrits après "NUMERO:" ou "N°" — chiffres uniquement
- "machine" : modèle imprimé centré en haut de fiche
- "pieces"  : UNIQUEMENT les lignes où QUANTITE contient un chiffre manuscrit ou cerclé
- Si un champ est illisible ou absent, retourne une chaîne vide "" (jamais null)"""


# ── Référentiels BDD ──────────────────────────────────────────
def _pieces_connues() -> dict:
    return {p.ref_piece.upper(): p.designation for p in PieceRef.query.all()}

def _labels_machines() -> list:
    return [m.label.upper() for m in MachineTypeRef.query.all()]

def _prenoms_techniciens() -> list:
    return [u.first_name.upper() for u in User.query.all()]


# ── Compression image ─────────────────────────────────────────
def _compresser_image(file_bytes: bytes, max_width: int = 2400, qualite: int = 80) -> str:
    #Image.MAX_IMAGE_PIXELS = None
    image = Image.open(io.BytesIO(file_bytes))
    #image.draft("RGB", (max_width, max_width * 2))
    image = image.convert("RGB")
    w, h  = image.size
    if w > max_width:
        image = image.resize((max_width, int(h * max_width / w)), Image.LANCZOS)
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=qualite, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    del image, buf
    return b64


# ── Résolution technicien ─────────────────────────────────────
def _resoudre_technicien(nom_brut: str, techniciens: list,
                         fallback_user_id: int | None = None) -> str:
    from difflib import get_close_matches
    if nom_brut and techniciens:
        matches = get_close_matches(nom_brut.upper(), techniciens, n=1, cutoff=0.6)
        if matches:
            return matches[0]
    if fallback_user_id:
        user = User.query.get(fallback_user_id)
        if user:
            return user.first_name.upper()
    return nom_brut.upper() if nom_brut else ""


# ── Fonction principale ───────────────────────────────────────
def analyser_fiche(file_bytes: bytes, fallback_user_id: int | None = None) -> dict:
    b64 = _compresser_image(file_bytes)
    del file_bytes

    texte_ocr = mistral.extraire_texte_ocr(b64)
    del b64
    if not texte_ocr:
        return {"erreur": "OCR échoué", "pieces": [], "nb_pieces_total": 0}

    pieces_connues  = _pieces_connues()
    labels_machines = _labels_machines()
    techniciens     = _prenoms_techniciens()

    refs_connues = "\n".join(f"- {r}: {d}" for r, d in pieces_connues.items())
    data = mistral.extraire_json_structure(texte_ocr, refs_connues, PROMPT_JSON)
    if not data:
        return {"erreur": "Extraction JSON échouée", "pieces": [], "nb_pieces_total": 0}

    machine_corrigee, is_new_machine = fuzzy_machine(
        data.get("machine", "").strip().upper(), labels_machines
    )
    technicien = _resoudre_technicien(
        data.get("nom", "").strip(), techniciens, fallback_user_id
    )

    pieces = []
    for p in data.get("pieces", []):
        ref_brute = normaliser_ref(p.get("ref", ""))
        qte       = int(p.get("quantite", 0))
        if not ref_brute or qte <= 0:
            continue
        ref_corrigee, designation, is_new = fuzzy_piece(ref_brute, pieces_connues)
        pieces.append({
            "ref_piece":   ref_corrigee,
            "designation": designation or p.get("designation", "").strip().upper(),
            "quantite":    qte,
            "is_new":      is_new,
        })

    return {
        "technicien":      technicien,
        "date":            normaliser_date_ocr(data.get("date", "")),
        "numero_serie":    normaliser_ref(data.get("numero", "")),
        "machine_type":    machine_corrigee,
        "is_new_machine":  is_new_machine,
        "pieces":          pieces,
        "nb_pieces_total": sum(p["quantite"] for p in pieces),
    }