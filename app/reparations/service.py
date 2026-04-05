from sqlalchemy import func

from app.extensions import db
from app.models.reference import MachineTypeRef, PieceRef
from app.models.reparation import Reparation
from app.models.piece_changee import PieceChangee
from difflib import get_close_matches
from datetime import datetime


def creer_reparation(data: dict) -> Reparation:
    date_rep = data['date_reparation']
    if isinstance(date_rep, str):
        date_rep = datetime.strptime(date_rep, '%d/%m/%Y').date()

    rep = Reparation(
        numero_serie    = data['numero_serie'].strip().upper(),
        machine_type    = correct_machine_type(data.get('machine_type', '')),
        technicien      = data.get('technicien', ''),
        date_reparation = date_rep,
        notes           = data.get('notes', '')
    )
    db.session.add(rep)
    db.session.flush()

    for p in data.get('pieces', []):
        db.session.add(PieceChangee(
            reparation_id = rep.id,
            ref_piece     = correct_piece_ref(p['ref_piece']),
            designation   = p.get('designation', ''),
            quantite      = int(p.get('quantite', 1))
        ))

    db.session.commit()
    return rep


def get_historique(numero_serie: str) -> list:
    return (
        Reparation.query
        .filter_by(numero_serie=numero_serie.strip().upper())
        .order_by(Reparation.date_reparation.desc())
        .all()
    )


def get_by_id(rep_id: int) -> Reparation:
    return db.get_or_404(Reparation, rep_id)


def supprimer(rep_id: int) -> None:
    rep = db.get_or_404(Reparation, rep_id)
    db.session.delete(rep)
    db.session.commit()


def correct_machine_type(raw: str) -> str:
    """Retourne la meilleure correspondance fuzzy ou la valeur brute."""
    if not raw:
        return raw
    labels = [r.label for r in MachineTypeRef.query.all()]
    if not labels:
        return raw
    matches = get_close_matches(raw, labels, n=1, cutoff=0.75)
    return matches[0] if matches else raw


def correct_piece_ref(raw: str) -> str:
    """Corrige une référence pièce par fuzzy matching."""
    if not raw:
        return raw
    refs = [r.ref_piece for r in PieceRef.query.all()]
    if not refs:
        return raw
    matches = get_close_matches(raw, refs, n=1, cutoff=0.80)
    return matches[0] if matches else raw


def suggest_machine_types(query: str, n: int = 5) -> list[str]:
    """Retourne jusqu'à n suggestions fuzzy pour un type de machine."""
    labels = [r.label for r in MachineTypeRef.query.all()]
    if not labels:
        return []
    return get_close_matches(query, labels, n=n, cutoff=0.5)


def suggest_piece_refs(query: str, n: int = 5) -> list[str]:
    """Retourne jusqu'à n suggestions fuzzy pour une référence pièce."""
    refs = [r.ref_piece for r in PieceRef.query.all()]
    if not refs:
        return []
    return get_close_matches(query, refs, n=n, cutoff=0.5)

def get_machines():
    """Retourne toutes les machines de référence."""
    machines = MachineTypeRef.query.order_by(MachineTypeRef.marque).all()
    return [
        {
            'id':           m.id,
            'marque':       m.marque,
            'modele':       m.modele,
            'type_machine': m.type_machine,
            'label':        m.label,  # @property Python — OK ici car pas dans SQL
        }
        for m in machines
    ]