from datetime import date as date_type
from app.models.reparation        import Reparation
from app.models.piece_changee     import PieceChangee
from app.models.piece_ref         import PieceRef
from app.repositories.reparation_repository import ReparationRepository
from app.repositories.piece_repository      import PieceRefRepository
from app.repositories.user_repository       import UserRepository
from app.utils.fuzzy              import fuzzy_piece


def creer_reparation(data: dict) -> Reparation:
    # ─── Date ──────────────────────────────────────────
    date_str = (data.get('date_reparation') or '').strip()
    if not date_str:
        raise ValueError("date_reparation est requis.")
    try:
        date_rep = date_type.fromisoformat(date_str)
    except ValueError:
        raise ValueError(f"Format de date invalide : {date_str!r}. Attendu : YYYY-MM-DD")

    # ─── Technicien ────────────────────────────────────
    technicien_id = None
    if data.get('technicien_id'):
        technicien_id = data['technicien_id']

    # ─── Réparation ──────────────────────────────────
    rep = Reparation(
        machine_id      = data['machine_id'],
        technicien      = data.get('technicien', ''),
        technicien_id   = technicien_id,
        date_reparation = date_rep,
        description     = data.get('description', data.get('notes', ''))
    )
    ReparationRepository.save(rep)

    # ─── Pièces ─────────────────────────────────────
    pieces_connues = PieceRefRepository.get_all_as_dict()

    for p in data.get('pieces', []):
        if not p.get('quantite', 0):
            continue

        ref_brute = p.get('ref_piece', '').strip().upper()
        ref_corrigee, designation, _ = fuzzy_piece(ref_brute, pieces_connues, cutoff=0.80)

        piece_obj = PieceRefRepository.get_by_ref(ref_corrigee)
        if not piece_obj and p.get('is_new'):
            piece_obj = PieceRef(
                ref_piece   = ref_corrigee,
                designation = p.get('designation', designation),
                marque_id   = p.get('marque_id')
            )
            PieceRefRepository.save(piece_obj)

        if piece_obj:
            ReparationRepository.add_piece_changee(
                PieceChangee(
                    reparation_id = rep.id,
                    piece_ref_id  = piece_obj.id,
                    quantite      = int(p.get('quantite', 1))
                )
            )

    ReparationRepository.commit()
    return rep


def get_all_reparations() -> list[Reparation]:
    return ReparationRepository.get_all()


def get_reparation_by_id(rep_id: int) -> Reparation:
    return ReparationRepository.get_by_id(rep_id)


def get_reparations_by_machine(machine_id: int) -> list[Reparation]:
    return ReparationRepository.get_by_machine(machine_id)


def get_reparations_by_technicien_id(technicien_id: int) -> list[Reparation]:
    return ReparationRepository.get_by_technicien_id(technicien_id)


def delete_reparation(rep_id: int) -> None:
    rep = ReparationRepository.get_by_id(rep_id)
    ReparationRepository.delete(rep)
