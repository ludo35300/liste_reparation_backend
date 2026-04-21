from datetime import datetime
from app.extensions import db


class Reparation(db.Model):
    __tablename__ = 'reparations'

    id              = db.Column(db.Integer, primary_key=True)
    machine_id      = db.Column(db.Integer,
                                db.ForeignKey('machines.id', ondelete='CASCADE'),
                                nullable=False, index=True)
    technicien_id   = db.Column(db.Integer,
                                db.ForeignKey('users.id', ondelete='SET NULL'),
                                nullable=True, index=True)
    technicien      = db.Column(db.String(100), default='')   # snapshot nom technicien
    date_reparation = db.Column(db.Date, nullable=False)
    description     = db.Column(db.Text, default='')
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    machine        = db.relationship('Machine', back_populates='reparations')
    technicien_ref = db.relationship('User',    back_populates='reparations',
                                     foreign_keys=[technicien_id])
    pieces         = db.relationship('PieceChangee', back_populates='reparation',
                                     cascade='all, delete-orphan', lazy='select')

    def __repr__(self):
        return f'<Reparation machine={self.machine_id} {self.date_reparation}>'
