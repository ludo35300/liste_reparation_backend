# app/repositories/user_queries.py
from app.models.user import User

def get_all_users() -> list[User]:
    return User.query.order_by(User.first_name.asc(), User.last_name.asc()).all()