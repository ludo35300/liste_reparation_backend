from app.utils.fuzzy import fuzzy_piece, fuzzy_machine


# ── fuzzy_piece ───────────────────────────────────────────────

def test_fuzzy_piece_exact():
    pieces = {"REF-001": "Courroie", "REF-002": "Moteur"}
    ref, desig, is_new = fuzzy_piece("REF-001", pieces, cutoff=0.75)
    assert ref == "REF-001"
    assert desig == "Courroie"
    assert is_new is False          # trouvé → pas nouveau

def test_fuzzy_piece_proche():
    pieces = {"REF-001": "Courroie", "REF-002": "Moteur"}
    ref, desig, is_new = fuzzy_piece("REF001", pieces, cutoff=0.75)
    assert ref == "REF-001"
    assert is_new is False          # assez proche → pas nouveau

def test_fuzzy_piece_inconnu():
    pieces = {"REF-001": "Courroie"}
    ref, desig, is_new = fuzzy_piece("ZZZZZ", pieces, cutoff=0.75)
    assert ref == "ZZZZZ"
    assert desig == ""
    assert is_new is True           # non trouvé → nouveau

def test_fuzzy_piece_dict_vide():
    ref, desig, is_new = fuzzy_piece("REF-001", {}, cutoff=0.75)
    assert ref == "REF-001"
    assert is_new is True           # dict vide → nouveau

def test_fuzzy_piece_ref_vide():
    ref, desig, is_new = fuzzy_piece("", {"REF-001": "Courroie"}, cutoff=0.75)
    assert ref == ""                # ref vide retournée telle quelle


# ── fuzzy_machine ─────────────────────────────────────────────

def test_fuzzy_machine_exact():
    labels = ["MOULIN SANTOS 40AN", "EXPRESSO JURA X8"]
    label, is_new = fuzzy_machine("MOULIN SANTOS 40AN", labels)
    assert label == "MOULIN SANTOS 40AN"
    assert is_new is False          # trouvé → pas nouveau

def test_fuzzy_machine_approche():
    labels = ["MOULIN SANTOS 40AN", "EXPRESSO JURA X8"]
    label, is_new = fuzzy_machine("SANTOS 40A", labels)
    assert "SANTOS" in label
    assert is_new is False          # assez proche → pas nouveau

def test_fuzzy_machine_inconnu():
    labels = ["MOULIN SANTOS 40AN"]
    label, is_new = fuzzy_machine("MACHINE INCONNUE XYZ", labels)
    assert label == "MACHINE INCONNUE XYZ"
    assert is_new is True           # non trouvé → nouveau

def test_fuzzy_machine_liste_vide():
    label, is_new = fuzzy_machine("SANTOS 40AN", [])
    assert label == "SANTOS 40AN"
    assert is_new is True           # liste vide → nouveau

def test_fuzzy_machine_brute_vide():
    label, is_new = fuzzy_machine("", ["MOULIN SANTOS 40AN"])
    assert label == ""
    assert is_new is True           # entrée vide → inconnu