from app.extensions import db


class PieceChangee(db.Model):
    __tablename__ = 'pieces_changees'

    id            = db.Column(db.Integer, primary_key=True)
    reparation_id = db.Column(db.Integer, db.ForeignKey('reparations.id', ondelete='CASCADE'), nullable=False, index=True)
    piece_ref_id  = db.Column(db.Integer, db.ForeignKey('piece_refs.id', ondelete='RESTRICT'), nullable=False, index=True)
    quantite      = db.Column(db.Integer, nullable=False, default=1)

    # Relation vers le catalogue
    piece_ref = db.relationship('PieceRef', foreign_keys=[piece_ref_id], lazy='select')

    # Propriétés déléguées au catalogue (pas de duplication)
    @property
    def ref_piece(self) -> str:
        return self.piece_ref.ref_piece if self.piece_ref else ''

    @property
    def designation(self) -> str:
        return self.piece_ref.designation if self.piece_ref else ''

    def __repr__(self):
        return f'<PieceChangee {self.ref_piece} x{self.quantite}>'