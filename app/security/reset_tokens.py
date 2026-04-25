import secrets, hashlib
from datetime import datetime, timedelta, timezone


def generate_raw_token() -> str:
    """Génère un token brut aléatoire."""
    return secrets.token_urlsafe(32)


def hash_token(raw: str) -> str:
    """Hash le token avant stockage en BDD."""
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def token_expiry(ttl_seconds: int = 30 * 60) -> datetime:
    """Retourne la date d'expiration."""
    return datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)


def is_token_valid(expires: datetime) -> bool:
    """Vérifie que le token n'est pas expiré."""
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) < expires