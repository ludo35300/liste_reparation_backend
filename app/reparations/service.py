from datetime import date as date_type
import datetime
from app.extensions            import db
from app.models.reparation     import Reparation
from app.models.piece_changee  import PieceChangee
from app.models.machine        import Machine
from app.models.piece_ref      import PieceRef
from app.utils.fuzzy           import fuzzy_piece


def _load_pieces_connues() -> dict:
    return {p.ref_piece.upper(): p.designation for p in PieceRef.query.all()}

def creer_reparation(data: dict) -> Reparation:
    # ─── Date ──────────────────────────────────────────────────
    date_str = (data.get('date_reparation') or '').strip()
    if not date_str:
        raise ValueError("date_reparation est requis.")

    try:
        date_rep = date_type.fromisoformat(date_str)  # YYYY-MM-DD
    except ValueError:
        raise ValueError(f"Format de date invalide : {date_str!r}. Attendu : YYYY-MM-DD")

    # ─── Technicien ────────────────────────────────────────────
    technicien_id = None
    if data.get('technicien'):
        from app.models.user import User
        user = User.query.filter_by(first_name=data['technicien']).first()
        technicien_id = user.id if user else None

    # ─── Réparation ────────────────────────────────────────────
    rep = Reparation(
        machine_id      = data['machine_id'],
        technicien      = data.get('technicien', ''),
        technicien_id   = technicien_id,
        date_reparation = date_rep,
        description     = data.get('description', data.get('notes', ''))
    )
    db.session.add(rep)
    db.session.flush()

    # ─── Pièces ────────────────────────────────────────────────
    pieces_connues = _load_pieces_connues()

    for p in data.get('pieces', []):
        if not p.get('quantite', 0):
            continue

        ref_brute = p.get('ref_piece', '').strip().upper()
        ref_corrigee, designation, _ = fuzzy_piece(ref_brute, pieces_connues, cutoff=0.80)

        piece_obj = PieceRef.query.filter_by(ref_piece=ref_corrigee).first()
        if not piece_obj and p.get('is_new'):
            piece_obj = PieceRef(
                ref_piece   = ref_corrigee,
                designation = p.get('designation', designation),
                marque_id   = p.get('marque_id')
            )
            db.session.add(piece_obj)
            db.session.flush()

        if piece_obj:
            db.session.add(PieceChangee(
                reparation_id = rep.id,
                piece_ref_id  = piece_obj.id,
                quantite      = int(p.get('quantite', 1))
            ))

    db.session.commit()
    return rep

def get_all_reparations():
    return Reparation.query.order_by(Reparation.date_reparation.desc()).all()

def get_reparation_by_id(rep_id: int):
    return db.get_or_404(Reparation, rep_id)

def get_reparations_by_machine(machine_id: int):
    return (Reparation.query
            .filter_by(machine_id=machine_id)
            .order_by(Reparation.date_reparation.desc())
            .all())

def get_reparations_by_technicien(technicien: str):
    return Reparation.query.filter_by(technicien=technicien).order_by(Reparation.date_reparation.desc()).all()

def delete_reparation(rep_id: int):
    rep = db.get_or_404(Reparation, rep_id)
    db.session.delete(rep)
    db.session.commit()

def parse_date(date_str: str):
    """Accepte YYYY-MM-DD (ISO, HTML) et DD/MM/YYYY (legacy)."""
    for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Format de date invalide : {date_str!r}. Attendu : YYYY-MM-DD")