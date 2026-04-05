# app/utils/dates.py
import re


def normaliser_date_ocr(date_brute: str) -> str:
    """Convertit JJ/MM/AA → JJ/MM/AAAA. Retourne '' si invalide."""
    if not date_brute:
        return ""
    date_clean = re.sub(r"[^\d/]", "", date_brute).strip("/")
    parties = date_clean.split("/")
    if len(parties) != 3:
        return date_brute
    j, m, a = parties
    if len(a) == 2:
        a = "20" + a
    return f"{j}/{m}/{a}"