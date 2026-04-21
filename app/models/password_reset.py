from datetime import datetime
from app.extensions import db


class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer,
                           db.ForeignKey('users.id', ondelete='CASCADE'),
                           nullable=False, unique=True, index=True)
    token_hash = db.Column(db.String(255), nullable=False)   # stocker le hash SHA-256
    expires_at = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', back_populates='reset_token')

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at

    def __repr__(self):
        return f'<PasswordResetToken user_id={self.user_id}>'
