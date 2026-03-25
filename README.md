# 🔐 AuthModule Backend

> API d'authentification robuste et réutilisable construite avec **Flask**.
> Implémente le pattern **JWT (Access + Refresh Tokens)** stockés dans des **Cookies HttpOnly** sécurisés avec protection **CSRF** et **Rate Limiting**.

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-green.svg?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Development-orange.svg)]()

---

## ✨ Fonctionnalités Clés

- **Sécurité Maximale** :
  - **JWT dans Cookies HttpOnly** (pas de LocalStorage, protection XSS).
  - **Protection CSRF** via Double Submit Cookie.
  - **Double Token** : Access Token (court) + Refresh Token (long).
- **Rate Limiting** : Protection contre le Brute-Force via `Flask-Limiter`.
- **Gestion des Utilisateurs** : Inscription, Connexion, Profil (`/me`).
- **Flow Mot de Passe** : Hachage sécurisé (Argon2/Bcrypt) et workflow de réinitialisation (Forgot/Reset Password).
- **Architecture Modulaire** : Utilisation de Flask Blueprints.

## 🚀 Installation & Démarrage

### Prérequis
- Python 3.13+
- Git

### 1. Cloner le projet
```bash
git clone https://github.com/ludo35300/AuthModuleBack.git
cd AuthModuleBack
```

### 2. Environnement Virtuel
``` bash
# Linux / Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Installation des dépendances
```bash
pip install -r requirements.txt
```

### 4. Lancer le serveur (Mode Développement)
```bash
flask run
```

L'API sera accessible sur : http://localhost:5000

## ⚙️ Configuration (.env)
À la racine du projet, créez un fichier .env pour surcharger la configuration

```bash
# .env example

# Sécurité (Générer avec secrets.token_hex(32))
SECRET_KEY=votre_super_secret_key_flask
JWT_SECRET_KEY=votre_super_jwt_secret_key

# Base de données (Dev = SQLite/Memory, Prod = Postgres)
DATABASE_URL=postgresql://user:password@localhost/authdb

# Rate Limiting (Dev = Memory, Prod = Redis)
RATELIMIT_STORAGE_URI=redis://localhost:6379

# CORS (Frontend URL)
CORS_ORIGINS=http://localhost:4200
```

## 📡 Documentation API

Authentification

| Méthode | Endpoint                  | Auth Requise  | Description                              |
| ------- | ------------------------- | ------------- | ---------------------------------------- |
| POST    | /api/auth/register        | ❌             | Créer un nouveau compte                  |
| POST    | /api/auth/login           | ❌             | Connexion (Set Cookies Access & Refresh) |
| POST    | /api/auth/logout          | ✅             | Déconnexion (Supprime les cookies)       |
| POST    | /api/auth/refresh         | ✅ (Refresh)   | Obtenir un nouveau Access Token          |
| POST    | /api/auth/forgot-password | ❌             | Demander un lien de réinitialisation     |
| POST    | /api/auth/reset-password  | ❌ (Token URL) | Définir un nouveau mot de passe          |

Utilisateur

| Méthode | Endpoint | Auth Requise | Description                            |
| ------- | -------- | ------------ | -------------------------------------- |
| GET     | /api/me  | ✅ (Access)   | Récupérer les infos du profil connecté |

## 🛠️ Stack Technique
Framework : Flask

Auth : Flask-JWT-Extended

Sécurité : Flask-Limiter, Werkzeug (Security)

Base de données : Repository Pattern (In-Memory pour dev / Extensible SQL)

Frontend Associé : [AuthModuleFront (Angular)](https://github.com/ludo35300/AuthModuleFront)

## 🚧 Roadmap & Améliorations Futures
 Migration vers PostgreSQL (SQLAlchemy).

 Ajout de Tests Unitaires (Pytest).

 Containerisation Docker & Docker Compose (App + Redis + DB).

 Validation des entrées avec Marshmallow.


Ce projet est une démonstration technique d'un module d'authentification sécurisé.