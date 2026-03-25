from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.schemas import ReparationSchema, ReparationCreateSchema
from . import service as svc

reparations_bp  = Blueprint('reparations', __name__)
rep_schema      = ReparationSchema()
reps_schema     = ReparationSchema(many=True)
create_schema   = ReparationCreateSchema()

@reparations_bp.route('/reparations', methods=['POST'])
@jwt_required()
def creer():
    try:
        data = create_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({"errors": e.messages}), 422
    rep = svc.creer_reparation(data)
    return jsonify(rep_schema.dump(rep)), 201

@reparations_bp.route('/reparations/<numero_serie>', methods=['GET'])
@jwt_required()
def historique(numero_serie):
    reps = svc.get_historique(numero_serie)
    return jsonify(reps_schema.dump(reps)), 200

@reparations_bp.route('/reparations/id/<int:rep_id>', methods=['GET'])
@jwt_required()
def detail(rep_id):
    rep = svc.get_by_id(rep_id)
    return jsonify(rep_schema.dump(rep)), 200

@reparations_bp.route('/reparations/<int:rep_id>', methods=['DELETE'])
@jwt_required()
def supprimer(rep_id):
    svc.supprimer(rep_id)
    return jsonify({"message": "Réparation supprimée"}), 200