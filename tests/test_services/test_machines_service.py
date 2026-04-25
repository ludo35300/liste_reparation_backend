from unittest.mock import patch, MagicMock
import pytest
from app.services import machines_service as svc


def test_create_machine_ok():
    with patch('app.services.machines_service.MachineRepository.exists_by_serie', return_value=False), \
         patch('app.services.machines_service.MachineRepository.save') as mock_save:
        mock_save.side_effect = lambda m: m
        machine = svc.create_machine({'numero_serie': 'SN-001', 'statut': 'en_attente'})
    assert machine.numero_serie == 'SN-001'


def test_create_machine_duplicate_raises():
    with patch('app.services.machines_service.MachineRepository.exists_by_serie', return_value=True):
        with pytest.raises(ValueError, match="déjà enregistré"):
            svc.create_machine({'numero_serie': 'SN-001'})


def test_get_machine_by_serie_not_found():
    with patch('app.services.machines_service.MachineRepository.get_by_serie', return_value=None):
        result = svc.get_machine_by_serie('INCONNU')
    assert result is None


def test_update_machine_applies_fields():
    mock_machine = MagicMock(statut='en_attente', notes='')
    with patch('app.services.machines_service.MachineRepository.get_by_id', return_value=mock_machine), \
         patch('app.services.machines_service.MachineRepository.save', side_effect=lambda m: m):
        result = svc.update_machine(1, {'statut': 'pret', 'notes': 'RAS'})
    assert result.statut == 'pret'
    assert result.notes == 'RAS'