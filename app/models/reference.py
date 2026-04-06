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

    pieces      = db.relationship('PieceRef', secondary=machine_piece_refs,
                                  back_populates='machines', lazy='select')
    reparations = db.relationship('Reparation', back_populates='machine_ref',
                                  foreign_keys='Reparation.machine_type_id',
                                  lazy='dynamic')

    @property
    def label(self) -> str:
        return f"{self.type_machine} {self.marque} {self.modele}"

    @classmethod
    def find_by_label(cls, label: str):
        label = label.strip().upper()
        for m in cls.query.all():
            if m.label.upper() == label:
                return m
        return None

    def __repr__(self):
        return f'<MachineTypeRef {self.label}>'


class PieceRef(db.Model):
    __tablename__ = 'piece_refs'

    id          = db.Column(db.Integer, primary_key=True)
    ref_piece   = db.Column(db.String(100), nullable=False, unique=True)
    designation = db.Column(db.String(200), nullable=False, default='')

    machines     = db.relationship('MachineTypeRef', secondary=machine_piece_refs,
                                   back_populates='pieces', lazy='select')
    utilisations = db.relationship('PieceChangee', back_populates='piece_ref',
                                   foreign_keys='PieceChangee.piece_ref_id',
                                   lazy='dynamic')

    def __repr__(self):
        return f'<PieceRef {self.ref_piece}>'