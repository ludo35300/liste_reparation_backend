# app/reparations/service.py
from datetime import datetime

from app.extensions           import db
from app.models.reparation    import Reparation
from app.models.piece_changee import PieceChangee
from app.utils.fuzzy          import fuzzy_machine, fuzzy_piece


# ── Helpers internes ──────────────────────────────────────────
def _load_labels_machines() -> list:
    from app.models.reference import MachineTypeRef
    return [m.label for m in MachineTypeRef.query.all()]

def _load_pieces_connues() -> dict:
    from app.models.reference import PieceRef
    return {p.ref_piece.upper(): p.designation for p in PieceRef.query.all()}


# ── CRUD ──────────────────────────────────────────────────────
def creer_reparation(data: dict) -> Reparation:
    date_rep = data['date_reparation']
    if isinstance(date_rep, str):
        date_rep = datetime.strptime(date_rep, '%d/%m/%Y').date()

    labels         = _load_labels_machines()
    pieces_connues = _load_pieces_connues()

    machine_corrigee, _ = fuzzy_machine(data.get('machine_type', ''), labels)

    rep = Reparation(
        numero_serie    = data['numero_serie'].strip().upper(),
        machine_type    = machine_corrigee,
        technicien      = data.get('technicien', ''),
        date_reparation = date_rep,
        notes           = data.get('notes', '')
    )
    db.session.add(rep)
    db.session.flush()

    for p in data.get('pieces', []):
        ref_brute = p.get('ref_piece', '')
        ref_corrigee, designation, _ = fuzzy_piece(ref_brute, pieces_connues, cutoff=0.80)
        db.session.add(PieceChangee(
            reparation_id = rep.id,
            ref_piece     = ref_corrigee,
            designation   = designation or p.get('designation', ''),
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


# ── Suggestions (autocomplétion front) ───────────────────────
def suggest_machine_types(query: str, n: int = 5) -> list[str]:
    from difflib import get_close_matches
    labels = _load_labels_machines()
    return get_close_matches(query, labels, n=n, cutoff=0.5) if labels else []


def suggest_piece_refs(query: str, n: int = 5) -> list[str]:
    from difflib import get_close_matches
    refs = list(_load_pieces_connues().keys())
    return get_close_matches(query, refs, n=n, cutoff=0.5) if refs else []