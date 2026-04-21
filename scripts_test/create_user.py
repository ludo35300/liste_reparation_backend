import sys
import os
import getpass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()   # ← AVANT create_app

from app import create_app

app = create_app()

def main():
    print("=" * 40)
    print("   Créer un utilisateur")
    print("=" * 40)

    email      = input("Email       : ").strip()
    first_name = input("Prénom      : ").strip()
    last_name  = input("Nom         : ").strip()
    password   = getpass.getpass("Mot de passe: ")
    confirm    = getpass.getpass("Confirmer   : ")

    if not email or not password:
        print("❌ Email et mot de passe requis.")
        sys.exit(1)

    if password != confirm:
        print("❌ Les mots de passe ne correspondent pas.")
        sys.exit(1)

    if len(password) < 4:
        print("❌ Mot de passe trop court (min 4 caractères).")
        sys.exit(1)

    with app.app_context():
        from app.security.passwords import hash_password
        from app.repositories.database import create_user, get_user_by_email, norm_email

        email = norm_email(email)

        if get_user_by_email(email):
            print(f"❌ L'email {email} est déjà utilisé.")
            sys.exit(1)

        create_user(email, hash_password(password), first_name, last_name)
        print(f"✅ Utilisateur '{first_name} {last_name}' <{email}> créé avec succès.")

if __name__ == '__main__':
    main()