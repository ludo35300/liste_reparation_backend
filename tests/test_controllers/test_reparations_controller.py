from unittest.mock import patch, MagicMock


def test_get_reparations_401_sans_jwt(client):
    resp = client.get('/api/reparations')
    assert resp.status_code == 401


def test_create_reparation_champs_manquants(client, auth_headers):
    resp = client.post('/api/reparations', json={}, headers=auth_headers)
    assert resp.status_code == 422


def test_create_reparation_date_invalide(client, auth_headers):
    resp = client.post('/api/reparations', json={
        'machine_id': 1,
        'date_reparation': 'pas-une-date',
    }, headers=auth_headers)
    assert resp.status_code == 422


def test_get_by_serie_machine_introuvable(client, auth_headers):
    with patch('app.controllers.reparations_controller.MachineRepository.get_by_serie', return_value=None):
        resp = client.get('/api/machines/serie/INCONNU', headers=auth_headers)
    assert resp.status_code == 404
    assert resp.get_json()['code'] == 'MACHINE_NOT_FOUND'


def test_get_mes_reparations_user_inconnu(client, auth_headers):
    with patch('app.services.reparations_service.UserRepository.get_by_id', return_value=None):
        resp = client.get('/api/reparations/mine', headers=auth_headers)
    assert resp.status_code == 404