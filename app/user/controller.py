from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..repositories.memory import users, norm_email

user_bp = Blueprint("user", __name__)

@user_bp.get("/me")
@jwt_required()
def me():
    email = norm_email(get_jwt_identity())
    user = users.get(email)
    if not user:
        return jsonify({"message": "Non authentifié"}), 401
    return jsonify({"email": user.email, "firstName": user.first_name, "lastName": user.last_name}), 200
