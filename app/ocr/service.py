import re
import os
import json
import base64
import time
import io
import requests
from PIL import Image
from app.utils.image_utils import load_image_from_bytes

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

PIECES_CONNUES = {
    "40100":  "BAC A GRAINS COMPLET",
    "40101":  "COUVERCLE BAC A GRAIN",
    "40701":  "COUVERCLE DISTRIBUTEUR",
    "40702":  "BANDE PLEXI INTERIEUR",
    "40725":  "COMPTEUR TOTALISEUR 5 CHIFFRES",
    "40726":  "RESSORT RAPPEL COMPTEUR",
    "40745":  "BUTEE DIAM 12H 7,5",
    "40746":  "BUTEE DIAM 12H4",
    "00001B": "PAIRE DE MEULES",
    "40662B": "RECUPERATEUR DE CAFE",
    "40759A": "COUVERCLE CARTER AUTO",
    "40797A": "CARTER AUTOMATIQUE",
    "40783":  "CROISILLON INTERMEDIAIRE",
    "40782":  "RACLETTE DE CROISILLONS",
    "40791":  "RONDELLE ONDULEE DOSEUR",
    "40781":  "CROISILLON SUPERIEUR",
    "40790":  "BRISE MOTTE",
    "40753A": "LANGUETTE CAOUTCHOUC",
    "40754A": "PLAQUETTE DE RETENUE LANGUETTE",
    "40609":  "CONDENSATEUR 100MF",
    "55841C": "TASSEUR DIAM 57MM",
    "40625":  "CORDON D ALIMENTATION AVEC PRISE EUR",
    "40206":  "VIS DE FIXATION MEULE (M4 X10)",
}

PROMPT_JSON = """Voici le texte extrait d'une fiche de réparation de moulin à café :

{texte_ocr}

Extrais les informations et réponds UNIQUEMENT en JSON strict sans texte autour :
{{
  "nom": "...",
  "date": "JJ/MM/AA",
  "numero": "...",
  "machine": "...",
  "pieces": [
    {{"ref": "...", "designation": "...", "quantite": 1}}
  ]
}}

Règles :
- "nom" : valeur manuscrite après "NOM:"
- "date" : date manuscrite après "DATE:", format JJ/MM/AA (année sur 2 chiffres)
- "numero" : chiffres manuscrits après "NUMERO:"
- "machine" : texte imprimé centré (ex: MOULIN SANTOS 40AN)
- "pieces" : UNIQUEMENT les lignes du tableau où QUANTITE contient un chiffre (① = 1, ② = 2, ③ = 3) ou un nombre manuscrit (1, 2, 3, etc).
- Ignore toutes les lignes avec QUANTITE vide"""


def _compresser_image(file_bytes, max_width=1000, qualite=72):
    Image.MAX_IMAGE_PIXELS = None
    
    # Ouvre sans décoder les pixels
    image = Image.open(io.BytesIO(file_bytes))
    
    # Réduit dès la lecture — évite de charger 200MP en RAM
    image.draft("RGB", (max_width, max_width * 2))
    image = image.convert("RGB")
    
    w, h = image.size
    print(f"[OCR] Taille après draft : {w}x{h} px")
    
    # Redimensionnement final précis
    if w > max_width:
        image = image.resize((max_width, int(h * max_width / w)), Image.LANCZOS)
    
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=qualite, optimize=True)
    b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    print(f"[OCR] Image compressée : {len(b64) // 1024} Ko")
    del image, buffer
    return b64

def _appel_mistral_ocr(b64):
    """Appel à l'API OCR Mistral Document AI."""
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type":  "application/json"
    }
    payload = {
        "model":    "mistral-ocr-latest",
        "document": {
            "type":      "image_url",
            "image_url": f"data:image/jpeg;base64,{b64}"
        }
    }
    for tentative in range(3):
        try:
            r = requests.post(
                "https://api.mistral.ai/v1/ocr",
                headers=headers,
                json=payload,
                timeout=30
            )
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


def _appel_mistral_json(texte_ocr):
    """Envoie le texte OCR à Mistral chat pour extraction JSON structurée."""
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type":  "application/json"
    }
    payload = {
        "model":    "mistral-small-latest",
        "messages": [{
            "role":    "user",
            "content": PROMPT_JSON.format(texte_ocr=texte_ocr)
        }]
    }
    for tentative in range(3):
        try:
            r = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            r.raise_for_status()
            texte = r.json()["choices"][0]["message"]["content"].strip()
            print(f"[Mistral JSON] Réponse : {texte}")
            match = re.search(r'\{.*\}', texte, re.DOTALL)
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


def analyser_fiche(file_bytes):
    # Compression légère — libère la RAM rapidement
    b64       = _compresser_image(file_bytes)
    del file_bytes

    # Étape 1 — OCR : lit tout le texte de la fiche
    texte_ocr = _appel_mistral_ocr(b64)
    del b64
    if not texte_ocr:
        return {"erreur": "OCR échoué", "pieces": [], "nb_pieces_total": 0}

    # Étape 2 — Extraction JSON structurée
    data = _appel_mistral_json(texte_ocr)
    if not data:
        return {"erreur": "Extraction JSON échouée", "pieces": [], "nb_pieces_total": 0}

    nom     = data.get("nom",     "").strip()
    date    = data.get("date",    "").strip()
    numero  = data.get("numero",  "").strip()
    machine = data.get("machine", "").strip()

    print(f"[OCR] NOM     : '{nom}'")
    print(f"[OCR] DATE    : '{date}'")
    print(f"[OCR] NUMERO  : '{numero}'")
    print(f"[OCR] MACHINE : '{machine}'")

    # Date JJ/MM/AA → JJ/MM/AAAA
    date_clean = re.sub(r'[^\d/]', '', date).strip('/')
    parties    = date_clean.split('/')
    if len(parties) == 3:
        j, m, a = parties
        if len(a) == 2:
            a = "20" + a
        date_clean = f"{j}/{m}/{a}"

    # Construction liste pièces
    pieces = []
    for p in data.get("pieces", []):
        ref                 = re.sub(r'\s+', '', str(p.get("ref", ""))).upper()
        qte                 = int(p.get("quantite", 0))
        designation_mistral = p.get("designation", "").strip().upper()
        if ref and qte > 0:
            pieces.append({
                "ref_piece":   ref,
                "designation": PIECES_CONNUES.get(ref, designation_mistral),
                "quantite":    qte
            })

    return {
        "technicien":      nom,
        "date":            date_clean,
        "numero_serie":    re.sub(r'\s+', '', numero).upper(),
        "machine_type":    machine.upper().strip(),
        "pieces":          pieces,
        "nb_pieces_total": sum(p['quantite'] for p in pieces)
    }