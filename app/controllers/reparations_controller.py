from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.utils.responses import api_error
from app.schemas import ReparationSchema
from app.services import reparations_service as svc

reparations_bp = Blueprint('reparations', __name__)
reparation_schema = ReparationSchema()
reparations_schema = ReparationSchema(many=True)


@reparations_bp.route('/reparations', methods=['GET'])
@jwt_required()
def get_reparations():
    return jsonify(reparations_schema.dump(svc.get_all_reparations())), 200

@reparations_bp.route('/reparations/<int:rep_id>', methods=['GET'])
@jwt_required()
def get_reparation(rep_id):
    return jsonify(reparation_schema.dump(svc.get_reparation_by_id(rep_id))), 200

@reparations_bp.route('/machines/<int:machine_id>/reparations', methods=['GET'])
@jwt_required()
def get_by_machine(machine_id):
    return jsonify(reparations_schema.dump(svc.get_reparations_by_machine(machine_id))), 200

@reparations_bp.route('/machines/serie/<string:numero_serie>', methods=['GET'])
@jwt_required()
def get_by_serie(numero_serie):
    reparations = svc.get_reparations_by_numero_serie(numero_serie)
    if reparations is None:
        return api_error('Machine introuvable', 404, code='MACHINE_NOT_FOUND')
    return jsonify(reparations_schema.dump(reparations)), 200

@reparations_bp.route('/reparations', methods=['POST'])
@jwt_required()
def create_reparation():
    data = reparation_schema.load(request.get_json(force=True) or {})
    rep  = svc.creer_reparation(data)
    return jsonify(reparation_schema.dump(rep)), 201

@reparations_bp.route('/reparations/<int:rep_id>', methods=['PATCH'])
@jwt_required()
def update_reparation(rep_id):
    data = reparation_schema.load(request.get_json(force=True) or {}, partial=True)
    rep  = svc.modifier_reparation(rep_id, data)
    return jsonify(reparation_schema.dump(rep)), 200

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
    return jsonify(reparations_schema.dump(reparations)), 200