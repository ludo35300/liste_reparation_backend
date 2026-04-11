import os

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.schemas import MachineTypeRefSchema, PieceRefSchema, MachineTypeRefSimpleSchema
from werkzeug.utils import secure_filename
from . import service as svc

references_bp = Blueprint('references', __name__)

machine_schema      = MachineTypeRefSchema()
machines_schema     = MachineTypeRefSchema(many=True)
machine_simple      = MachineTypeRefSimpleSchema(many=True)
piece_schema        = PieceRefSchema()
pieces_schema       = PieceRefSchema(many=True)


# ── GET /machines ──────────────────────────────────────────────
@references_bp.route('/machines', methods=['GET'])
@jwt_required()
def get_machines():
    machines = svc.get_all_machines()
    return jsonify(machine_simple.dump(machines)), 200

# ── GET /machines/<id> ─────────────────────────────────────────
@references_bp.route('/machines/<int:machine_id>', methods=['GET'])
@jwt_required()
def get_machine(machine_id):
    machine = svc.get_machine_by_id(machine_id)
    return jsonify(machine_schema.dump(machine)), 200


# ── POST /machines ─────────────────────────────────────────────
@references_bp.route('/machines', methods=['POST'])
@jwt_required()
def create_machine():
    data         = request.get_json(force=True)
    marque       = data.get('marque', '').strip()
    modele       = data.get('modele', '').strip()
    url_logo     = data.get('url_logo', '').strip()
    type_machine = data.get('type_machine', '').strip()

    if not marque or not modele or not type_machine:
        return jsonify({'error': 'marque, modele et type_machine sont requis'}), 422

    machine = svc.create_machine(marque, modele, type_machine)
    return jsonify(machine_schema.dump(machine)), 201


# ── DELETE /machines/<id> ──────────────────────────────────────
@references_bp.route('/machines/<int:machine_id>', methods=['DELETE'])
@jwt_required()
def delete_machine(machine_id):
    svc.delete_machine(machine_id)
    return jsonify({'message': 'Machine supprimée'}), 200


# ── GET /pieces ────────────────────────────────────────────────
@references_bp.route('/pieces', methods=['GET'])
@jwt_required()
def get_pieces():
    pieces = svc.get_all_pieces()
    return jsonify(pieces_schema.dump(pieces)), 200


# ── POST /pieces ───────────────────────────────────────────────
@references_bp.route('/pieces', methods=['POST'])
@jwt_required()
def create_piece():
    data        = request.get_json(force=True)
    ref_piece   = data.get('ref_piece', '').strip()
    designation = data.get('designation', '').strip()
    if not ref_piece:
        return jsonify({'error': 'ref_piece requis'}), 422
    piece = svc.create_piece(ref_piece, designation)
    return jsonify(piece_schema.dump(piece)), 201


# ── DELETE /pieces/<id> ────────────────────────────────────────
@references_bp.route('/pieces/<int:piece_id>', methods=['DELETE'])
@jwt_required()
def delete_piece(piece_id):
    svc.delete_piece(piece_id)
    return jsonify({'message': 'Pièce supprimée'}), 200


# ── POST /machines/<id>/pieces/<piece_id> ──────────────────────
@references_bp.route('/machines/<int:machine_id>/pieces/<int:piece_id>',
                     methods=['POST'])
@jwt_required()
def add_piece(machine_id, piece_id):
    machine = svc.add_piece_to_machine(machine_id, piece_id)
    return jsonify(machine_schema.dump(machine)), 200


# ── DELETE /machines/<id>/pieces/<piece_id> ────────────────────
@references_bp.route('/machines/<int:machine_id>/pieces/<int:piece_id>',
                     methods=['DELETE'])
@jwt_required()
def remove_piece(machine_id, piece_id):
    machine = svc.remove_piece_from_machine(machine_id, piece_id)
    return jsonify(machine_schema.dump(machine)), 200

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'svg'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# ── GET /machines/<id>/pieces ──────────────────────────────────
@references_bp.route('/machines/<int:machine_id>/pieces', methods=['GET'])
@jwt_required()
def get_pieces_by_machine(machine_id):
    pieces = svc.get_pieces_by_machine(machine_id)
    return jsonify(pieces_schema.dump(pieces)), 200


# ── PATCH /machines/<id>/logo ──────────────────────────────
@references_bp.route('/machines/<int:machine_id>/logo', methods=['PATCH'])
@jwt_required()
def upload_logo(machine_id):
    if 'logo' not in request.files:
        return jsonify({'error': 'Fichier logo manquant'}), 422

    file = request.files['logo']
    if not file.filename or not allowed_file(file.filename):
        return jsonify({'error': 'Format non supporté (png, jpg, webp, svg)'}), 422

    machine = svc.get_machine_by_id(machine_id)

    ext      = file.filename.rsplit('.', 1)[1].lower()
    filename = secure_filename(f"{machine.marque.upper()}.{ext}")
    folder   = os.path.join(os.path.dirname(__file__), '..', 'static', 'logos')
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder, filename))

    logo_url = f"/static/logos/{filename}"
    updated  = svc.update_machine_logo(machine_id, logo_url)

    return jsonify(machine_schema.dump(updated)), 200