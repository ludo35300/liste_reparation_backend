from app.extensions import db

# ── Table pivot Many-to-Many ───────────────────────────────────
machine_piece_refs = db.Table(
    'machine_piece_refs',
    db.Column('machine_type_id', db.Integer,
              db.ForeignKey('machine_type_refs.id', ondelete='CASCADE'),
              primary_key=True),
    db.Column('piece_ref_id', db.Integer,
              db.ForeignKey('piece_refs.id', ondelete='CASCADE'),
              primary_key=True)
)


class MachineTypeRef(db.Model):
    __tablename__ = 'machine_type_refs'

    id      = db.Column(db.Integer, primary_key=True)
    marque  = db.Column(db.String(100), nullable=False)
    modele  = db.Column(db.String(100), nullable=False)
    type_machine = db.Column(db.String(100), nullable=False)  # ex: MOULIN, CAFETIERE...
    url_logo = db.Column(db.String(500), nullable=True)

    # Contrainte d'unicité sur la combinaison des 3
    __table_args__ = (
        db.UniqueConstraint('marque', 'modele', 'type_machine', name='uq_machine'),
    )

    # Propriété calculée pour la rétrocompatibilité
    @property
    def label(self):
        return f"{self.type_machine} {self.marque} {self.modele}"

    pieces = db.relationship(
        'PieceRef',
        secondary=machine_piece_refs,
        back_populates='machines',
        lazy='select'
    )

    def __repr__(self):
        return f'<MachineTypeRef {self.label}>'


class PieceRef(db.Model):
    __tablename__ = 'piece_refs'

    id          = db.Column(db.Integer, primary_key=True)
    ref_piece   = db.Column(db.String(100), nullable=False, unique=True)
    designation = db.Column(db.String(200))

    # Relation inverse
    machines = db.relationship(
        'MachineTypeRef',
        secondary=machine_piece_refs,
        back_populates='pieces',
        lazy='select'
    )

    def __repr__(self):
        return f'<PieceRef {self.ref_piece}>'