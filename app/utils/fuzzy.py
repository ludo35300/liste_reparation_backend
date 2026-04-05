# app/utils/fuzzy.py
from difflib import get_close_matches


def fuzzy_match(valeur: str, candidats: list, cutoff: float = 0.6) -> str | None:
    """Retourne la meilleure correspondance ou None."""
    if not valeur or not candidats:
        return None
    matches = get_close_matches(valeur.upper(), [c.upper() for c in candidats], n=1, cutoff=cutoff)
    return matches[0] if matches else None


def fuzzy_machine(machine_brute: str, labels: list) -> tuple[str, bool]:
    """Retourne (label_corrigé, is_new)."""
    if not machine_brute:
        return "", True
    match = fuzzy_match(machine_brute, labels, cutoff=0.6)
    if match:
        return match, False
    return machine_brute.upper(), True


def fuzzy_piece(ref_brute: str, pieces_connues: dict, cutoff: float = 0.75) -> tuple[str, str, bool]:
    """Retourne (ref_corrigée, designation, is_new)."""
    ref = ref_brute.upper()
    if ref in pieces_connues:
        return ref, pieces_connues[ref], False
    match = fuzzy_match(ref, list(pieces_connues.keys()), cutoff=cutoff)
    if match:
        return match, pieces_connues[match], False
    return ref, "", True