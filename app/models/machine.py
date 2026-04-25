from datetime import datetime, timezone
from app.extensions import db

STATUTS_VALIDES = ('en_attente', 'en_reparation', 'pret', 'termine')


class Machine(db.Model):
    __tablename__ = 'machines'

    id           = db.Column(db.Integer, primary_key=True)
    numero_serie = db.Column(db.String(100), nullable=False, unique=True, index=True)
    modele_id    = db.Column(db.Integer,
                             db.ForeignKey('modeles.id', ondelete='SET NULL'),
                             nullable=True, index=True)
    statut       = db.Column(db.String(20), nullable=False, default='en_attente')
    date_entree  = db.Column(db.Date, nullable=True)
    notes        = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.CheckConstraint(
            "statut IN ('en_attente', 'en_reparation', 'pret', 'termine')",
            name='ck_machine_statut'
        ),
    )

    modele      = db.relationship('Modele',     back_populates='machines')
    reparations = db.relationship('Reparation', back_populates='machine',
                                  cascade='all, delete-orphan', lazy='select')

    def __repr__(self):
        return f'<Machine {self.numero_serie} [{self.statut}]>'
