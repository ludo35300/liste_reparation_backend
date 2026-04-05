# app/models/piece_changee.py
from app.extensions import db


class PieceChangee(db.Model):
    __tablename__ = 'pieces_changees'

    id            = db.Column(db.Integer, primary_key=True)
    reparation_id = db.Column(db.Integer,
                              db.ForeignKey('reparations.id', ondelete='CASCADE'),
                              nullable=False, index=True)

    # ── Snapshot texte ─────────────────────────────────────────────
    ref_piece     = db.Column(db.String(50),  nullable=False)
    designation   = db.Column(db.String(200), nullable=False)

    # ── FK relationnelle ───────────────────────────────────────────
    piece_ref_id  = db.Column(db.Integer,
                              db.ForeignKey('piece_refs.id', ondelete='SET NULL'),
                              nullable=True, index=True)

    quantite      = db.Column(db.Integer, nullable=False, default=1)

    # ── Relation ───────────────────────────────────────────────────
    piece_ref     = db.relationship('PieceRef', foreign_keys=[piece_ref_id], lazy='select')

    def __repr__(self):
        return f'<PieceChangee {self.ref_piece} x{self.quantite}>'