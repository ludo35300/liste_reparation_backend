import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from app.schemas.modele import ModeleSchema, ModeleSimpleSchema
from app.schemas.marque import MarqueSchema
from app.schemas.piece import PieceRefSchema, PieceRefUpdateSchema
from app.services import references_service as svc
from app.utils.responses import api_error
from app.extensions import db

references_bp = Blueprint('references', __name__)

marque_schema   = MarqueSchema()
marques_schema  = MarqueSchema(many=True)
modele_schema   = ModeleSchema()
modeles_schema  = ModeleSimpleSchema(many=True)
piece_schema    = PieceRefSchema()
pieces_schema   = PieceRefSchema(many=True)
piece_update_schema = PieceRefUpdateSchema()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'svg'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ── MARQUES ────────────────────────────────────────────────────
@references_bp.route('/marques', methods=['GET'])
@jwt_required()
def get_marques():
    return jsonify(marques_schema.dump(svc.get_all_marques())), 200

@references_bp.route('/marques/<int:marque_id>', methods=['GET'])
@jwt_required()
def get_marque(marque_id):
    return jsonify(marque_schema.dump(svc.get_marque_by_id(marque_id))), 200

@references_bp.route('/marques', methods=['POST'])
@jwt_required()
def create_marque():
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        nom = (request.form.get('nom') or '').strip().upper()
        file = request.files.get('logo')
        url_logo = None

        if not nom:
            return api_error("Le nom de la marque est obligatoire.", 400, code="VALIDATION_ERROR")

        if file and file.filename:
            if not allowed_file(file.filename):
                return api_error('Format non supporté (png, jpg, jpeg, webp, svg)', 422, code='VALIDATION_ERROR')

            ext = file.filename.rsplit('.', 1)[1].lower()
            safe_nom = secure_filename(nom.replace(' ', '_'))
            filename = secure_filename(f"{safe_nom}.{ext}")

            folder = os.path.join(os.path.dirname(__file__), '..', 'static', 'logos')
            os.makedirs(folder, exist_ok=True)
            file.save(os.path.join(folder, filename))

            url_logo = f"{request.host_url.rstrip('/')}/static/logos/{filename}"

        marque = svc.create_marque(nom, url_logo)
        return jsonify(marque_schema.dump(marque)), 201

    data = marque_schema.load(request.get_json(force=True) or {})
    return jsonify(marque_schema.dump(svc.create_marque(data['nom'], data.get('url_logo')))), 201

@references_bp.route('/marques/<int:marque_id>', methods=['DELETE'])
@jwt_required()
def delete_marque(marque_id):
    svc.delete_marque(marque_id)
    return jsonify({'message': 'Marque supprimée'}), 200

@references_bp.route('/marques/<int:marque_id>/logo', methods=['PATCH'])
@jwt_required()
def upload_logo_marque(marque_id):
    if 'logo' not in request.files:
        return api_error('Fichier logo manquant', 422, code='VALIDATION_ERROR')
    file = request.files['logo']
    if not file.filename or not allowed_file(file.filename):
        return api_error('Format non supporté (png, jpg, webp, svg)', 422, code='VALIDATION_ERROR')
    marque   = svc.get_marque_by_id(marque_id)
    ext      = file.filename.rsplit('.', 1)[1].lower()
    filename = secure_filename(f"{marque.nom}.{ext}")
    folder   = os.path.join(os.path.dirname(__file__), '..', 'static', 'logos')
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder, filename))
    updated  = svc.update_marque_logo(marque_id, f"/static/logos/{filename}")
    return jsonify(marque_schema.dump(updated)), 200

# ── MODELES ────────────────────────────────────────────────────
@references_bp.route('/modeles', methods=['GET'])
@jwt_required()
def get_modeles():
    marque_id = request.args.get('marque_id', type=int)
    return jsonify(modeles_schema.dump(svc.get_all_modeles(marque_id))), 200

@references_bp.route('/modeles/<int:modele_id>', methods=['GET'])
@jwt_required()
def get_modele(modele_id):
    return jsonify(modele_schema.dump(svc.get_modele_by_id(modele_id))), 200

@references_bp.route('/modeles', methods=['POST'])
@jwt_required()
def create_modele():
    data = modele_schema.load(request.get_json(force=True) or {})
    return jsonify(modele_schema.dump(svc.create_modele(data['nom'], data['type_machine'], data['marque_id']))), 201

@references_bp.route('/modeles/<int:modele_id>', methods=['DELETE'])
@jwt_required()
def delete_modele(modele_id):
    svc.delete_modele(modele_id)
    return jsonify({'message': 'Modèle supprimé'}), 200

@references_bp.route('/modeles/<int:modele_id>/pieces', methods=['GET'])
@jwt_required()
def get_pieces_by_modele(modele_id):
    return jsonify(pieces_schema.dump(svc.get_pieces_by_modele(modele_id))), 200

@references_bp.route('/modeles/<int:modele_id>/pieces/<int:piece_id>', methods=['POST'])
@jwt_required()
def add_piece(modele_id, piece_id):
    return jsonify(modele_schema.dump(svc.add_piece_to_modele(modele_id, piece_id))), 200

@references_bp.route('/modeles/<int:modele_id>/pieces/<int:piece_id>', methods=['DELETE'])
@jwt_required()
def remove_piece(modele_id, piece_id):
    return jsonify(modele_schema.dump(svc.remove_piece_from_modele(modele_id, piece_id))), 200

@references_bp.route('/suggestions/modele', methods=['GET'])
@jwt_required()
def suggest_modele():
    q = request.args.get('q', '').strip().upper()
    return jsonify([{'id': modele.id, 'label': modele.label} for modele in svc.suggest_modeles(q)]), 200

# ── PIECES ────────────────────────────────────────────────────
@references_bp.route('/pieces', methods=['GET'])
@jwt_required()
def get_pieces():
    marque_id = request.args.get('marque_id', type=int)
    return jsonify(pieces_schema.dump(svc.get_all_pieces(marque_id))), 200

@references_bp.route('/pieces/<int:piece_id>', methods=['GET'])
@jwt_required()
def get_piece(piece_id):
    return jsonify(piece_schema.dump(svc.get_piece_by_id(piece_id))), 200

@references_bp.route('/pieces', methods=['POST'])
@jwt_required()
def create_piece():
    data = piece_schema.load(request.get_json(force=True) or {})
    marque_id = data.get('marque_id')
    if not marque_id:
        return api_error("La marque est obligatoire.", 400, code="VALIDATION_ERROR")
    print(data)
    piece = svc.create_piece(
        data['ref_piece'],
        data.get('designation', ''),
        data.get('marque_id')
    )
    db.session.commit()
    return jsonify(piece_schema.dump(piece)), 201

@references_bp.route('/pieces/<int:piece_id>', methods=['PUT'])
@jwt_required()
def update_piece(piece_id):
    data  = piece_update_schema.load(request.get_json(force=True) or {})
    piece = svc.update_piece(piece_id, data['ref_piece'], data['designation'])
    return jsonify(piece_schema.dump(piece)), 200
 
@references_bp.route('/pieces/<int:piece_id>', methods=['DELETE'])
@jwt_required()
def delete_piece(piece_id):
    svc.delete_piece(piece_id)
    return jsonify({'message': 'Pièce supprimée'}), 200

@references_bp.route('/suggestions/piece-ref', methods=['GET'])
@jwt_required()
def suggest_piece_ref():
    q = request.args.get('q', '').strip().upper()
    return jsonify([{'ref_piece': piece.ref_piece, 'designation': piece.designation} for piece in svc.suggest_piece_refs(q)]), 200
