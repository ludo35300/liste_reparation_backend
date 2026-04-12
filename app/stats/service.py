from sqlalchemy import distinct, func
from sqlalchemy.orm import joinedload
from app.extensions           import db
from app.models.reference     import PieceRef
from app.models.reparation    import Reparation
from app.models.piece_changee import PieceChangee


def get_stats_globales() -> dict:
    total_reps   = db.session.query(func.count(Reparation.id)).scalar() or 0
    total_pieces = db.session.query(func.sum(PieceChangee.quantite)).scalar() or 0
    machines_uniques = db.session.query(
        func.count(distinct(Reparation.numero_serie))
    ).scalar() or 0

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

    # ── Toutes les réparations avec leurs pièces ──────────────────
    reparations = (
        db.session.query(Reparation)
        .options(joinedload(Reparation.pieces))   # évite le N+1
        .order_by(Reparation.date_reparation.desc())
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
        "reparations": [
            {
                "id":               r.id,
                "numero_serie":     r.numero_serie,
                "machine_type":     r.machine_type,
                "technicien":       r.technicien,
                "date_reparation":  r.date_reparation,
                "notes":            r.notes,
                "pieces": [
                    {
                        "ref_piece":   pc.ref_piece,
                        "designation": pc.designation,
                        "quantite":    pc.quantite,
                    }
                    for pc in (r.pieces or [])
                ],
            }
            for r in reparations
        ],
    }