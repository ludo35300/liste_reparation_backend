from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models.machine import Machine
from app.models.piece_ref import PieceRef
from app.models.reparation import Reparation
from app.models.user import User
from app.schemas import ReparationSchema
from . import service as svc

reparations_bp = Blueprint('reparations', __name__)
rep_schema     = ReparationSchema()
reps_schema    = ReparationSchema(many=True)


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
    """Historique par numéro de série — pour la recherche rapide depuis le front."""
    machine = Machine.query.filter_by(numero_serie=numero_serie.strip().upper()).first()
    if not machine:
        return jsonify({'error': 'Machine introuvable'}), 404
    return jsonify(reps_schema.dump(svc.get_reparations_by_machine(machine.id))), 200

@reparations_bp.route('/reparations', methods=['POST'])
@jwt_required()
def create_reparation():
    data = request.get_json(force=True)
    if not data.get('machine_id') or not data.get('date_reparation'):
        return jsonify({'error': 'machine_id et date_reparation requis'}), 422
    rep = svc.creer_reparation(data)
    return jsonify(rep_schema.dump(rep)), 201

@reparations_bp.route('/reparations/<int:rep_id>', methods=['DELETE'])
@jwt_required()
def delete_reparation(rep_id):
    svc.delete_reparation(rep_id)
    return jsonify({'message': 'Réparation supprimée'}), 200

@reparations_bp.route('/reparations/mine', methods=['GET'])
@jwt_required()
def get_mes_reparations():

    identity = get_jwt_identity()
    user = User.query.filter_by(id=identity).first()
    technicien = user.first_name+" "+user.last_name
    print(reps_schema.dump(svc.get_reparations_by_technicien(technicien)))
    return jsonify(reps_schema.dump(svc.get_reparations_by_technicien(technicien))), 200

@reparations_bp.route('/suggestions/piece-ref', methods=['GET'])
@jwt_required()
def suggest_piece_ref():
    q = request.args.get('q', '').strip().upper()
    pieces = PieceRef.query.filter(
        PieceRef.ref_piece.ilike(f'%{q}%')
    ).limit(10).all()
    return jsonify([
        {'ref_piece': p.ref_piece, 'designation': p.designation}
        for p in pieces
    ]), 200


@reparations_bp.route('/suggestions/modele', methods=['GET'])
@jwt_required()
def suggest_modele():
    from app.models.modele import Modele
    q = request.args.get('q', '').strip().upper()
    modeles = Modele.query.filter(
        Modele.nom.ilike(f'%{q}%')
    ).limit(10).all()
    return jsonify([
        {'id': m.id, 'label': m.label}
        for m in modeles
    ]), 200