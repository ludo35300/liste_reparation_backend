# app/extensions.py
# ─────────────────────────────────────────────────────────────────────────────
# Instanciation des extensions Flask sans application (pattern Application Factory).
#
# Toutes les extensions sont créées ici SANS app, puis liées à l'application
# dans create_app() via extension.init_app(app).
# Cela permet de réutiliser les extensions dans les tests sans conflit.
# ─────────────────────────────────────────────────────────────────────────────

from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow

# ── JWT ──────────────────────────────────────────────────────────────────────
# Gère la création/lecture/validation des tokens JWT (stockés en cookies HttpOnly).
jwt = JWTManager()

# ── Rate limiter ─────────────────────────────────────────────────────────────
# Protège les routes contre le brute-force et le spam.
# - key_func       : identifie le client par son IP réelle (prise en compte du reverse proxy via ProxyFix)
# - default_limits : aucune limite globale par défaut ; les limites sont déclarées route par route
# - storage_uri    : mémoire en dév (non partagée entre workers) ;
#                    en production, définir RATELIMIT_STORAGE_URI=redis://... dans le .env
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[]
)

# ── Base de données ──────────────────────────────────────────────────────────
# La connexion est configurée via SQLALCHEMY_DATABASE_URI dans config.py.
db = SQLAlchemy()

# ── Migrations Alembic ───────────────────────────────────────────────────────
# Commandes : flask db init / migrate / upgrade
migrate = Migrate()

# ── Sérialisation / validation ───────────────────────────────────────────────
ma = Marshmallow()
