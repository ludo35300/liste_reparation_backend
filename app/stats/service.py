# app/stats/service.py
from sqlalchemy import func
from app.extensions          import db
from app.models.reparation   import Reparation
from app.models.piece_changee import PieceChangee


def get_stats_globales() -> dict:
    total_reps   = db.session.query(func.count(Reparation.id)).scalar() or 0
    total_pieces = db.session.query(func.sum(PieceChangee.quantite)).scalar() or 0
    return {
        "total_reparations": int(total_reps),
        "total_pieces":      int(total_pieces),
    }