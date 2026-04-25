from datetime import datetime, timezone
from app.extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name    = db.Column(db.String(100), nullable=False, default='')
    last_name     = db.Column(db.String(100), nullable=False, default='')
    created_at    = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    reparations   = db.relationship('Reparation', back_populates='technicien_ref',
                                    foreign_keys='Reparation.technicien_id',
                                    lazy='select')
    reset_token   = db.relationship('PasswordResetToken', back_populates='user',
                                    uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'
