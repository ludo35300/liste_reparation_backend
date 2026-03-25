# app/security/passwords.py
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Paramètres proches des recommandations OWASP (à ajuster selon machine) [web:102]
ph = PasswordHasher(
    time_cost=2,
    memory_cost=19 * 1024,  # KiB (~19 MiB)
    parallelism=1,
)

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, stored: str) -> bool:
    try:
        return ph.verify(stored, password)
    except VerifyMismatchError:
        return False

def needs_rehash(stored: str) -> bool:
    return ph.check_needs_rehash(stored)
