from app.extensions import db
from app.models.user import User
from app.models.password_reset import PasswordResetToken


def _norm_email(email: str) -> str:
    return (email or '').strip().lower()


class UserRepository:

    @staticmethod
    def norm_email(email: str) -> str:
        return _norm_email(email)

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
            email=_norm_email(email),
            password_hash=password_hash,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
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
        """Crée ou met à jour le token de réinitialisation dans password_reset_tokens."""
        if user.reset_token:
            user.reset_token.token_hash = token_hash
            user.reset_token.expires_at = expires
        else:
            db.session.add(PasswordResetToken(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=expires,
            ))
        db.session.commit()

    @staticmethod
    def get_by_reset_token(token_hash: str) -> User | None:
        """Recherche via la table password_reset_tokens, retourne l'User associé."""
        token = PasswordResetToken.query.filter_by(token_hash=token_hash).first()
        return token.user if token else None

    @staticmethod
    def clear_reset_token(user: User) -> None:
        """Supprime le token de réinitialisation."""
        if user.reset_token:
            db.session.delete(user.reset_token)
            db.session.commit()