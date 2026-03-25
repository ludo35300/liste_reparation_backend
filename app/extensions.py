from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow

jwt     = JWTManager()
limiter = Limiter(key_func=get_remote_address, default_limits=[])
db      = SQLAlchemy()
migrate = Migrate()
ma      = Marshmallow()