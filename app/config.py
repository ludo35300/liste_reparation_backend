import os
import secrets 

class DevConfig:
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_CSRF_IN_COOKIES = True

    JWT_COOKIE_SECURE = False          # True en prod (HTTPS)
    JWT_COOKIE_SAMESITE = "Lax"        # potentiellement "Strict" si même-site

    JWT_SECRET_KEY = secrets.token_hex(32)   # en prod: variable d'env
    # Dans ProdConfig
    # JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))

    JWT_ACCESS_COOKIE_PATH = "/api/"
    JWT_REFRESH_COOKIE_PATH = "/api/auth/refresh"

    JWT_ACCESS_TOKEN_EXPIRES = 10 * 60
    JWT_REFRESH_TOKEN_EXPIRES = 7 * 24 * 3600

    CORS_ORIGINS = ["http://localhost:4200"]