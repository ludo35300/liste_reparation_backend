# app/models/__init__.py
# Import dans l'ordre des dépendances : parent → enfant

from .user          import User           # pas de FK vers d'autres modèles
from .reference     import MachineTypeRef, PieceRef  # pas de FK vers d'autres modèles
from .reparation    import Reparation     # FK → users + machine_type_refs
from .piece_changee import PieceChangee   # FK → reparations + piece_refs

__all__ = ['User', 'MachineTypeRef', 'PieceRef', 'Reparation', 'PieceChangee']