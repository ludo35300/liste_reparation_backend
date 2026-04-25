import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db as _db


@pytest.fixture(scope='session')
def app():
    """App Flask configurée pour les tests — SQLite en mémoire."""
    _app = create_app(TestConfig)
    with _app.app_context():
        _db.create_all()
        yield _app
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    """Chaque test démarre avec une session propre."""
    with app.app_context():
        yield _db
        _db.session.rollback()


@pytest.fixture()
def auth_headers(client):
    """Crée un user de test et retourne les headers JWT."""
    from app.repositories.user_repository import UserRepository
    from app.security.passwords import hash_password
    from flask_jwt_extended import create_access_token

    with client.application.app_context():
        user = UserRepository.get_by_email('test@test.fr')
        if not user:
            user = UserRepository.create(
                email='test@test.fr',
                password_hash=hash_password('motdepasse'),
                first_name='Test',
                last_name='User',
           )
        token = create_access_token(identity=str(user.id))
    return {'Authorization': f'Bearer {token}'}