from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from .service import (
    login_user, refresh_access_token, logout_user,
    register_user, forgot_password, reset_password
)
from ..extensions import limiter

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/login")
@limiter.limit("10 per minute")
def login():
    data = request.get_json(silent=True) or {}
    return login_user(data.get("email"), data.get("password"))

@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    return refresh_access_token()

@auth_bp.post("/logout")
@jwt_required()
def logout():
    return logout_user()

@auth_bp.post("/register")
@limiter.limit("3 per minute")
def register():
    data = request.get_json(silent=True) or {}
    return register_user(data.get("email"), data.get("password"), data.get("firstName"), data.get("lastName"))

@auth_bp.post("/forgot-password")
@limiter.limit("5 per minute")
def forgot():
    data = request.get_json(silent=True) or {}
    return forgot_password(data.get("email"))

@auth_bp.post("/reset-password")
@limiter.limit("5 per minute")
def reset():
    data = request.get_json(silent=True) or {}
    return reset_password(data.get("token"), data.get("password"))

@auth_bp.get("/csrf")
def csrf():
    # Juste pour "réveiller" la session et s'assurer que les cookies CSRF sont présents.
    # Utile au démarrage de l'app Angular.
    return jsonify({"ok": True}), 200

@auth_bp.get("/session")
@jwt_required()
def session():
    return {"ok": True}, 200
