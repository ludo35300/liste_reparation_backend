from unittest.mock import patch, MagicMock, call
from datetime import date
import pytest
from app.services import reparations_service as svc


def _mock_save(obj):
    obj.id = 1
    return obj


def test_creer_reparation_ok():
    # Mock de la machine retournée par MachineRepository.get_by_id
    mock_machine = MagicMock()
    mock_machine.modele = None  # pas de modèle → marque_id = None

    with patch('app.services.reparations_service.ReparationRepository.add'), \
         patch('app.services.reparations_service.ReparationRepository.flush'), \
         patch('app.services.reparations_service.ReparationRepository.commit'), \
         patch('app.services.reparations_service.ReparationRepository.get_by_machine', return_value=[]), \
         patch('app.services.reparations_service.PieceRefRepository.get_all_as_dict', return_value={}), \
         patch('app.services.reparations_service.ReparationRepository.add_piece_changee'), \
         patch('app.services.reparations_service.MachineRepository.get_by_id', return_value=mock_machine), \
         patch('app.services.reparations_service.MachineRepository.save'):
        rep = svc.creer_reparation({
            'machine_id': 1,
            'date_reparation': '2026-04-25',
            'technicien_id': 5,
            'technicien': 'Ludovic',
            'pieces': [],
        })
    assert rep.machine_id == 1
    assert rep.date_reparation == date(2026, 4, 25)

def test_creer_reparation_date_invalide():
    with pytest.raises(ValueError, match="Format de date invalide"):
        svc.creer_reparation({'machine_id': 1, 'date_reparation': '25/04/2026'})


def test_creer_reparation_date_manquante():
    with pytest.raises(ValueError, match="requis"):
        svc.creer_reparation({'machine_id': 1, 'date_reparation': ''})


def test_get_reparations_by_serie_machine_introuvable():
    with patch('app.services.reparations_service.MachineRepository.get_by_serie', return_value=None):
        result = svc.get_reparations_by_numero_serie('INCONNU')
    assert result is None


def test_get_mes_reparations_user_inconnu():
    with patch('app.services.reparations_service.UserRepository.get_by_id', return_value=None):
        result = svc.get_mes_reparations(999)
    assert result is None


def test_get_mes_reparations_ok():
    mock_user = MagicMock(id=5)
    mock_reps = [MagicMock(id=1), MagicMock(id=2)]
    with patch('app.services.reparations_service.UserRepository.get_by_id', return_value=mock_user), \
         patch('app.services.reparations_service.ReparationRepository.get_by_technicien_id', return_value=mock_reps):
        result = svc.get_mes_reparations(5)
    assert len(result) == 2