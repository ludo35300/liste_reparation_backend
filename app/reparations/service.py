from app.extensions import db
from app.models.reparation import Reparation
from app.models.piece_changee import PieceChangee
from datetime import datetime

def creer_reparation(data: dict) -> Reparation:
    date_rep = data['date_reparation']
    if isinstance(date_rep, str):
        date_rep = datetime.strptime(date_rep, '%d/%m/%Y').date()

    rep = Reparation(
        numero_serie    = data['numero_serie'].strip().upper(),
        machine_type    = data.get('machine_type', ''),
        technicien      = data.get('technicien', ''),
        date_reparation = date_rep,
        notes           = data.get('notes', '')
    )
    db.session.add(rep)
    db.session.flush()

    for p in data.get('pieces', []):
        db.session.add(PieceChangee(
            reparation_id = rep.id,
            ref_piece     = p['ref_piece'],
            designation   = p.get('designation', ''),
            quantite      = int(p.get('quantite', 1))
        ))

    db.session.commit()
    return rep

def get_historique(numero_serie: str) -> list:
    return Reparation.query \
        .filter_by(numero_serie=numero_serie.upper()) \
        .order_by(Reparation.date_reparation.desc()) \
        .all()

def get_by_id(rep_id: int) -> Reparation:
    return db.get_or_404(Reparation, rep_id)

def supprimer(rep_id: int):
    rep = db.get_or_404(Reparation, rep_id)
    db.session.delete(rep)
    db.session.commit()