# app/utils/strings.py
import re


def normaliser_ref(ref: str) -> str:
    """Supprime les espaces et met en majuscules."""
    return re.sub(r"\s+", "", str(ref)).upper()