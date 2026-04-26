# app/ocr/routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .service import analyser_fiche
from app.utils.responses import api_error

ocr_bp = Blueprint('ocr', __name__)


@ocr_bp.route('/scan', methods=['POST'])
@jwt_required()
def scan():
    if 'image' not in request.files:
        return api_error("Aucun fichier image reçu", 400, code="VALIDATION_ERROR")

    user_id = int(get_jwt_identity())
    result  = analyser_fiche(request.files['image'].read(), fallback_user_id=user_id)

    if "erreur" in result:
        return api_error(result["erreur"], 422, code="OCR_ERROR", details=result)

    return jsonify(result), 200