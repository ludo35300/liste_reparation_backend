import mimetypes

from flask import Blueprint, send_from_directory
from flask_jwt_extended import jwt_required


images_bp  = Blueprint('images', __name__)



@images_bp.get("/static/logos/<path:filename>")
@jwt_required()
def serve_logo(filename):
    mimetype, _ = mimetypes.guess_type(filename)
    return send_from_directory(
        directory="/app/static/logos",
        path=filename,
        mimetype=mimetype or "application/octet-stream"
    )