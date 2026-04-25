from unittest.mock import patch, MagicMock
from app.auth import service as auth_svc


def test_login_utilisateur_inconnu(app):
    with app.app_context():
        with patch('app.auth.service.UserRepository.get_by_email', return_value=None):
            resp, status = auth_svc.login_user('inconnu@test.fr', 'mdp')
    assert status == 401


def test_login_mauvais_mot_de_passe(app):
    mock_user = MagicMock(password_hash='hash')
    with app.app_context():
        with patch('app.auth.service.UserRepository.get_by_email', return_value=mock_user), \
             patch('app.auth.service.verify_password', return_value=False):
            resp, status = auth_svc.login_user('test@test.fr', 'mauvais')
    assert status == 401


def test_register_email_deja_utilise(app):
    with app.app_context():
        with patch('app.auth.service.UserRepository.get_by_email', return_value=MagicMock()):
            resp, status = auth_svc.register_user('deja@test.fr', 'mdp', 'Luc', 'D')
    assert status == 409


def test_register_champs_manquants(app):
    with app.app_context():
        with patch('app.auth.service.UserRepository.get_by_email', return_value=None):
            resp, status = auth_svc.register_user('', '', '', '')
    assert status == 400


def test_reset_password_token_invalide(app):
    with app.app_context():
        with patch('app.auth.service.UserRepository.get_by_reset_token', return_value=None):
            resp, status = auth_svc.reset_password('token_faux', 'nouveau_mdp')
    assert status == 400


def test_reset_password_champs_manquants(app):
    with app.app_context():
        resp, status = auth_svc.reset_password('', '')
    assert status == 400