from datetime import datetime
from app.extensions import db


class Reparation(db.Model):
    __tablename__ = 'reparations'

    id              = db.Column(db.Integer, primary_key=True)
    numero_serie    = db.Column(db.String(100), nullable=False, index=True)
    machine_type    = db.Column(db.String(200), nullable=False)  # snapshot texte
    technicien      = db.Column(db.String(100), default='')      # snapshot texte
    machine_type_id = db.Column(db.Integer,
                                db.ForeignKey('machine_type_refs.id', ondelete='SET NULL'),
                                nullable=True, index=True)
    technicien_id   = db.Column(db.Integer,
                                db.ForeignKey('users.id', ondelete='SET NULL'),
                                nullable=True, index=True)
    date_reparation = db.Column(db.Date, nullable=False)
    notes           = db.Column(db.Text, default='')
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    pieces       = db.relationship('PieceChangee', backref='reparation',
                                   lazy=True, cascade='all, delete-orphan')
    machine_ref  = db.relationship('MachineTypeRef', foreign_keys=[machine_type_id],
                                   lazy='select')
    technicien_ref = db.relationship('User', foreign_keys=[technicien_id], lazy='select')

    def __repr__(self):
        return f'<Reparation {self.numero_serie} – {self.machine_type}>'