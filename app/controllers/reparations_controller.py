from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.core.errors import api_error
from app.schemas import ReparationSchema
from app.services import reparations_service as svc

reparations_bp = Blueprint('reparations', __name__)
rep_schema = ReparationSchema()
reps_schema = ReparationSchema(many=True)


@reparations_bp.route('/reparations', methods=['GET'])
@jwt_required()
def get_reparations():
    return jsonify(reps_schema.dump(svc.get_all_reparations())), 200


@reparations_bp.route('/reparations/<int:rep_id>', methods=['GET'])
@jwt_required()
def get_reparation(rep_id):
    return jsonify(rep_schema.dump(svc.get_reparation_by_id(rep_id))), 200


@reparations_bp.route('/machines/<int:machine_id>/reparations', methods=['GET'])
@jwt_required()
def get_by_machine(machine_id):
    return jsonify(reps_schema.dump(svc.get_reparations_by_machine(machine_id))), 200


@reparations_bp.route('/machines/serie/<string:numero_serie>', methods=['GET'])
@jwt_required()
def get_by_serie(numero_serie):
    reparations = svc.get_reparations_by_numero_serie(numero_serie)
    if reparations is None:
        return api_error('Machine introuvable', 404, code='MACHINE_NOT_FOUND')
    return jsonify(reps_schema.dump(reparations)), 200


@reparations_bp.route('/reparations', methods=['POST'])
@jwt_required()
def create_reparation():
    data = request.get_json(force=True)
    if not data.get('machine_id') or not data.get('date_reparation'):
        return api_error('machine_id et date_reparation requis', 422, code='VALIDATION_ERROR')
    try:
        rep = svc.creer_reparation(data)
    except ValueError as e:
        return api_error(str(e), 422, code='VALIDATION_ERROR')
    return jsonify(rep_schema.dump(rep)), 201


@reparations_bp.route('/reparations/<int:rep_id>', methods=['DELETE'])
@jwt_required()
def delete_reparation(rep_id):
    svc.delete_reparation(rep_id)
    return jsonify({'message': 'Réparation supprimée'}), 200


@reparations_bp.route('/reparations/mine', methods=['GET'])
@jwt_required()
def get_mes_reparations():
    reparations = svc.get_mes_reparations(get_jwt_identity())
    if reparations is None:
        return api_error('Utilisateur introuvable', 404, code='USER_NOT_FOUND')
    return jsonify(reps_schema.dump(reparations)), 200


@reparations_bp.route('/suggestions/piece-ref', methods=['GET'])
@jwt_required()
def suggest_piece_ref():
    q = request.args.get('q', '').strip().upper()
    pieces = svc.suggest_piece_refs(q)
    return jsonify([
        {'ref_piece': p.ref_piece, 'designation': p.designation}
        for p in pieces
    ]), 200


@reparations_bp.route('/suggestions/modele', methods=['GET'])
@jwt_required()
def suggest_modele():
    q = request.args.get('q', '').strip().upper()
    modeles = svc.suggest_modeles(q)
    return jsonify([
        {'id': m.id, 'label': m.label}
        for m in modeles
    ]), 200