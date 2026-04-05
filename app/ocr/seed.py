# app/ocr/seed.py
from app.extensions import db
from app.models.reference import MachineTypeRef, PieceRef

PIECES_INITIALES = {
    "40100": "BAC A GRAINS COMPLET",
    "40101": "COUVERCLE BAC A GRAIN",
    "40701": "COUVERCLE DISTRIBUTEUR",
    "40702": "BANDE PLEXI INTERIEUR",
    "40725": "COMPTEUR TOTALISEUR 5 CHIFFRES",
    "40726": "RESSORT RAPPEL COMPTEUR",
    "40745": "BUTEE DIAM 12H 7,5",
    "40746": "BUTEE DIAM 12H4",
    "00001B": "PAIRE DE MEULES",
    "40662B": "RECUPERATEUR DE CAFE",
    "40759A": "COUVERCLE CARTER AUTO",
    "40797A": "CARTER AUTOMATIQUE",
    "40783": "CROISILLON INTERMEDIAIRE",
    "40782": "RACLETTE DE CROISILLONS",
    "40791": "RONDELLE ONDULEE DOSEUR",
    "40781": "CROISILLON SUPERIEUR",
    "40790": "BRISE MOTTE",
    "40753A": "LANGUETTE CAOUTCHOUC",
    "40754A": "PLAQUETTE DE RETENUE LANGUETTE",
    "40609": "CONDENSATEUR 100MF",
    "55841C": "TASSEUR DIAM 57MM",
    "40625": "CORDON D ALIMENTATION AVEC PRISE EUR",
    "40206": "VIS DE FIXATION MEULE (M4 X10)",
}

MACHINES_INITIALES = [
    "MOULIN SANTOS 40AN",
    "MOULIN SANTOS 55",
]

def seed_referentiels():
    ajouts_pieces = ajouts_machines = 0
    for ref, designation in PIECES_INITIALES.items():
        if not PieceRef.query.filter(
            db.func.upper(PieceRef.ref_piece) == ref.upper()
        ).first():
            db.session.add(PieceRef(ref_piece=ref.upper(), designation=designation))
            ajouts_pieces += 1
    for label in MACHINES_INITIALES:
        if not MachineTypeRef.query.filter(
            db.func.upper(MachineTypeRef.label) == label.upper()
        ).first():
            db.session.add(MachineTypeRef(label=label.upper()))
            ajouts_machines += 1
    db.session.commit()
    print(f"[Seed] {ajouts_pieces} pièces, {ajouts_machines} machines ajoutées.")