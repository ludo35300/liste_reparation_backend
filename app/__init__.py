from flask import Flask, jsonify, make_response
from flask_cors import CORS

from .config import DevConfig
from .extensions import jwt, limiter
from flask_jwt_extended.exceptions import JWTExtendedException
from .http.errors import api_error

def create_app():
    app = Flask(__name__)
    
    @app.errorhandler(JWTExtendedException)
    def handle_jwt_error(e):
        # Ex: missing CSRF header, token expired, etc.
        return api_error("Non authentifié", 401, code="AUTH_REQUIRED")
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        resp = jsonify({
            "message": "Trop de tentatives, réessaie plus tard",
            "code": "RATE_LIMITED",
        })
        resp.status_code = 429
        resp.headers["Retry-After"] = "60"
        return resp
    
    app.config.from_object(DevConfig)

    # Cookies cross-origin => origin explicite + credentials (pas '*') [web:86]
    CORS(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True)

    jwt.init_app(app)
    limiter.init_app(app)

    from .auth.controller import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    from .user.controller import user_bp
    app.register_blueprint(user_bp, url_prefix="/api")

    return app