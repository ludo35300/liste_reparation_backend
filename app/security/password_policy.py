# app/security/password_policy.py
def validate_password(pwd: str) -> list[str]:
    pwd = pwd or ""
    errors: list[str] = []

    # Demo: minimum raisonnable; OWASP/NIST insistent surtout sur la longueur.
    if len(pwd) < 10:
        errors.append("Mot de passe trop court (min 10).")

    # Max >= 64 recommandé pour passphrases.
    if len(pwd) > 64:
        errors.append("Mot de passe trop long (max 64 en démo).")

    # Pas de règles de complexité imposées ici (évite les règles inutiles).
    return errors
