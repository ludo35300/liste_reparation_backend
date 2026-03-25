from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.reparation import Reparation
from app.models.piece_changee import PieceChangee

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/stats', methods=['GET'])
@jwt_required()
def stats():
    total     = Reparation.query.count()
    machines  = db.session.query(Reparation.numero_serie).distinct().count()
    total_pcs = db.session.query(db.func.sum(PieceChangee.quantite)).scalar() or 0
    top10     = db.session.query(
        PieceChangee.ref_piece,
        PieceChangee.designation,
        db.func.sum(PieceChangee.quantite).label('total')
    ).group_by(PieceChangee.ref_piece) \
     .order_by(db.desc('total')).limit(10).all()

    return jsonify({
        "total_reparations":        total,
        "machines_uniques":         machines,
        "total_pieces":             total_pcs,
        "pieces_les_plus_changees": [
            {"ref": r, "designation": d, "total": t} for r, d, t in top10
        ]
    }), 200