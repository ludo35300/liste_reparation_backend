from app.extensions import db
from app.models.user import User


def _norm_email(email: str) -> str:
    return (email or '').strip().lower()


class UserRepository:
    @staticmethod
    def norm_email(email: str) -> str:
        return (email or '').strip().lower()

    @staticmethod
    def get_by_id(user_id: int) -> User | None:
        return db.session.get(User, user_id)

    @staticmethod
    def get_by_email(email: str) -> User | None:
        return User.query.filter_by(email=_norm_email(email)).first()

    @staticmethod
    def get_all() -> list[User]:
        return User.query.order_by(User.first_name.asc(), User.last_name.asc()).all()

    @staticmethod
    def create(email: str, password_hash: str,
               first_name: str, last_name: str) -> User:
        user = User(
            email         = _norm_email(email),
            password_hash = password_hash,
            first_name    = first_name.strip(),
            last_name     = last_name.strip(),
        )
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update_password(user: User, new_hash: str) -> None:
        user.password_hash = new_hash
        db.session.commit()

    # ── Reset token ───────────────────────────────────────────
    @staticmethod
    def save_reset_token(user: User, token_hash: str, expires) -> None:
        user.reset_token         = token_hash
        user.reset_token_expires = expires
        db.session.commit()

    @staticmethod
    def get_by_reset_token(token_hash: str) -> User | None:
        return User.query.filter_by(reset_token=token_hash).first()

    @staticmethod
    def clear_reset_token(user: User) -> None:
        user.reset_token         = None
        user.reset_token_expires = None
        db.session.commit()
