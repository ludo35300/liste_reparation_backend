# app/ocr/service.py
"""
Service principal d'analyse de fiches de réparation par OCR via Mistral.

Flux :
    1. Compression de l'image (JPEG optimisé)
    2. Appel unique Mistral (image + prompt JSON en une seule requête)
    3. Correction floue : machine_type et refs pièces
    4. Résolution du technicien (fuzzy + fallback utilisateur connecté)
    5. Retour d'un dict structuré prêt à être enregistré
"""

import io
import base64
import logging
from datetime import datetime, timedelta

from PIL import Image

from app.models.reference import MachineTypeRef, PieceRef
from app.models.user      import User
from app.integrations     import mistral
from app.utils.fuzzy      import fuzzy_machine, fuzzy_piece
from app.utils.dates      import normaliser_date_ocr
from app.utils.strings    import normaliser_ref

logger = logging.getLogger(__name__)


# ── Prompt Mistral ────────────────────────────────────────────────────────────
# Le prompt est injecté directement avec l'image (un seul appel API).
# Les {refs_connues} sont injectées dynamiquement pour aider Mistral
# à corriger les références pièces détectées par OCR.
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
- "nom" :
  - Texte manuscrit situé après "NOM:" en haut à gauche de la fiche
  - Si le texte ressemble à un prénom ou nom (lettres), retourne-le
  - Si l'OCR retourne des chiffres à la place (ex: "1000"), tente quand même
    de retourner la valeur brute — ce sera corrigé par fuzzy matching côté serveur
  - Retourne TOUJOURS la valeur brute après "NOM:", même si elle semble étrange
- "date"    : date manuscrite après "DATE:", format JJ/MM/AA strict 
- "numero" :
  - Chiffres manuscrits situés après "NUMERO:" ou "N°" en haut à droite
  - Retourne UNIQUEMENT les chiffres, sans espaces ni caractères spéciaux
  - Exemple : "959280"
- "machine" :
  - Modèle imprimé en gras, centré horizontalement dans le haut de la fiche
  - Ce texte est PRÉ-IMPRIMÉ (pas manuscrit), souvent en majuscules grasses
  - Il est situé ENTRE la zone NOM/DATE/NUMERO en haut et au dessus du tableau REF/QUANTITE/DESIGNATION
  - Exemples typiques : "MOULIN SANTOS 40AN", "MOULIN SANTOS 45", "CONTI CC100"
  - Retourne le texte EXACT tel qu'imprimé, en majuscules, sans l'interpréter
- "pieces"  : UNIQUEMENT les lignes où QUANTITE contient un chiffre manuscrit ou cerclé
-"ref" : conserve les espaces et lettres tels quels : "00001 B" reste "00001 B", pas "00001B"
- Si un champ est illisible ou absent, retourne une chaîne vide "" (jamais null)"""

# ── Cache en mémoire pour les référentiels BDD ────────────────────────────────
# Les données de référence (pièces, machines, techniciens) changent rarement.
# On évite ainsi 3 requêtes SQL à chaque analyse en les mémorisant 5 minutes.
_cache: dict = {}
_CACHE_TTL = timedelta(minutes=5)
def _get_cached(key: str, loader):
    """
    Retourne la donnée en cache si elle est encore fraîche (< TTL),
    sinon la recharge depuis la BDD et met à jour le cache.
    """
    now = datetime.utcnow()
    if key not in _cache or (now - _cache[key]["ts"]) > _CACHE_TTL:
        _cache[key] = {"data": loader(), "ts": now}
    return _cache[key]["data"]
def _pieces_connues() -> dict:
    """Retourne {REF_PIECE_UPPER: designation} depuis le cache ou la BDD."""
    return _get_cached(
        "pieces",
        lambda: {p.ref_piece.upper(): p.designation for p in PieceRef.query.all()}
    )
def _labels_machines() -> list:
    """Retourne la liste des labels machines en majuscules (pour fuzzy matching)."""
    return _get_cached(
        "machines",
        lambda: [m.label.upper() for m in MachineTypeRef.query.all()]
    )
def _prenoms_techniciens() -> list:
    """Retourne la liste des prénoms techniciens en majuscules (pour fuzzy matching)."""
    return _get_cached(
        "techniciens",
        lambda: [u.first_name.upper() for u in User.query.all()]
    )
def _deduire_machine_depuis_pieces(pieces: list, labels_machines: list) -> str:
    """
    Fallback : tente de déduire le type de machine depuis les refs pièces détectées,
    en cherchant dans la BDD quelle machine utilise le plus de pièces de la liste.

    Utile quand le nom de machine est absent ou illisible sur la photo (image de biais,
    haut de fiche hors cadre, etc.).

    Retourne le label machine le plus probable, ou "" si aucune correspondance.
    """
    from app.models.reference import MachineTypeRef

    if not pieces or not labels_machines:
        return ""

    # Récupère les refs détectées sur la fiche (normalisées)
    refs_fiche = {p["ref_piece"] for p in pieces}

    meilleur_label = ""
    meilleur_score = 0

    for machine in MachineTypeRef.query.all():
        # Refs connues pour cette machine (via la table d'association machine_piece_refs)
        refs_machine = {pr.ref_piece.upper() for pr in machine.pieces}

        if not refs_machine:
            continue

        # Score = nombre de refs de la fiche présentes dans cette machine
        score = len(refs_fiche & refs_machine)

        if score > meilleur_score:
            meilleur_score = score
            meilleur_label = machine.label.upper()

    # On n'accepte la déduction que si au moins 2 pièces correspondent
    # (1 seule correspondance peut être une coïncidence)
    if meilleur_score >= 2:
        print(f"[SERVICE] 🔍 Machine déduite depuis les pièces : "
              f"'{meilleur_label}' (score={meilleur_score})")
        return meilleur_label

    print(f"[SERVICE] ⚠️  Impossible de déduire la machine "
          f"(meilleur score={meilleur_score}, seuil=2)")
    return ""
# ── Compression image ─────────────────────────────────────────────────────────
def _compresser_image(file_bytes: bytes, qualite: int = 85,
                      max_dim: int = 1920) -> str:
    """
    Compresse l'image en JPEG base64 pour l'envoi à l'API Mistral.

    Optimisations :
    - Redimensionnement si > max_dim px : inutile au-delà pour l'OCR,
      réduit fortement la taille du payload envoyé à l'API.
    - Conversion forcée en RGB : évite une OSError si l'image source
      est un PNG avec canal alpha (RGBA) ou en mode palette (P).
    - quality=85: réduit ~40% la taille sans impact
      visible sur la lisibilité des textes manuscrits.
    """
    image = Image.open(io.BytesIO(file_bytes))

    # Redimensionner si la dimension maximale dépasse le seuil
    if max(image.size) > max_dim:
        image.thumbnail((max_dim, max_dim), Image.LANCZOS)

    # JPEG ne supporte que RGB/L — convertir si nécessaire (ex: PNG RGBA)
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")

    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=qualite, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    del image, buf
    return b64
# ── Conversion sécurisée de quantité ─────────────────────────────────────────
def _safe_int(val, default: int = 0) -> int:
    """
    Convertit une valeur en entier sans lever d'exception.
    Mistral peut retourner "2" (str), 2.0 (float) ou une valeur vide.
    On passe par float() pour gérer "1.0" avant int().
    """
    try:
        return max(0, int(float(str(val).strip())))
    except (ValueError, TypeError):
        return default
# ── Résolution du technicien ──────────────────────────────────────────────────
def _resoudre_technicien(nom_brut: str, techniciens: list,
                         fallback_user_id: int | None = None) -> str:
    """
    Tente de retrouver le technicien exact à partir du nom OCR (potentiellement
    mal orthographié) via difflib.get_close_matches.

    Ordre de priorité :
    1. Correspondance floue sur la liste des techniciens (cutoff=0.6)
    2. Fallback sur l'utilisateur connecté (fallback_user_id)
    3. Retour du nom brut en majuscules si aucune correspondance
    """
    from difflib import get_close_matches

    if nom_brut and techniciens:
        matches = get_close_matches(nom_brut.upper(), techniciens, n=1, cutoff=0.6)
        if matches:
            return matches[0]

    # Fallback : on utilise l'utilisateur connecté (id passé par le controller)
    if fallback_user_id:
        # db.session.get() est la syntaxe SQLAlchemy 2.x (User.query.get() est déprécié)
        from app.extensions import db
        user = db.session.get(User, fallback_user_id)
        if user:
            return user.first_name.upper()

    return nom_brut.upper() if nom_brut else ""
# ── Fonction principale ───────────────────────────────────────────────────────
def analyser_fiche(file_bytes: bytes, fallback_user_id: int | None = None) -> dict:
    """
    Analyse complète d'une fiche de réparation à partir des bytes de l'image.

    Paramètres :
        file_bytes        -- contenu brut du fichier image (jpg, png, etc.)
        fallback_user_id  -- ID de l'utilisateur connecté, utilisé si le nom
                             du technicien est illisible sur la fiche

    Retourne :
        dict avec les clés : technicien, date, numero_serie, machine_type,
                             is_new_machine, pieces, nb_pieces_total
        ou dict {"erreur": ..., "pieces": [], "nb_pieces_total": 0} en cas d'échec
    """
    try:
        # Étape 1 : compression + encodage base64 de l'image
        b64 = _compresser_image(file_bytes)
        del file_bytes  # Libération mémoire immédiate

        # Étape 2 : appel unique à Mistral (image + prompt → JSON directement)
        # On évite un double appel (OCR puis structuration) en fusionnant les deux.
        # mistral.analyser_image_json doit envoyer l'image b64 + PROMPT_JSON en une seule requête.
        pieces_connues  = _pieces_connues()
        labels_machines = _labels_machines()
        techniciens     = _prenoms_techniciens()

        refs_connues = "\n".join(f"- {r}: {d}" for r, d in pieces_connues.items())
        data = mistral.analyser_image_json(b64, refs_connues, PROMPT_JSON)
        del b64  # Libération mémoire après envoi

        if not data:
            return {"erreur": "Extraction JSON échouée", "pieces": [], "nb_pieces_total": 0}

        # Étape 3 : traitement de chaque pièce détectée
        pieces = []
        for p in data.get("pieces", []):
            ref_brute = normaliser_ref(p.get("ref", ""))
            qte       = _safe_int(p.get("quantite", 0))  # Conversion sécurisée

            # On ignore les lignes sans référence ou avec quantité nulle/négative
            if not ref_brute or qte <= 0:
                continue

            # fuzzy_piece retourne (ref_corrigée, designation, is_new) :
            # is_new=True si la ref n'existe pas dans le catalogue connu
            ref_corrigee, designation, is_new = fuzzy_piece(ref_brute, pieces_connues)

            pieces.append({
                "ref_piece":   ref_corrigee,
                # Priorité à la designation du catalogue ; fallback sur celle de Mistral
                "designation": designation or p.get("designation", "").strip().upper(),
                "quantite":    qte,
                "is_new":      is_new,  # Signale les nouvelles pièces à valider
            })
        # Étape 4 : correction floue du type de machine
        # fuzzy_machine retourne (label_corrigé, is_new) :
        # is_new=True si aucune machine connue ne correspond (seuil non atteint)

        machine_corrigee, is_new_machine = fuzzy_machine(
            data.get("machine", "").strip().upper(), labels_machines
        )
        # Fallback : si machine non détectée ET qu'on a des pièces connues,
        # on peut déduire la machine depuis les refs
        if not machine_corrigee and pieces_connues:
            machine_corrigee = _deduire_machine_depuis_pieces(pieces, labels_machines)
            is_new_machine = (machine_corrigee == "")

            
        # Étape 5 : résolution du technicien par fuzzy matching
        technicien = _resoudre_technicien(
            data.get("nom", "").strip(), techniciens, fallback_user_id
        )

        

        return {
            "technicien":      technicien,
            "date":            normaliser_date_ocr(data.get("date", "")),
            "numero_serie":    normaliser_ref(data.get("numero", "")),
            "machine_type":    machine_corrigee,
            "is_new_machine":  is_new_machine,  # True → à valider/créer en BDD
            "pieces":          pieces,
            "nb_pieces_total": sum(p["quantite"] for p in pieces),
        }

    except Exception as exc:
        # On logue l'exception complète côté serveur (traceback)
        # mais on retourne un message générique au client pour ne pas exposer l'erreur
        logger.exception("Erreur inattendue dans analyser_fiche : %s", exc)
        return {
            "erreur": f"Erreur inattendue : {type(exc).__name__}",
            "pieces": [],
            "nb_pieces_total": 0,
        }