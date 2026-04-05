from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended.exceptions import JWTExtendedException
from .config import DevConfig
from .extensions import jwt, limiter, db, migrate, ma
from .http.errors import api_error
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevConfig)

    # ── Gestion des erreurs ───────────────────────────────
    @app.errorhandler(JWTExtendedException)
    def handle_jwt_error(e):
        return api_error('Non authentifié', 401, code='AUTH_REQUIRED')

    @app.errorhandler(429)
    def ratelimit_handler(e):
        resp = jsonify({"message": "Trop de tentatives", "code": "RATE_LIMITED"})
        resp.status_code = 429
        resp.headers['Retry-After'] = '60'
        return resp

    # ── Extensions ────────────────────────────────────────
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    jwt.init_app(app)
    limiter.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    # ── Blueprints ────────────────────────────────────────
    from .auth.controller        import auth_bp
    from .user.controller        import user_bp
    from .reparations.controller import reparations_bp
    from .stats.controller       import stats_bp
    from .ocr.controller         import ocr_bp
    from .references.controller import references_bp


    app.register_blueprint(auth_bp,        url_prefix='/api/auth')
    app.register_blueprint(user_bp,        url_prefix='/api')
    app.register_blueprint(reparations_bp, url_prefix='/api')
    app.register_blueprint(stats_bp,       url_prefix='/api')
    app.register_blueprint(ocr_bp,         url_prefix='/api')
    app.register_blueprint(references_bp, url_prefix='/api')

    return app