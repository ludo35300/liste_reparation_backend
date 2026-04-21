from app.extensions import db

# Table de jonction pièces ↔ modèles
modele_piece_refs = db.Table(
    'modele_piece_refs',
    db.Column('modele_id',    db.Integer,
              db.ForeignKey('modeles.id',    ondelete='CASCADE'), primary_key=True),
    db.Column('piece_ref_id', db.Integer,
              db.ForeignKey('piece_refs.id', ondelete='CASCADE'), primary_key=True)
)


class Modele(db.Model):
    __tablename__ = 'modeles'

    id           = db.Column(db.Integer, primary_key=True)
    nom          = db.Column(db.String(100), nullable=False)
    type_machine = db.Column(db.String(100), nullable=False)   # ex: Expresso, Broyeur
    marque_id    = db.Column(db.Integer,
                             db.ForeignKey('marques.id', ondelete='CASCADE'),
                             nullable=False, index=True)

    __table_args__ = (
        db.UniqueConstraint('nom', 'marque_id', name='uq_modele_marque'),
    )

    marque   = db.relationship('Marque',   back_populates='modeles')
    machines = db.relationship('Machine',  back_populates='modele',
                               lazy='select')
    pieces   = db.relationship('PieceRef', secondary='modele_piece_refs',
                               back_populates='modeles', lazy='select')

    @property
    def label(self) -> str:
        return f"{self.type_machine} {self.marque.nom} {self.nom}"

    def __repr__(self):
        return f'<Modele {self.label}>'
