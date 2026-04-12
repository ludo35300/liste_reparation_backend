# app/stats/service.py
from sqlalchemy import distinct, func
from app.extensions          import db
from app.models.reference import PieceRef
from app.models.reparation   import Reparation
from app.models.piece_changee import PieceChangee


def get_stats_globales() -> dict:
    total_reps   = db.session.query(func.count(Reparation.id)).scalar() or 0
    total_pieces = db.session.query(func.sum(PieceChangee.quantite)).scalar() or 0
    machines_uniques = db.session.query(func.count(distinct(Reparation.numero_serie))).scalar() or 0
    # ── Top 10 pièces les plus changées ───────────────────────────
    top_pieces = (
        db.session.query(
            PieceRef.ref_piece.label("ref"),
            PieceRef.designation.label("designation"),
            func.sum(PieceChangee.quantite).label("total"),
        )
        .join(PieceRef, PieceChangee.piece_ref_id == PieceRef.id)
        .group_by(PieceRef.id, PieceRef.ref_piece, PieceRef.designation)
        .order_by(func.sum(PieceChangee.quantite).desc())
        .limit(10)
        .all()
    )
    return {
        "total_reparations": int(total_reps),
        "total_pieces":      int(total_pieces),
        "machines_uniques":  int(machines_uniques),
        "pieces_les_plus_changees": [
            {
                "ref":         p.ref,
                "designation": p.designation,
                "total":       int(p.total),
            }
            for p in top_pieces
        ],
    }