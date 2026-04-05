from flask import jsonify


def api_error(message: str, status: int = 400, code: str | None = None, details=None):
    payload = {"message": message}
    if code:
        payload["code"] = code
    if details is not None:
        payload["details"] = details
    return jsonify(payload), status