# app/utils/responses.py
from flask import jsonify


def api_error(message: str, status: int = 400,
              code: str | None = None, details=None):
    payload = {"message": message}
    if code:
        payload["code"] = code
    if details is not None:
        payload["details"] = details
    return jsonify(payload), status


def api_success(data=None, message: str | None = None, status: int = 200):
    """Réponse succès homogène — utile pour les endpoints non-CRUD."""
    payload = {}
    if message:
        payload["message"] = message
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status