from app.repositories.user_repository import UserRepository

def get_current_user(user_id: int):
    return UserRepository.get_by_id(int(user_id))

def get_all_techniciens():
    return UserRepository.get_all()