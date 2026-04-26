from app.utils.dates import normaliser_date_ocr


def test_format_jj_mm_aa():
    assert normaliser_date_ocr("25/04/26") == "25/04/2026"

def test_format_jj_mm_aaaa():
    assert normaliser_date_ocr("25/04/2026") == "25/04/2026"

def test_format_avec_tirets():
    assert normaliser_date_ocr("25-04-2026") == "25/04/2026"

def test_format_avec_points():
    assert normaliser_date_ocr("25.04.2026") == "25/04/2026"

def test_chaine_vide():
    assert normaliser_date_ocr("") == ""

def test_valeur_none():
    assert normaliser_date_ocr(None) == ""

def test_date_illisible():
    assert normaliser_date_ocr("??/??/??") == ""

def test_date_iso_deja_correcte():
    assert normaliser_date_ocr("2026-04-25") == ""

def test_mois_invalide():
    assert normaliser_date_ocr("25/13/2026") == ""

def test_jour_invalide():
    assert normaliser_date_ocr("32/04/2026") == ""