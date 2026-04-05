import os
import secrets 

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

class DevConfig:
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_CSRF_IN_COOKIES = True

    JWT_COOKIE_SECURE = False          # True en prod (HTTPS)
    JWT_COOKIE_SAMESITE = "Lax"        # potentiellement "Strict" si même-site

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32)) 

    JWT_ACCESS_COOKIE_PATH = "/api/"
    JWT_REFRESH_COOKIE_PATH = "/api/auth/refresh"

    JWT_ACCESS_TOKEN_EXPIRES = 10 * 60
    JWT_REFRESH_TOKEN_EXPIRES = 7 * 24 * 3600

    CORS_ORIGINS = ["http://localhost:4200"]

    # ── Base de données ───────────────────────────────────
    SQLALCHEMY_DATABASE_URI           = 'sqlite:///' + os.path.join(BASE_DIR, 'reparations_dev.db')
    SQLALCHEMY_TRACK_MODIFICATIONS    = False

    # ── Upload ────────────────────────────────────────────
    MAX_CONTENT_LENGTH  = 32 * 1024 * 1024   # 32 Mo
    JSON_ENSURE_ASCII   = False

class ProdConfig(DevConfig):
    JWT_COOKIE_SECURE           = True
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32)) 
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost/reparations_db'
    )
    CORS_ORIGINS                = os.getenv('CORS_ORIGINS', 'http://localhost:4200').split(',')