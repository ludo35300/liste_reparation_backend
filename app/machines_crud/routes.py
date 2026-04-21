from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.schemas import MachineSchema
from . import service as svc

machines_bp  = Blueprint('machines', __name__)
mach_schema  = MachineSchema()
machs_schema = MachineSchema(many=True)


@machines_bp.route('/machines', methods=['GET'])
@jwt_required()
def get_machines():
    return jsonify(machs_schema.dump(svc.get_all_machines())), 200


@machines_bp.route('/machines/<int:machine_id>', methods=['GET'])
@jwt_required()
def get_machine(machine_id):
    return jsonify(mach_schema.dump(svc.get_machine_by_id(machine_id))), 200


@machines_bp.route('/machines', methods=['POST'])
@jwt_required()
def create_machine():
    data = request.get_json(force=True)
    if not data.get('numero_serie'):
        return jsonify({'error': 'numero_serie requis'}), 422
    try:
        machine = svc.create_machine(data)
    except ValueError as e:
        return jsonify({'error': str(e)}), 409
    return jsonify(mach_schema.dump(machine)), 201


@machines_bp.route('/machines/<int:machine_id>', methods=['PATCH'])
@jwt_required()
def update_machine(machine_id):
    data = request.get_json(force=True)
    machine = svc.update_machine(machine_id, data)
    return jsonify(mach_schema.dump(machine)), 200


@machines_bp.route('/machines/<int:machine_id>', methods=['DELETE'])
@jwt_required()
def delete_machine(machine_id):
    svc.delete_machine(machine_id)
    return jsonify({'message': 'Machine supprimée'}), 200


@machines_bp.route('/machines/serie/<string:numero_serie>', methods=['GET'])
@jwt_required()
def get_by_serie(numero_serie):
    machine = svc.get_machine_by_serie(numero_serie)
    if not machine:
        return jsonify({'error': 'Machine non trouvée'}), 404
    return jsonify(mach_schema.dump(machine)), 200


@machines_bp.route('/machines/<int:machine_id>/info', methods=['GET'])
@jwt_required()
def get_machine_info(machine_id):
    """Retourne les specs + vue éclatée si disponibles pour ce modèle."""
    return jsonify(svc.get_machine_info(machine_id)), 200
