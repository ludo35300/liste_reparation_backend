# app/stats/routes.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.services import statistiques_service as svc

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/stats', methods=['GET'])
@jwt_required()
def stats():
    return jsonify(svc.get_stats_globales()), 200