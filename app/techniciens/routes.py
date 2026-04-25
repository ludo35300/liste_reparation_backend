from flask import Blueprint, jsonify
from app.repositories.database import get_all_users

techniciens_bp  = Blueprint('techniciens', __name__)

@techniciens_bp.get('/techniciens')
def get_techniciens():
    users = get_all_users()

    return jsonify([
        {
            'id': user.id,
            'email': user.email,
            'nom': f'{user.first_name} {user.last_name}'.strip(),
        }
        for user in users
    ])