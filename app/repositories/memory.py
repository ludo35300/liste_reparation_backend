from dataclasses import dataclass
from typing import Dict
import hashlib, hmac

from app.security.passwords import hash_password

@dataclass
class User:
    email: str
    password_hash: str
    first_name: str
    last_name: str

def norm_email(email: str) -> str:
    return (email or "").strip().lower()

def hash_pwd_dev(p: str) -> str:
    return hashlib.sha256(p.encode("utf-8")).hexdigest()

def verify_pwd_dev(p: str, ph: str) -> bool:
    return hmac.compare_digest(hash_pwd_dev(p), ph)

users: Dict[str, User] = {}
users[norm_email("admin@test.com")] = User("admin@test.com", hash_password("1234"), "Ludovic", "Randu")

reset_db: Dict[str, dict] = {}  # token_hash -> {email, exp, used}