import os
from pathlib import Path

STATUTS_REPARATION_VALIDES = ('en_reparation', 'termine')
STATUTS_VALIDES = ('en_attente', 'en_reparation', 'pret', 'termine')
LOGO_FOLDER = Path(os.getenv("LOGO_FOLDER", "app/static/logos"))
