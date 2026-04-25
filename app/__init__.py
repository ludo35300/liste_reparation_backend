from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended.exceptions import JWTExtendedException
from .config import DevConfig, ProdConfig
import os
from .extensions import jwt, limiter, db, migrate, ma
from .core.errors import api_error
from dotenv import load_dotenv


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(ProdConfig if os.getenv("FLASK_ENV") == 'production' else DevConfig)

    @app.errorhandler(JWTExtendedException)
    def handle_jwt_error(e):
        return api_error('Non authentifié', 401, code='AUTH_REQUIRED')

    @app.errorhandler(429)
    def ratelimit_handler(e):
        resp = jsonify({"message": "Trop de tentatives", "code": "RATE_LIMITED"})
        resp.status_code = 429
        resp.headers['Retry-After'] = '60'
        return resp

    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    jwt.init_app(app)
    limiter.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    with app.app_context():
        # Import centralisé — Alembic voit tous les modèles via __init__.py
        from app.models import (  # noqa: F401
            Marque, Modele, modele_piece_refs,
            Machine, PieceRef,
            Reparation, PieceChangee,
            User, PasswordResetToken
        )

    from .auth.routes        import auth_bp
    from .controllers.user_controller        import user_bp
    from .controllers.machines_controller  import machines_bp
    from .controllers.reparations_controller import reparations_bp
    from .controllers.statistiques_controller       import stats_bp
    from .ocr.routes         import ocr_bp
    from .controllers.references_controller  import references_bp

    app.register_blueprint(auth_bp,        url_prefix='/api/auth')
    app.register_blueprint(user_bp,        url_prefix='/api')
    app.register_blueprint(machines_bp,    url_prefix='/api')
    app.register_blueprint(reparations_bp, url_prefix='/api')
    app.register_blueprint(stats_bp,       url_prefix='/api')
    app.register_blueprint(ocr_bp,         url_prefix='/api')
    app.register_blueprint(references_bp,  url_prefix='/api')

    return app
