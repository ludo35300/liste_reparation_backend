from app.models.machine import Machine
from unittest.mock import patch, MagicMock


def _mock_machine():
    m = MagicMock(spec=Machine)
    m.id = 1
    m.numero_serie = 'SN-001'
    m.statut = 'en_attente'
    m.modele_id = None
    m.modele = None
    m.date_entree = None
    m.notes = ''
    m.created_at = None
    return m


def test_get_machines_401_sans_jwt(client):
    resp = client.get('/api/machines')
    assert resp.status_code == 401


def test_create_machine_missing_serie(client, auth_headers):
    resp = client.post('/api/machines', json={}, headers=auth_headers)
    assert resp.status_code == 422


def test_create_machine_duplicate(client, auth_headers):
    with patch('app.services.machines_service.MachineRepository.exists_by_serie', return_value=True):
        resp = client.post('/api/machines', json={'numero_serie': 'SN-001'}, headers=auth_headers)
    assert resp.status_code == 409


def test_create_machine_ok(client, auth_headers):
    mock_m = _mock_machine()
    with patch('app.services.machines_service.MachineRepository.exists_by_serie', return_value=False), \
         patch('app.services.machines_service.MachineRepository.save', return_value=mock_m):
        resp = client.post('/api/machines', json={'numero_serie': 'SN-001'}, headers=auth_headers)
    assert resp.status_code == 201