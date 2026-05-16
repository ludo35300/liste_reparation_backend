# app/extensions.py
# ─────────────────────────────────────────────────────────────────────────────
# Instanciation des extensions Flask sans application (pattern Application Factory).
#
# Toutes les extensions sont créées ici SANS app, puis liées à l'application
# dans create_app() via extension.init_app(app).
# Cela permet de réutiliser les extensions dans les tests sans conflit.
# ─────────────────────────────────────────────────────────────────────────────
import os

from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow

# Gestionnaire JWT : gère la création, la validation et le rafraîchissement
# des tokens d'accès et de rafraîchissement (stockés en cookies HttpOnly).
jwt = JWTManager()

# Rate limiter : protège les routes sensibles contre le brute-force et le spam.
# - key_func       : identifie le client par son IP réelle (prise en compte du reverse proxy via ProxyFix)
# - default_limits : aucune limite globale par défaut ; les limites sont déclarées route par route
# - storage_uri    : mémoire en dév (non partagée entre workers) ;
#                    en production, définir RATELIMIT_STORAGE_URI=redis://... dans le .env
storageuri = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    storage_uri=storageuri
)

# ORM SQLAlchemy : mapping objet-relationnel vers PostgreSQL (ou SQLite en test).
# La connexion est configurée via SQLALCHEMY_DATABASE_URI dans config.py.
db = SQLAlchemy()

# Flask-Migrate : wrapper Alembic pour gérer les migrations de schéma.
# Commandes : flask db init / migrate / upgrade
migrate = Migrate()

# Marshmallow : sérialisation / désérialisation et validation des données
# entre les requêtes JSON et les objets SQLAlchemy.
ma = Marshmallow()
