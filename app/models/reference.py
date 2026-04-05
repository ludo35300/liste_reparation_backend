# app/models/reference.py
from app.extensions import db

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

    id           = db.Column(db.Integer, primary_key=True)
    marque       = db.Column(db.String(100), nullable=False)
    modele       = db.Column(db.String(100), nullable=False)
    type_machine = db.Column(db.String(100), nullable=False)
    url_logo     = db.Column(db.String(500), nullable=True)

    __table_args__ = (
        db.UniqueConstraint('marque', 'modele', 'type_machine', name='uq_machine'),
    )

    @property
    def label(self) -> str:
        return f"{self.type_machine} {self.marque} {self.modele}"

    pieces = db.relationship('PieceRef', secondary=machine_piece_refs,
                             back_populates='machines', lazy='select')

    # Relation inverse vers les réparations
    reparations = db.relationship('Reparation', back_populates='machine_ref',
                                  foreign_keys='Reparation.machine_type_id',
                                  lazy='dynamic')

    def __repr__(self):
        return f'<MachineTypeRef {self.label}>'
    
    @classmethod
    def find_by_label(cls, label: str):
        """Recherche par label reconstruit (type_machine + marque + modele)."""
        from sqlalchemy import func
        parts = label.strip().split(' ', 2)  # ["TYPE", "MARQUE", "MODELE"]
        if len(parts) < 3:
            return None
        return cls.query.filter_by(
            type_machine=parts[0],
            marque=parts[1],
            modele=parts[2]
        ).first()


class PieceRef(db.Model):
    __tablename__ = 'piece_refs'

    id          = db.Column(db.Integer, primary_key=True)
    ref_piece   = db.Column(db.String(100), nullable=False, unique=True)
    designation = db.Column(db.String(200))

    machines = db.relationship('MachineTypeRef', secondary=machine_piece_refs,
                               back_populates='pieces', lazy='select')

    # Relation inverse vers les pièces changées
    utilisations = db.relationship('PieceChangee', back_populates='piece_ref',
                                   foreign_keys='PieceChangee.piece_ref_id',
                                   lazy='dynamic')

    def __repr__(self):
        return f'<PieceRef {self.ref_piece}>'