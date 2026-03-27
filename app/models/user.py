from app.extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id                  = db.Column(db.Integer, primary_key=True)
    email               = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash       = db.Column(db.String(255), nullable=False)
    first_name          = db.Column(db.String(100), nullable=False, default='')
    last_name           = db.Column(db.String(100), nullable=False, default='')
    reset_token         = db.Column(db.String(255), nullable=True)
    reset_token_expires = db.Column(db.DateTime,    nullable=True)
    created_at          = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.email}>'