import re
import os
import json
import base64
import time
import io
import requests
from PIL import Image
from difflib import get_close_matches
from flask_jwt_extended import get_jwt_identity
from app.models.reference import MachineTypeRef, PieceRef
from app.models.user import User

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

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
- "nom"     : prénom ou nom manuscrit après "NOM:" — retourne UNIQUEMENT le texte manuscrit, pas le mot "NOM"
- "date"    : date manuscrite après "DATE:", format JJ/MM/AA strict (année 2 chiffres)
- "numero"  : chiffres manuscrits après "NUMERO:" ou "N°" — chiffres uniquement, sans espaces
- "machine" : modèle imprimé centré en haut de fiche (ex: MOULIN SANTOS 40AN) — texte imprimé, pas manuscrit
- "pieces"  : UNIQUEMENT les lignes où la colonne QUANTITE contient un chiffre manuscrit ou cerclé (① = 1, ② = 2, ③ = 3)
              Pour chaque pièce, si la référence ressemble à une référence connue, utilise la référence connue exacte
              Ignore TOUTES les lignes avec QUANTITE vide ou illisible
- Si un champ est illisible ou absent, retourne une chaîne vide "" (jamais null)"""


# ─────────────────────────────────────────────────────────────────────────────
# Chargement des référentiels BDD
# ─────────────────────────────────────────────────────────────────────────────
def _charger_pieces_connues() -> dict:
    return {p.ref_piece.upper(): p.designation for p in PieceRef.query.all()}

def _charger_machines_connues() -> list:
    return [m.label.upper() for m in MachineTypeRef.query.all()]

def _charger_techniciens_connus() -> list:
    return [u.first_name.upper() for u in User.query.all()]

# ─────────────────────────────────────────────────────────────────────────────
# Fuzzy matching
# 
def _fuzzy_machine(machine_brute: str, labels: list) -> tuple:
    if not machine_brute or not labels:
        return machine_brute.upper() if machine_brute else "", True

    matches = get_close_matches(machine_brute.upper(), labels, n=1, cutoff=0.6)
    if matches:
        print(f"[Fuzzy] Machine \'{machine_brute}\' → \'{matches[0]}\'")
        return matches[0], False

    print(f"[Fuzzy] Machine \'{machine_brute}\' inconnue → nouvelle")
    return machine_brute.upper(), True

def _fuzzy_piece(ref_brute: str, pieces_connues: dict, designation_mistral: str) -> tuple:
    ref = ref_brute.upper()

    if ref in pieces_connues:
        return ref, pieces_connues[ref], False

    matches = get_close_matches(ref, list(pieces_connues.keys()), n=1, cutoff=0.75)
    if matches:
        ref_corrigee = matches[0]
        print(f"[Fuzzy] Pièce \'{ref}\' → \'{ref_corrigee}\'")
        return ref_corrigee, pieces_connues[ref_corrigee], False

    print(f"[Fuzzy] Pièce \'{ref}\' inconnue → nouvelle")
    return ref, designation_mistral, True

def _resoudre_technicien(nom_brut: str, techniciens: list) -> str:
    """
    1. Fuzzy match sur la liste des users
    2. Sinon → prénom de l\'utilisateur connecté (JWT)
    3. Sinon → nom brut OCR
    """
    if nom_brut and techniciens:
        matches = get_close_matches(nom_brut.upper(), techniciens, n=1, cutoff=0.6)
        if matches:
            print(f"[Fuzzy] Technicien \'{nom_brut}\' → \'{matches[0]}\'")
            return matches[0]

    return nom_brut.upper() if nom_brut else ""

# ─────────────────────────────────────────────────────────────────────────────
# Compression image
# ─────────────────────────────────────────────────────────────────────────────
def _compresser_image(file_bytes, max_width=1000, qualite=72):
    Image.MAX_IMAGE_PIXELS = None 
    image = Image.open(io.BytesIO(file_bytes)) # Ouvre sans décoder les pixels
    image.draft("RGB", (max_width, max_width * 2))# Réduit dès la lecture — évite de charger 200MP en RAM
    image = image.convert("RGB")
    w, h = image.size
    print(f"[OCR] Taille après draft : {w}x{h} px")
    # Redimensionnement final précis
    if w > max_width:
        image = image.resize((max_width, int(h * max_width / w)), Image.LANCZOS)
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=qualite, optimize=True)
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    print(f"[OCR] Image compressée : {len(b64) // 1024} Ko")
    del image, buffer
    return b64

# ─────────────────────────────────────────────────────────────────────────────
# Appels Mistral
# ─────────────────────────────────────────────────────────────────────────────
def _appel_mistral_ocr(b64):
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type":  "application/json",
    }
    payload = {
        "model":    "mistral-ocr-latest",
        "document": {"type": "image_url", "image_url": f"data:image/jpeg;base64,{b64}"},
    }
    for tentative in range(3):
        try:
            r = requests.post("https://api.mistral.ai/v1/ocr", headers=headers, json=payload, timeout=30)
            r.raise_for_status()
            pages = r.json().get("pages", [])
            if pages:
                texte = pages[0].get("markdown", "")
                print(f"[Mistral OCR] Texte extrait :\n{texte[:600]}")
                return texte
            return ""
        except requests.exceptions.HTTPError as e:
            if r.status_code == 429:
                attente = 15 * (tentative + 1)
                print(f"[Mistral OCR] Rate limit, attente {attente}s... ({tentative+1}/3)")
                time.sleep(attente)
            else:
                print(f"[Mistral OCR] Erreur {r.status_code} : {r.text}")
                raise e
    return ""

def _appel_mistral_json(texte_ocr: str, refs_connues: str):
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type":  "application/json",
    }
    payload = {
        "model":    "mistral-small-latest",
        "messages": [{
            "role":    "user",
            "content": PROMPT_JSON.format(texte_ocr=texte_ocr, refs_connues=refs_connues),
        }],
    }
    for tentative in range(3):
        try:
            r = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers=headers, json=payload, timeout=30,
            )
            r.raise_for_status()
            texte = r.json()["choices"][0]["message"]["content"].strip()
            # Retire les balises markdown si Mistral les ajoute quand même
            texte = re.sub(r"^```(?:json)?\s*", "", texte)
            texte = re.sub(r"\s*```$", "", texte)
            match = re.search(r"\{.*\}", texte, re.DOTALL)
            print(f"[Mistral JSON] Réponse : {texte}")
            if match:
                return json.loads(match.group())
            return {}
        except requests.exceptions.HTTPError as e:
            if r.status_code == 429:
                attente = 15 * (tentative + 1)
                print(f"[Mistral JSON] Rate limit, attente {attente}s... ({tentative+1}/3)")
                time.sleep(attente)
            else:
                print(f"[Mistral JSON] Erreur {r.status_code} : {r.text}")
                raise e
    return {}


# ─────────────────────────────────────────────────────────────────────────────
# Fonction principale
# ─────────────────────────────────────────────────────────────────────────────
def analyser_fiche(file_bytes):
    b64 = _compresser_image(file_bytes)
    del file_bytes

    # Étape 1 — OCR brut
    texte_ocr = _appel_mistral_ocr(b64)
    del b64
    if not texte_ocr:
        return {"erreur": "OCR échoué", "pieces": [], "nb_pieces_total": 0}

    # Chargement référentiels (une seule fois)
    pieces_connues     = _charger_pieces_connues()
    labels_machines    = _charger_machines_connues()
    techniciens_connus = _charger_techniciens_connus()

    # Injection des refs connues dans le prompt pour aider Mistral
    refs_connues = "\n".join(
        f"- {ref} : {designation}"
        for ref, designation in pieces_connues.items()
    )

    # Étape 2 — Extraction JSON structurée (avec contexte refs)
    data = _appel_mistral_json(texte_ocr, refs_connues)
    if not data:
        return {"erreur": "Extraction JSON échouée", "pieces": [], "nb_pieces_total": 0}

    nom     = data.get("nom",     "").strip()
    date    = data.get("date",    "").strip()
    numero  = data.get("numero",  "").strip()
    machine = data.get("machine", "").strip().upper()

    print(f"[OCR] NOM     : \'{nom}\'")
    print(f"[OCR] DATE    : \'{date}\'")
    print(f"[OCR] NUMERO  : \'{numero}\'")
    print(f"[OCR] MACHINE : \'{machine}\'")

    # Normalisation date JJ/MM/AA → JJ/MM/AAAA
    date_clean = re.sub(r"[^\d/]", "", date).strip("/")
    parties    = date_clean.split("/")
    if len(parties) == 3:
        j, m, a = parties
        if len(a) == 2:
            a = "20" + a
        date_clean = f"{j}/{m}/{a}"

    # Fuzzy matching machine
    machine_corrigee, is_new_machine = _fuzzy_machine(machine, labels_machines)

    # Résolution technicien (fuzzy + fallback JWT)
    technicien = _resoudre_technicien(nom, techniciens_connus)

    # Construction liste pièces
    pieces = []
    for p in data.get("pieces", []):
        ref_brute  = re.sub(r"\s+", "", str(p.get("ref", ""))).upper()
        qte                 = int(p.get("quantite", 0))
        designation_mistral = p.get("designation", "").strip().upper()

        if not ref_brute or qte <= 0:
            continue

        ref_corrigee, designation, is_new = _fuzzy_piece(
            ref_brute, pieces_connues, designation_mistral
        )

        pieces.append({
            "ref_piece":   ref_corrigee,
            "designation": designation,
            "quantite":    qte,
            "is_new":      is_new,
        })

    return {
        "technicien":      technicien,
        "date":            date_clean,
        "numero_serie": re.sub(r"\s+", "", numero).upper(),
        "machine_type":    machine_corrigee,
        "is_new_machine":  is_new_machine,
        "pieces":          pieces,
        "nb_pieces_total": sum(p["quantite"] for p in pieces),
    }