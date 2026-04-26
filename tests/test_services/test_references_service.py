from unittest.mock import patch, MagicMock
import pytest
from app.services import references_service as svc


# ── Marques ───────────────────────────────────────────────────

def test_create_marque_ok():
    mock_marque = MagicMock(id=1, nom='SANTOS')
    with patch('app.services.references_service.MarqueRepository.get_by_nom', return_value=None), \
         patch('app.services.references_service.MarqueRepository.save', return_value=mock_marque):
        result = svc.create_marque('SANTOS', None)
    assert result.nom == 'SANTOS'

#def test_create_marque_doublon():
    #with patch('app.services.references_service.MarqueRepository.get_by_nom', return_value=MagicMock()):
        #with pytest.raises(ValueError, match="existe déjà"):
            #svc.create_marque('SANTOS', None)

def test_get_all_marques():
    mock_list = [MagicMock(id=1), MagicMock(id=2)]
    with patch('app.services.references_service.MarqueRepository.get_all', return_value=mock_list):
        result = svc.get_all_marques()
    assert len(result) == 2


# ── Modeles ───────────────────────────────────────────────────

def test_create_modele_ok():
    mock_modele = MagicMock(id=1, nom='40AN')
    with patch('app.services.references_service.ModeleRepository.save', return_value=mock_modele):
        result = svc.create_modele('40AN', 'Moulin', 1)
    assert result.nom == '40AN'

def test_get_all_modeles():
    mock_list = [MagicMock(id=1)]
    with patch('app.services.references_service.ModeleRepository.get_all', return_value=mock_list):
        result = svc.get_all_modeles()
    assert len(result) == 1

def test_suggest_modeles():
    mock_list = [MagicMock(id=1, label='MOULIN SANTOS 40AN')]
    with patch('app.services.references_service.ModeleRepository.search', return_value=mock_list):
        result = svc.suggest_modeles('SANTOS')
    assert len(result) == 1


# ── Pièces ────────────────────────────────────────────────────

def test_create_piece_ok():
    mock_piece = MagicMock(id=1, ref_piece='REF-001')
    with patch('app.services.references_service.PieceRefRepository.get_by_ref', return_value=None), \
         patch('app.services.references_service.PieceRefRepository.save', return_value=mock_piece):
        result = svc.create_piece('REF-001', 'Courroie', 1)
    assert result.ref_piece == 'REF-001'

#def test_create_piece_doublon():
    #with patch('app.services.references_service.PieceRefRepository.get_by_ref', return_value=MagicMock()):
        #with pytest.raises(ValueError, match="existe déjà"):
            #svc.create_piece('REF-001', 'Courroie', 1)

def test_suggest_piece_refs():
    mock_list = [MagicMock(ref_piece='REF-001', designation='Courroie')]
    with patch('app.services.references_service.PieceRefRepository.search', return_value=mock_list):
        result = svc.suggest_piece_refs('REF')
    assert len(result) == 1
