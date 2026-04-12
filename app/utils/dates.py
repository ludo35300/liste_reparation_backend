# app/utils/dates.py  (extrait — remplace l'ancienne fonction)
import re
from datetime import date


# Confusions OCR fréquentes chiffre → liste des chiffres possibles lus à la place
# Exemples réels : "7" lu à la place de "2", "0" lu à la place de "6", etc.
_OCR_CONFUSIONS = {
    "0": ["0", "8", "6"],
    "1": ["1", "7"],
    "2": ["2", "7"],
    "3": ["3", "8"],
    "4": ["4", "9"],
    "5": ["5", "6"],
    "6": ["6", "0", "5"],
    "7": ["7", "1", "2"],
    "8": ["8", "0", "3"],
    "9": ["9", "4"],
}


def normaliser_date_ocr(date_brute: str) -> str:
    """
    Normalise une date OCR vers le format JJ/MM/AAAA.

    Problèmes couverts :
    - JJ/MM/AA  → JJ/MM/20AA  (cas nominal)
    - JJ/MM/AAAA déjà complet → vérifié et retourné tel quel
    - Année aberrante OCR (ex: 2076 au lieu de 2026) → corrigée par
      substitution des confusions OCR connues (2↔7, 6↔0, etc.)
    - Jour ou mois hors plage valide → retourne ''
    - Date dans le futur > 1 an ou avant 2000 → retourne ''
    - Date calendaire impossible (30/02) → retourne ''
    - Séparateurs variés (tiret, point, espace) → normalisés en /
    """
    print(f"[DEBUG DATE] brut reçu : repr={repr(date_brute)}")
    
    if not date_brute:
        return ""

    # Normalise les séparateurs alternatifs en "/"
    date_clean = re.sub(r"[\-\.\s]", "/", date_brute)
    # Supprime tout caractère non numérique et non "/"
    date_clean = re.sub(r"[^\d/]", "", date_clean).strip("/")

    parties = date_clean.split("/")
    if len(parties) != 3:
        return ""

    j_str, m_str, a_str = parties

    # ── Validation jour et mois ───────────────────────────────────────────────
    try:
        j = int(j_str)
        m = int(m_str)
    except ValueError:
        return ""

    if not (1 <= j <= 31) or not (1 <= m <= 12):
        return ""

    # ── Normalisation de l'année ──────────────────────────────────────────────
    annee_courante = date.today().year  # ex: 2026

    try:
        a = int(a_str)
    except ValueError:
        return ""

    if len(a_str) == 2:
        a_candidate = 2000 + a  # tentative directe

        # Si le résultat est incohérent (> année courante + 1 ou < 2000)
        # → on tente une correction OCR chiffre par chiffre
        if a_candidate > annee_courante + 1:
            candidats = _generer_candidats_annee_courte(a_str, annee_courante)
            if candidats:
                a = candidats[0]
            else:
                return ""  # Aucune correction plausible
        else:
            a = a_candidate

    elif len(a_str) == 4:
        ecart = abs(a - annee_courante)

        if ecart > 5:
            # Année suspecte : on tente de corriger via les confusions OCR connues
            # Ex: "2076" → le "7" a été lu à la place du "2" → candidat "2026"
            candidats = _generer_candidats_annee(a_str, annee_courante)
            if candidats:
                a = candidats[0]  # Prend l'année la plus proche de l'année courante
            else:
                return ""  # Aucune correction plausible trouvée

    else:
        # Longueur inattendue (1 ou 3 chiffres)
        return ""

    # ── Vérification de cohérence temporelle ─────────────────────────────────
    # Une fiche de réparation ne peut pas être datée dans plus d'1 an dans le futur
    # ni avant l'an 2000
    if a < 2000 or a > annee_courante + 1:
        return ""

    
    # ── Validation calendaire complète ───────────────────────────────────────
    # Vérifie que la combinaison jour/mois/an est réellement valide (ex: 30/02 → non)
    try:
        date(a, m, j)
    except ValueError:
        return ""

    return f"{j:02d}/{m:02d}/{a}"


def _generer_candidats_annee(annee_str: str, annee_ref: int) -> list[int]:
    """
    Génère les années à 4 chiffres les plus probables à partir d'une lecture OCR
    erronée, en substituant chaque chiffre par ses confusions OCR connues.

    Ex : "2076" → position 2 : "7" peut être "2" → candidat "2026" ✓
         "2076" → position 2 : "7" peut être "1" → candidat "2016" (moins proche)

    Retourne les candidats triés par proximité à annee_ref,
    filtrés entre 2000 et annee_ref + 1.
    """
    candidats = set()
    chiffres = list(annee_str)

    for i, c in enumerate(chiffres):
        # Liste des chiffres que l'OCR a pu lire à la place du chiffre réel
        alternatives = set(_OCR_CONFUSIONS.get(c, [c]))
        for alt in alternatives:
            if alt.isdigit():
                variante = chiffres[:i] + [alt] + chiffres[i + 1:]
                try:
                    a = int("".join(variante))
                    if 2000 <= a <= annee_ref + 1:
                        candidats.add(a)
                except ValueError:
                    continue

    # Trie par proximité à l'année de référence (la correction la plus probable en premier)
    return sorted(candidats, key=lambda x: abs(x - annee_ref))

def _generer_candidats_annee_courte(aa_str: str, annee_ref: int) -> list[int]:
    """
    Corrige une année à 2 chiffres aberrante via les confusions OCR.
    Ex: "76" → "7" peut être "2" → "26" → 2026 ✓
    """
    candidats = set()
    chiffres = list(aa_str)

    for i, c in enumerate(chiffres):
        for alt in _OCR_CONFUSIONS.get(c, [c]):
            if alt.isdigit():
                variante = chiffres[:i] + [alt] + chiffres[i + 1:]
                try:
                    a = 2000 + int("".join(variante))
                    if 2000 <= a <= annee_ref + 1:
                        candidats.add(a)
                except ValueError:
                    continue

    return sorted(candidats, key=lambda x: abs(x - annee_ref))