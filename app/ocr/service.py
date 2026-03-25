import re
from app.utils.image_utils import load_image_from_bytes, preprocess_for_ocr, crop_zone

_reader = None

def get_reader():
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(['fr', 'en'], gpu=False)
    return _reader

ZONES = {
    "nom":    (0.05, 0.04, 0.30, 0.06),
    "date":   (0.70, 0.04, 0.25, 0.06),
    "numero": (0.70, 0.08, 0.25, 0.06),
}

PIECES_CONNUES = {
    "40100": "BAC A GRAINS COMPLET",
    "40101": "COUVERCLE BAC A GRAIN",
    "40701": "COUVERCLE DISTRIBUTEUR",
    "40702": "BANDE PLEXI INTERIEUR",
    "40725": "COMPTEUR TOTALISEUR 5 CHIFFRES",
    "40726": "RESSORT RAPPEL COMPTEUR",
    "40745": "BUTEE DIAM 12H 7,5",
    "40746": "BUTEE DIAM 12H4",
    "00001B": "PAIRE DE MEULES",
    "40662B": "RECUPERATEUR DE CAFE",
    "40759A": "COUVERCLE CARTER AUTO",
    "40797A": "CARTER AUTOMATIQUE",
    "40783": "CROISILLON INTERMEDIAIRE",
    "40782": "RACLETTE DE CROISILLONS",
    "40791": "RONDELLE ONDULEE DOSEUR",
    "40781": "CROISILLON SUPERIEUR",
    "40790": "BRISE MOTTE",
    "40753A": "LANGUETTE CAOUTCHOUC",
    "40754A": "PLAQUETTE DE RETENUE LANGUETTE",
    "40609": "CONDENSATEUR 100MF",
    "55841C": "TASSEUR DIAM 57MM",
    "40625": "CORDON D ALIMENTATION AVEC PRISE EUR",
    "40206": "VIS DE FIXATION MEULE (M4 X10)",
}

def _ocr_zone(img, zone_key):
    zone      = crop_zone(img, *ZONES[zone_key])
    processed = preprocess_for_ocr(zone)
    results   = get_reader().readtext(processed, detail=0, paragraph=True)
    return ' '.join(results).strip() if results else ''

def _extraire_quantites(img):
    pieces_detectees = []
    col_x, col_w     = 0.155, 0.07
    nb_lignes        = len(PIECES_CONNUES)
    zone_debut_y     = 0.22
    zone_fin_y       = 0.90
    hauteur_ligne    = (zone_fin_y - zone_debut_y) / nb_lignes
    refs             = list(PIECES_CONNUES.keys())

    for i, ref in enumerate(refs):
        y        = zone_debut_y + i * hauteur_ligne
        cell     = crop_zone(img, col_x, y, col_w, hauteur_ligne * 0.85)
        processed = preprocess_for_ocr(cell)
        results  = get_reader().readtext(processed, detail=0, allowlist='0123456789')
        texte    = ''.join(results).strip()
        if texte and texte.isdigit() and int(texte) > 0:
            pieces_detectees.append({
                "ref_piece":   ref,
                "designation": PIECES_CONNUES[ref],
                "quantite":    int(texte)
            })

    return pieces_detectees

def analyser_fiche(file_bytes):
    img    = load_image_from_bytes(file_bytes)
    nom    = _ocr_zone(img, 'nom')
    date   = _ocr_zone(img, 'date')
    numero = _ocr_zone(img, 'numero')
    date_clean = re.sub(r'[^\d/\-\.]', '', date)
    date_clean = re.sub(r'[\-\.]', '/', date_clean)
    pieces = _extraire_quantites(img)
    return {
        "technicien":      nom,
        "date":            date_clean,
        "numero_serie":    numero.upper().replace(' ', '-'),
        "machine_type":    "MOULIN SANTOS 40AN",
        "pieces":          pieces,
        "nb_pieces_total": sum(p['quantite'] for p in pieces)
    }