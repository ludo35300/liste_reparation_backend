# scripts/reset_data.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.reparation import Reparation
from app.models.piece_changee import PieceChangee
from app.models.reference import MachineTypeRef, PieceRef, machine_piece_refs

app = create_app()

with app.app_context():
    print("⚠️  Réinitialisation des données métier...")

    # Ordre important : enfants avant parents (FK)
    db.session.execute(machine_piece_refs.delete())  # table pivot
    PieceChangee.query.delete()
    Reparation.query.delete()
    PieceRef.query.delete()
    MachineTypeRef.query.delete()

    db.session.commit()
    print("✅ Données supprimées — utilisateurs conservés.")