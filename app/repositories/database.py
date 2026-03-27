from app.extensions import db
from app.models.user import User


def norm_email(email: str) -> str:
    return (email or '').strip().lower()


def get_user_by_email(email: str) -> User | None:
    return User.query.filter_by(email=norm_email(email)).first()


def get_user_by_id(user_id: int) -> User | None:
    return db.session.get(User, user_id)


def create_user(email: str, password_hash: str,
                first_name: str, last_name: str) -> User:
    user = User(
        email         = norm_email(email),
        password_hash = password_hash,
        first_name    = first_name.strip(),
        last_name     = last_name.strip()
    )
    db.session.add(user)
    db.session.commit()
    return user


def update_password(user: User, new_hash: str):
    user.password_hash = new_hash
    db.session.commit()


def save_reset_token(user: User, token_hash: str, expires):
    user.reset_token         = token_hash
    user.reset_token_expires = expires
    db.session.commit()


def get_user_by_reset_token(token_hash: str) -> User | None:
    return User.query.filter_by(reset_token=token_hash).first()


def clear_reset_token(user: User):
    user.reset_token         = None
    user.reset_token_expires = None
    db.session.commit()