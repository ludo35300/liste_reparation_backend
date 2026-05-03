from app.extensions import db


class PieceRef(db.Model):
    __tablename__ = 'piece_refs'

    id          = db.Column(db.Integer, primary_key=True)
    ref_piece   = db.Column(db.String(100), nullable=False, unique=True)
    designation = db.Column(db.String(200), nullable=False, default='')
    marque_id   = db.Column(db.Integer,
                            db.ForeignKey('marques.id', ondelete='CASCADE'),
                            nullable=False, index=True)

    marque   = db.relationship('Marque',  back_populates='pieces')
    modeles  = db.relationship('Modele',  secondary='modele_piece_refs',
                               back_populates='pieces', lazy='select')
    utilisations = db.relationship('PieceChangee', back_populates='piece_ref',
                                   lazy='select')

    def __repr__(self):
        return f'<PieceRef {self.ref_piece}>'
