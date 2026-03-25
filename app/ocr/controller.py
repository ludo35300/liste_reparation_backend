from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from .service import analyser_fiche

ocr_bp = Blueprint('ocr', __name__)

@ocr_bp.route('/scan', methods=['POST'])
@jwt_required()
def scan():
    if 'image' not in request.files:
        return jsonify({"error": "Aucun fichier image reçu"}), 400
    result = analyser_fiche(request.files['image'].read())
    return jsonify(result), 200