from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.utils.responses import api_error
from app.services import user_service as svc

# Blueprint dédié aux routes utilisateur
user_bp = Blueprint('user', __name__)

@user_bp.get('/me')
@jwt_required()
def get_current_user():
    """
    Retourne les informations du compte actuellement authentifié.

    Authentication:
        Requiert un JWT valide.

    Returns:
        tuple:
            - JSON contenant les informations utilisateur
            - HTTP 200 si succès

    Error Responses:
        401:
            Utilisateur non authentifié ou introuvable.
    """

    # Récupère l'identité stockée dans le JWT
    user = svc.get_current_user(get_jwt_identity())
    # Sécurité supplémentaire : le token peut être valide mais l'utilisateur supprimé/inexistant
    if not user:
        return api_error("Non authentifié", 401, code="AUTH_REQUIRED")

    return jsonify({ "email": user.email, "firstName": user.first_name, "lastName": user.last_name }), 200


@user_bp.get('/techniciens')
@jwt_required()
def get_techniciens():
    """
    Retourne la liste des techniciens.

    Authentication:
        Requiert un JWT valide.

    Returns:
        tuple:
            - Liste JSON des techniciens
            - HTTP 200 si succès
    """

    users = svc.get_all_techniciens()

    return jsonify([
        {
            'id': user.id,
            'email': user.email,
            'nom': f'{user.first_name} {user.last_name}'.strip(),
        }
        for user in users
    ]), 200