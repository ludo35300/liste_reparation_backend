from unittest.mock import patch, MagicMock
from app.services import user_service as svc


def test_get_current_user_found():
    mock_user = MagicMock(id=1, email='a@b.fr')
    with patch('app.services.user_service.UserRepository.get_by_id', return_value=mock_user):
        result = svc.get_current_user(1)
    assert result.id == 1
    assert result.email == 'a@b.fr'


def test_get_current_user_not_found():
    with patch('app.services.user_service.UserRepository.get_by_id', return_value=None):
        result = svc.get_current_user(999)
    assert result is None


def test_get_all_techniciens_returns_list():
    mock_users = [MagicMock(id=1), MagicMock(id=2)]
    with patch('app.services.user_service.UserRepository.get_all', return_value=mock_users):
        result = svc.get_all_techniciens()
    assert len(result) == 2