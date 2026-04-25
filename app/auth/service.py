import logging

from flask import jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies,
)

from app.security.passwords import verify_password, hash_password
from app.security.reset_tokens import (
    generate_raw_token, hash_token, token_expiry, is_token_valid,
)
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

def login_user(email: str, password: str):
    user = UserRepository.get_by_email(UserRepository.norm_email(email))
    if not user or not verify_password(password or '', user.password_hash):
        return jsonify({"message": "Identifiants invalides"}), 401

    access  = create_access_token(identity=str(user.id))
    refresh = create_refresh_token(identity=str(user.id))

    resp = jsonify({
        "ok": True,
        "user": {
            "email":     user.email,
            "firstName": user.first_name,
            "lastName":  user.last_name,
        }
    })
    set_access_cookies(resp, access)
    set_refresh_cookies(resp, refresh)
    return resp, 200


def refresh_access_token():
    user_id    = get_jwt_identity()
    new_access = create_access_token(identity=user_id)
    resp       = jsonify({"ok": True})
    set_access_cookies(resp, new_access)
    return resp, 200


def logout_user():
    resp = jsonify({"ok": True})
    unset_jwt_cookies(resp)
    return resp, 200


def register_user(email: str, password: str,
                  first_name: str, last_name: str):
    email = UserRepository.norm_email(email)
    if not email or not (password or ''):
        return jsonify({"message": "Email et mot de passe requis"}), 400
    if UserRepository.get_by_email(email):
        return jsonify({"message": "Email déjà utilisé"}), 409

    UserRepository.create(email, hash_password(password),
                          first_name or '', last_name or '')
    return jsonify({"ok": True}), 201


def forgot_password(email: str):
    user = UserRepository.get_by_email(UserRepository.norm_email(email))
    if user:
        raw        = generate_raw_token()
        token_hash = hash_token(raw)
        expires    = token_expiry(30 * 60)
        UserRepository.save_reset_token(user, token_hash, expires)
        logger.debug("reset link: http://localhost:4200/auth/reset-password?token=%s", raw)
    return jsonify({"ok": True}), 200


def reset_password(token: str, new_password: str):
    if not (token or '').strip() or not (new_password or ''):
        return jsonify({"message": "Token et mot de passe requis"}), 400

    token_hash = hash_token(token.strip())
    user       = UserRepository.get_by_reset_token(token_hash)

    if not user or not user.reset_token or not is_token_valid(user.reset_token.expires_at):
        return jsonify({"message": "Lien invalide ou expiré"}), 400

    UserRepository.update_password(user, hash_password(new_password))
    UserRepository.clear_reset_token(user)
    return jsonify({"ok": True}), 200