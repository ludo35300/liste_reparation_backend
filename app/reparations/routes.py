from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.schemas import ReparationSchema
from . import service as svc


reparations_bp = Blueprint('reparations', __name__)
rep_schema     = ReparationSchema()
reps_schema    = ReparationSchema(many=True)


# ── POST /reparations ─────────────────────────────────────────
@reparations_bp.route('/reparations', methods=['POST'])
@jwt_required()
def creer():
    try:
        data = rep_schema.load(request.get_json(force=True))
    except ValidationError as e:
        return jsonify({"errors": e.messages}), 422

    rep = svc.creer_reparation(data)
    return jsonify(rep_schema.dump(rep)), 201


# ── GET /reparations/<numero_serie> ───────────────────────────
@reparations_bp.route('/reparations/<string:numero_serie>', methods=['GET'])
@jwt_required()
def historique(numero_serie):
    reps = svc.get_historique(numero_serie)
    return jsonify(reps_schema.dump(reps)), 200


# ── GET /reparations/id/<rep_id> ──────────────────────────────
@reparations_bp.route('/reparations/id/<int:rep_id>', methods=['GET'])
@jwt_required()
def detail(rep_id):
    rep = svc.get_by_id(rep_id)
    return jsonify(rep_schema.dump(rep)), 200


# ── DELETE /reparations/<rep_id> ──────────────────────────────
@reparations_bp.route('/reparations/<int:rep_id>', methods=['DELETE'])
@jwt_required()
def supprimer(rep_id):
    svc.supprimer(rep_id)
    return jsonify({"message": "Réparation supprimée"}), 200


# ── GET /suggestions/machine-type?q=... ───────────────────────
@reparations_bp.route('/suggestions/machine-type', methods=['GET'])
@jwt_required()
def suggest_machine_type():
    query = request.args.get('q', '').strip()
    matches = svc.suggest_machine_types(query)
    return jsonify(matches), 200


# ── GET /suggestions/piece-ref?q=... ─────────────────────────
@reparations_bp.route('/suggestions/piece-ref', methods=['GET'])
@jwt_required()
def suggest_piece_ref():
    query = request.args.get('q', '').strip()
    matches = svc.suggest_piece_refs(query)
    return jsonify(matches), 200