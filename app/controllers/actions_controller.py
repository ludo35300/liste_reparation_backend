from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.schemas.action import ReparationActionSchema
from app.services import actions_service as svc
from app.utils.responses import api_error

actions_bp = Blueprint('actions', __name__)

action_schema  = ReparationActionSchema()
actions_schema = ReparationActionSchema(many=True)


@actions_bp.route('/reparations/<int:rep_id>/actions', methods=['GET'])
@jwt_required()
def get_actions(rep_id):
    return jsonify(actions_schema.dump(svc.get_actions(rep_id))), 200


@actions_bp.route('/reparations/<int:rep_id>/actions', methods=['POST'])
@jwt_required()
def add_action(rep_id):
    data = action_schema.load(request.get_json(force=True) or {})
    try:
        action = svc.ajouter_action(rep_id, data)
    except ValueError as e:
        return api_error(str(e), 422, code='VALIDATION_ERROR')
    return jsonify(action_schema.dump(action)), 201


@actions_bp.route('/reparations/<int:rep_id>/actions/<int:action_id>', methods=['PATCH'])
@jwt_required()
def update_action(rep_id, action_id):
    data = action_schema.load(request.get_json(force=True) or {}, partial=True)
    try:
        action = svc.modifier_action(rep_id, action_id, data)
    except ValueError as e:
        return api_error(str(e), 422, code='VALIDATION_ERROR')
    return jsonify(action_schema.dump(action)), 200


@actions_bp.route('/reparations/<int:rep_id>/actions/<int:action_id>', methods=['DELETE'])
@jwt_required()
def delete_action(rep_id, action_id):
    try:
        svc.supprimer_action(rep_id, action_id)
    except ValueError as e:
        return api_error(str(e), 422, code='VALIDATION_ERROR')
    return jsonify({'message': 'Action supprimée'}), 200
