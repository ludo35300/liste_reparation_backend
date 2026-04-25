# Ce fichier est conservé pour rétro-compatibilité.
# Utiliser UserRepository depuis app/repositories/user_repository.py
from app.repositories.user_repository import UserRepository

get_user_by_email     = UserRepository.get_by_email
get_user_by_id        = UserRepository.get_by_id
get_all_users         = UserRepository.get_all
create_user           = UserRepository.create
update_password       = UserRepository.update_password
save_reset_token      = UserRepository.save_reset_token
get_user_by_reset_token = UserRepository.get_by_reset_token
clear_reset_token     = UserRepository.clear_reset_token
