from flask import jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    get_jwt_identity, set_access_cookies, set_refresh_cookies, unset_jwt_cookies
)

from app.security.passwords import verify_password, hash_password, needs_rehash

from ..repositories.memory import users, norm_email, hash_pwd_dev, User
from ..security.reset_tokens import create_reset_token, consume_reset_token

def login_user(email: str, password: str):
    email = norm_email(email)
    user = users.get(email)
    if not user or not verify_password(password or "", user.password_hash):
        return jsonify({"message": "Identifiants invalides"}), 401

    access = create_access_token(identity=user.email)
    refresh = create_refresh_token(identity=user.email)

    resp = jsonify({"ok": True, "user": {"email": user.email, "firstName": user.first_name, "lastName": user.last_name}})
    set_access_cookies(resp, access)
    set_refresh_cookies(resp, refresh)
    return resp, 200

def refresh_access_token():
    email = get_jwt_identity()
    new_access = create_access_token(identity=email)
    resp = jsonify({"ok": True})
    set_access_cookies(resp, new_access)
    return resp, 200

def logout_user():
    resp = jsonify({"ok": True})
    unset_jwt_cookies(resp)  # nécessaire car cookies HttpOnly [web:94]
    return resp, 200

def register_user(email: str, password: str, first_name: str, last_name: str):
    email = norm_email(email)
    if not email or not (password or ""):
        return jsonify({"message": "Email et mot de passe requis"}), 400
    if email in users:
        return jsonify({"message": "Email déjà utilisé"}), 409

    users[email] = User(
        email=email,
        password_hash=hash_password(password),
        first_name=(first_name or "").strip(),
        last_name=(last_name or "").strip(),
    )
    return jsonify({"ok": True}), 201

def forgot_password(email: str):
    email = norm_email(email)
    user = users.get(email)
    if user:
        raw = create_reset_token(user.email)
        print(f"[DEV] reset link: http://localhost:4200/auth/reset-password?token={raw}")
    return jsonify({"ok": True}), 200

def reset_password(token: str, new_password: str):
    if not (token or "").strip() or not (new_password or ""):
        return jsonify({"message": "Token et mot de passe requis"}), 400

    email = consume_reset_token(token.strip())
    if not email:
        return jsonify({"message": "Lien invalide ou expiré"}), 400

    user = users.get(norm_email(email))
    if not user:
        return jsonify({"message": "Lien invalide ou expiré"}), 400

    user.password_hash = hash_password(new_password)
    return jsonify({"ok": True}), 200
