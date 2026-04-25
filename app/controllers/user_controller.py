from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.repositories.database import get_user_by_id, get_all_users

user_bp = Blueprint('user', __name__)

@user_bp.get('/me')
@jwt_required()
def me():
    user = get_user_by_id(int(get_jwt_identity()))
    if not user:
        return jsonify({"message": "Non authentifié"}), 401
    return jsonify({
        "email":     user.email,
        "firstName": user.first_name,
        "lastName":  user.last_name
    }), 200

def get_techniciens():
    users = get_all_users()

    return jsonify([
        {
            'id': user.id,
            'email': user.email,
            'nom': f'{user.first_name} {user.last_name}'.strip(),
        }
        for user in users
    ])
