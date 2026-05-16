# app/__init__.py
# ─────────────────────────────────────────────────────────────────────────────
# Point d'entrée principal de l'application Flask.
#
# Rôle de ce fichier :
# - créer l'application
# - charger la configuration selon l'environnement
# - initialiser les extensions
# - enregistrer les handlers d'erreur
# - enregistrer les blueprints
#
# ─────────────────────────────────────────────────────────────────────────────

import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended.exceptions import JWTExtendedException
from marshmallow import ValidationError
from werkzeug.middleware.proxy_fix import ProxyFix

from app.utils.responses import api_error
from .config import DevConfig, ProdConfig
from .extensions import db, jwt, limiter, ma, migrate


def register_error_handlers(app: Flask) -> None:
    """Enregistre les gestionnaires d'erreurs globaux de l'application."""

    @app.errorhandler(JWTExtendedException)
    def handle_jwt_error(error):
        # Toute erreur JWT (absence, expiration, token invalide, mauvais type)
        # retourne une réponse uniforme.
        return api_error("Non authentifié", 401, code="AUTH_REQUIRED")

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        # Erreurs Marshmallow lors du load()/validate()
        return api_error(
            "Données invalides",
            422,
            code="VALIDATION_ERROR",
            details=error.messages,
        )

    @app.errorhandler(429)
    def handle_rate_limit(error):
        # Flask-Limiter peut fournir un Retry-After dynamique,
        # mais ici on garde une réponse homogène simple.
        response = jsonify({
            "message": "Trop de tentatives",
            "code": "RATE_LIMITED",
        })
        response.status_code = 429
        response.headers["Retry-After"] = "60"
        return response

def register_extensions(app: Flask) -> None:
    """Initialise toutes les extensions Flask."""

    jwt.init_app(app)
    limiter.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    # CORS doit être initialisé après app.config
    # supports_credentials=True est requis pour les cookies JWT.
    CORS(
        app,
        origins=app.config["CORS_ORIGINS"],
        supports_credentials=True,
    )

def register_blueprints(app: Flask) -> None:
    """Enregistre tous les blueprints API."""

    from .auth.routes import auth_bp
    from .controllers.actions_controller import actions_bp
    from .controllers.machines_controller import machines_bp
    from .controllers.references_controller import references_bp
    from .controllers.reparations_controller import reparations_bp
    from .controllers.statistiques_controller import stats_bp
    from .controllers.user_controller import user_bp
    from .ocr.routes import ocr_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api")
    app.register_blueprint(machines_bp, url_prefix="/api")
    app.register_blueprint(reparations_bp, url_prefix="/api")
    app.register_blueprint(stats_bp, url_prefix="/api")
    app.register_blueprint(ocr_bp, url_prefix="/api")
    app.register_blueprint(references_bp, url_prefix="/api")
    app.register_blueprint(actions_bp, url_prefix="/api")


def register_models() -> None:
    """Importe les modèles pour que Flask-Migrate/Alembic les voie bien."""

    from app.models import (
        Machine,
        Marque,
        Modele,
        PasswordResetToken,
        PieceChangee,
        PieceRef,
        Reparation,
        User,
        modele_piece_refs,
    )


def create_app(config=None) -> Flask:
    """Factory principale de l'application Flask."""

    load_dotenv()
    app = Flask(__name__)
    # ProxyFix ne doit être activé que si l'application est réellement
    # derrière un reverse proxy (Nginx, Traefik, etc.).
    # Ici on fait confiance à 1 proxy pour chaque header.
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_prefix=1,
    )

    # Choix de la configuration selon l'environnement
    env_config = ProdConfig if os.getenv("FLASK_ENV") == "production" else DevConfig
    app.config.from_object(env_config)

    # Permet d'injecter une config de test ou de surcharge depuis l'appelant
    if config is not None:
        app.config.from_object(config)

    register_error_handlers(app)
    register_extensions(app)
    register_blueprints(app)

    with app.app_context():
        register_models()

    return app