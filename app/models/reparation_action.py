from datetime import datetime, timezone
from app.extensions import db

TYPES_ACTION_VALIDES = (
    'diagnostic', 'demontage', 'remplacement_piece',
    'nettoyage', 'test', 'commentaire', 'statut'
)

RESULTATS_CLOTURE_VALIDES = (
    'reparee', 'non_reparable', 'attente_piece', 'restitution'
)


class ReparationAction(db.Model):
    __tablename__ = 'reparation_actions'

    id             = db.Column(db.Integer, primary_key=True)
    reparation_id  = db.Column(db.Integer,
                               db.ForeignKey('reparations.id', ondelete='CASCADE'),
                               nullable=False, index=True)
    technicien_id  = db.Column(db.Integer,
                               db.ForeignKey('users.id', ondelete='SET NULL'),
                               nullable=True, index=True)
    type           = db.Column(db.String(30), nullable=False)
    titre          = db.Column(db.String(200), nullable=False)
    description    = db.Column(db.Text, default='')
    technicien     = db.Column(db.String(100), default='')   # snapshot
    date_action    = db.Column(db.Date, nullable=False)
    duree_minutes  = db.Column(db.Integer, nullable=True)
    statut_avant   = db.Column(db.String(20), nullable=True)
    statut_apres   = db.Column(db.String(20), nullable=True)
    created_at     = db.Column(db.DateTime(timezone=True),
                               default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.CheckConstraint(
            "type IN ('diagnostic','demontage','remplacement_piece',"
            "'nettoyage','test','commentaire','statut')",
            name='ck_action_type'
        ),
        db.CheckConstraint(
            "statut_avant IS NULL OR statut_avant IN "
            "('en_attente','en_reparation','pret','termine')",
            name='ck_action_statut_avant'
        ),
        db.CheckConstraint(
            "statut_apres IS NULL OR statut_apres IN "
            "('en_attente','en_reparation','pret','termine')",
            name='ck_action_statut_apres'
        ),
    )

    reparation    = db.relationship('Reparation',      back_populates='actions')
    technicien_ref = db.relationship('User',           foreign_keys=[technicien_id])


    def __repr__(self):
        return f'<ReparationAction {self.type} rep={self.reparation_id}>'
