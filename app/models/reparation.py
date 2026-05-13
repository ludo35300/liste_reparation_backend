from datetime import datetime, timezone
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
    technicien      = db.Column(db.String(100), default='')
    date_reparation = db.Column(db.Date, nullable=False)
    date_cloture    = db.Column(db.Date, nullable=True)
    statut          = db.Column(db.String(20), nullable=False, default='en_reparation')
    description     = db.Column(db.Text, default='')
    created_at      = db.Column(db.DateTime(timezone=True),
                                default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.CheckConstraint(
            "statut IN STATUTS_REPARATION_VALIDES",
            name='ck_reparation_statut'
        ),
    )

    machine         = db.relationship('Machine', back_populates='reparations')
    technicien_ref  = db.relationship('User', back_populates='reparations',
                                      foreign_keys=[technicien_id])
    pieces          = db.relationship('PieceChangee', back_populates='reparation',
                                      cascade='all, delete-orphan', lazy='select')
    actions         = db.relationship('ReparationAction', back_populates='reparation',
                                      cascade='all, delete-orphan',
                                      order_by='ReparationAction.date_action',
                                      lazy='select')

    def __repr__(self):
        return f'<Reparation machine={self.machine_id} {self.date_reparation} [{self.statut}]>'