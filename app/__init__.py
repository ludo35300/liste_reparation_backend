# app/__init__.py
# ─────────────────────────────────────────────────────────────────────────────
# Point d'entrée de l'application : pattern Application Factory.
#
# create_app() permet de :
#   - créer plusieurs instances de l'app (tests, prod) sans conflit global
#   - injecter une configuration différente selon l'environnement
#   - éviter les imports circulaires entre modules
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
from .extensions import jwt, limiter, db, migrate, ma


def create_app(config=None):
    """Crée et configure l'application Flask.

    Args:
        config: Objet de configuration optionnel. Utilisé principalement
                dans les tests (ex: TestConfig) pour surcharger DevConfig/ProdConfig.

    Returns:
        Une instance Flask configurée et prête à servir les requêtes.
    """
    # Charge les variables d'environnement depuis le fichier .env
    # (doit être appelé avant app.config.from_object pour que os.getenv() fonctionne)
    load_dotenv()

    app = Flask(__name__)

    # ProxyFix : corrige les headers IP/protocole quand l'app est derrière un reverse proxy (Nginx).
    # x_for=1 : lit X-Forwarded-For (IP du client réel, utile pour le rate limiting par IP)
    # x_proto=1 : lit X-Forwarded-Proto (https) pour que JWT_COOKIE_SECURE fonctionne correctement
    # x_host=1, x_prefix=1 : reconstruction correcte de l'URL complète
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_prefix=1,
    )

    # Sélection automatique de la configuration selon l'environnement :
    #   FLASK_ENV=production  → ProdConfig (JWT_COOKIE_SECURE=True, JWT_SECRET_KEY obligatoire)
    #   (défaut)              → DevConfig
    app.config.from_object(ProdConfig if os.getenv("FLASK_ENV") == 'production' else DevConfig)

    # Permet de surcharger la config depuis l'extérieur (tests, scripts custom)
    if config is not None:
        app.config.from_object(config)

    # ── Gestionnaires d'erreurs globaux ─────────────────────────────────────────────

    @app.errorhandler(JWTExtendedException)
    def handle_jwt_error(e):
        """Capture toutes les exceptions JWT (token absent, expiré, invalide)
        et retourne une réponse JSON homogène 401."""
        return api_error('Non authentifié', 401, code='AUTH_REQUIRED')

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        """Capture les erreurs de validation Marshmallow levées lors du schema.load()
        et retourne le détail des champs invalides en 422."""
        return api_error('Données invalides', 422, code='VALIDATION_ERROR', details=e.messages)

    @app.errorhandler(429)
    def ratelimit_handler(e):
        """Capture les dépassements de rate limit (Flask-Limiter).
        Retry-After indique au client combien de secondes attendre avant de réessayer."""
        resp = jsonify({"message": "Trop de tentatives", "code": "RATE_LIMITED"})
        resp.status_code = 429
        resp.headers['Retry-After'] = '60'
        return resp

    # ── Initialisation des extensions ───────────────────────────────────────────────
    # L'ordre est important : CORS avant JWT pour que les headers prévols soient traités
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    jwt.init_app(app)
    limiter.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    # ── Pré-chargement des modèles SQLAlchemy ──────────────────────────────────────
    with app.app_context():
        # Import centralisé de TOUS les modèles dans le contexte applicatif.
        # Indispensable pour qu'Alembic (flask db migrate) détecte les tables
        # et génère les migrations correctement.
        # noqa: F401 → les imports sont volontaires même s'ils semblent inutilisés ici.
        from app.models import (  # noqa: F401
            Marque, Modele, modele_piece_refs,
            Machine, PieceRef,
            Reparation, PieceChangee,
            User, PasswordResetToken
        )

    # ── Enregistrement des Blueprints (routes) ────────────────────────────────────
    # Les imports sont faits ici (et non en haut du fichier) pour éviter les
    # imports circulaires : les contrôleurs importent db/extensions qui
    # sont définis dans ce même module.
    from .auth.routes                         import auth_bp
    from .controllers.user_controller         import user_bp
    from .controllers.machines_controller     import machines_bp
    from .controllers.reparations_controller  import reparations_bp
    from .controllers.statistiques_controller import stats_bp
    from .controllers.references_controller   import references_bp
    from .controllers.actions_controller      import actions_bp
    from .ocr.routes                          import ocr_bp

    app.register_blueprint(auth_bp,         url_prefix='/api/auth')
    app.register_blueprint(user_bp,         url_prefix='/api')
    app.register_blueprint(machines_bp,     url_prefix='/api')
    app.register_blueprint(reparations_bp,  url_prefix='/api')
    app.register_blueprint(stats_bp,        url_prefix='/api')
    app.register_blueprint(references_bp,   url_prefix='/api')
    app.register_blueprint(actions_bp,      url_prefix='/api')
    app.register_blueprint(ocr_bp,          url_prefix='/api')

    return app
