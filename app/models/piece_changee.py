# app/models/piece_changee.py
from app.extensions import db

class PieceChangee(db.Model):
    __tablename__ = 'pieces_changees'

    id            = db.Column(db.Integer, primary_key=True)
    reparation_id = db.Column(db.Integer,
                              db.ForeignKey('reparations.id', ondelete='CASCADE'),
                              nullable=False, index=True)
    piece_ref_id  = db.Column(db.Integer,
                              db.ForeignKey('piece_refs.id', ondelete='RESTRICT'),
                              nullable=False, index=True)        # ← obligatoire
    ref_piece     = db.Column(db.String(50), nullable=False)    # snapshot léger
    quantite      = db.Column(db.Integer, nullable=False, default=1)

    # ── Relation ──────────────────────────────────────────────
    piece_ref = db.relationship('PieceRef', foreign_keys=[piece_ref_id], lazy='select')

    @property
    def designation(self) -> str:
        return self.piece_ref.designation if self.piece_ref else ''
        return f'<PieceChangee {self.ref_piece} x{self.quantite}>'