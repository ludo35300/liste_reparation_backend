import time, secrets, hashlib
from ..repositories.memory import reset_db

def create_reset_token(email: str, ttl_seconds: int = 30 * 60) -> str:
    raw = secrets.token_urlsafe(32)
    th = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    reset_db[th] = {"email": email, "exp": int(time.time()) + ttl_seconds, "used": False}
    return raw

def consume_reset_token(raw: str) -> str | None:
    th = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    row = reset_db.get(th)
    now = int(time.time())
    if not row or row["used"] or row["exp"] <= now:
        return None
    row["used"] = True
    return row["email"]
