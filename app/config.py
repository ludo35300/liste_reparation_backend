# app/config.py
# ─────────────────────────────────────────────────────────────────────────────
# Configuration par environnement.
# Chaque classe hérite de la précédente pour ne surcharger que les différences.
#
# Sélection automatique dans create_app() :
#   FLASK_ENV=production  → ProdConfig
#   (défaut)              → DevConfig
#
# Variables d'environnement attendues dans le .env :
#   DATABASE_URL        URL PostgreSQL (ou SQLite pour les tests)
#   JWT_SECRET_KEY      Clé secrète JWT  (OBLIGATOIRE en production)
#   CORS_ORIGINS        Liste d'origines séparées par des virgules
#   RATELIMIT_STORAGE_URI  URI Redis pour le rate limiter (optionnel, défaut : mémoire)
# ─────────────────────────────────────────────────────────────────────────────
import os
import secrets

# Chemin racine du projet (utilisable pour construire des chemins absolus)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class DevConfig:
    # ── JWT / Auth ────────────────────────────────────────────────────────────
    # Les tokens sont stockés dans des cookies HttpOnly (pas dans localStorage)
    JWT_TOKEN_LOCATION          = ["cookies"]
    JWT_COOKIE_CSRF_PROTECT     = True   # Double-submit cookie CSRF activé
    JWT_CSRF_IN_COOKIES         = True
    JWT_COOKIE_SECURE           = False  # False en dev (HTTP), True en prod (HTTPS)
    JWT_COOKIE_SAMESITE         = "Lax"  # Lax = OK pour navigation normale, bloque les requêtes cross-site

    # En dev : clé aléatoire si absent du .env (invalide les tokens au redémarrage — normal en dev)
    # En prod : la clé DOIT être fixée dans le .env (voir ProdConfig)
    JWT_SECRET_KEY              = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))

    # Restreindre les cookies JWT aux seuls chemins qui en ont besoin
    JWT_ACCESS_COOKIE_PATH      = "/api/"             # Cookie access token valable sur tout /api/
    JWT_REFRESH_COOKIE_PATH     = "/api/auth/refresh"  # Cookie refresh uniquement sur la route de renouvellement

    # Durées de vie des tokens
    JWT_ACCESS_TOKEN_EXPIRES    = 1 * 24 * 3600  # 1 jour
    JWT_REFRESH_TOKEN_EXPIRES   = 7 * 24 * 3600  # 7 jours

    # ── CORS ─────────────────────────────────────────────────────────────────
    CORS_ORIGINS                = ["http://localhost:4200"]  # Frontend Angular en dev

    # ── Base de données ───────────────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI     = os.getenv('DATABASE_URL')
    # Désactive le système de tracking d'événements SQLAlchemy (deprecated, consomme de la mémoire)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── Upload / Divers ───────────────────────────────────────────────────────
    MAX_CONTENT_LENGTH          = 32 * 1024 * 1024  # Taille max des uploads : 32 Mo

    RATELIMIT_ENABLED           = True
    RATELIMIT_STORAGE_URI       = "memory://"
    RATELIMIT_HEADERS_ENABLED   = True
    RATELIMIT_STRATEGY          = "fixed-window"


class ProdConfig(DevConfig):
    # ── JWT ───────────────────────────────────────────────────────────────────
    JWT_COOKIE_SECURE           = True  # HTTPS obligatoire en production

    # En production, JWT_SECRET_KEY DOIT être définie dans les variables d'environnement.
    # Si elle est absente, on lève une erreur immédiatement au démarrage (fail-fast).
    JWT_SECRET_KEY              = os.environ["JWT_SECRET_KEY"]

    # ── Base de données ───────────────────────────────────────────────────────
    # Redéclaré explicitement (même valeur que DevConfig, mais sémantiquement clair)
    SQLALCHEMY_DATABASE_URI     = os.getenv('DATABASE_URL')

    # ── CORS ─────────────────────────────────────────────────────────────────
    # En prod, les origines autorisées sont définies dans le .env sous forme de liste séparée par des virgules
    # Exemple : CORS_ORIGINS=https://mon-app.fr,https://www.mon-app.fr
    CORS_ORIGINS                = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()]

   # RATELIMIT_ENABLED           = True
   # RATELIMIT_STORAGE_URI       = os.getenv("RATELIMIT_STORAGE_URI", "redis://redis:6379/0")
  #  RATELIMIT_HEADERS_ENABLED   = True
  #  RATELIMIT_STRATEGY          = "fixed-window"


class TestConfig(DevConfig):
    # ── Configuration de test (pytest) ────────────────────────────────────────
    TESTING                     = True
    SQLALCHEMY_DATABASE_URI     = "sqlite:///:memory:"  # Base en mémoire, isolée par test
    JWT_COOKIE_CSRF_PROTECT     = False  # Désactivé pour simplifier les appels de test
    JWT_COOKIE_SECURE           = False
    RATELIMIT_ENABLED           = False  # Pas de rate limiting pendant les tests
    WTF_CSRF_ENABLED            = False
    JWT_TOKEN_LOCATION          = ["headers"]  # Plus simple à injecter dans les tests que les cookies
    RATELIMIT_ENABLED           = False
