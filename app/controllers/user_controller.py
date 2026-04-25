from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.core.errors import api_error
from app.repositories.user_repository import UserRepository
from app.core.errors import api_error

user_bp = Blueprint('user', __name__)


@user_bp.get('/me')
@jwt_required()
def me():
    user = UserRepository.get_by_id(int(get_jwt_identity()))
    if not user:
        return api_error("Non authentifié", 401, code="AUTH_REQUIRED")

    return jsonify({
        "email": user.email,
        "firstName": user.first_name,
        "lastName": user.last_name,
    }), 200


@user_bp.get('/techniciens')
@jwt_required()
def get_techniciens():
    users = UserRepository.get_all()

    return jsonify([
        {
            "id": user.id,
            "email": user.email,
            "nom": f"{user.first_name} {user.last_name}".strip(),
        }
        for user in users
    ]), 200