from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.repositories.machine_repository import MachineRepository
from app.repositories.reparation_repository import ReparationRepository
from app.schemas.machine import MachineSchema
from app.schemas.reparation import ReparationSchema
from app.utils.responses import api_error
from app.services import reparations_service as svc
from app.utils.exceptions import MachineAlreadyInRepairError

reparations_bp = Blueprint('reparations', __name__)
machine_schema = MachineSchema()
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
    machine = MachineRepository.get_by_serie(numero_serie)
    if not machine:
        return api_error('Machine introuvable', 404, code='MACHINE_NOT_FOUND')

    reparations = ReparationRepository.get_by_machine(machine.id)

    # Infos enrichies (specs, vue éclatée) si disponibles
    machine_info = None
    if machine.modele:
        from app.machines import resolve_machine_info
        info = resolve_machine_info(
            brand        = machine.modele.marque.nom if machine.modele.marque else '',
            model        = machine.modele.nom,
            numero_serie = machine.numero_serie,
        )
        if info:
            machine_info = {
                "brand":         info.brand,
                "model":         info.model,
                "description":   info.description,
                "specs":         info.specs,
                "exploded_view": {
                    "label":     info.exploded_view.label,
                    "pdf_url":   info.exploded_view.pdf_url,
                    "image_url": getattr(info.exploded_view, 'image_url', None),
                    "note":      info.exploded_view.note,
                } if info.exploded_view else None,
            }

    return jsonify({
        "found":              True,
        "numero_serie":       machine.numero_serie,
        "machine":            machine_schema.dump(machine), 
        "machine_type":       machine.modele.label if machine.modele else None,
        "nombre_reparations": len(reparations),
        "reparations":        reparations_schema.dump(reparations),
        "machine_info":       machine_info,
    }), 200

@reparations_bp.route('/reparations', methods=['POST'])
@jwt_required()
def create_reparation():
    data = reparation_schema.load(request.get_json(force=True) or {})
    try:
        rep = svc.creer_reparation(data)
    except MachineAlreadyInRepairError as e:
        return api_error(str(e), 409, code=e.code)
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