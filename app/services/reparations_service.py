from datetime import date as date_type

from cv2 import data

from app.models.reparation import Reparation
from app.models.piece_changee import PieceChangee
from app.models.piece_ref import PieceRef
from app.repositories.machine_repository import MachineRepository
from app.repositories.modele_repository import ModeleRepository
from app.repositories.piece_repository import PieceRefRepository
from app.repositories.reparation_repository import ReparationRepository
from app.repositories.user_repository import UserRepository
from app.utils.fuzzy import fuzzy_piece
from app.utils.exceptions import MachineAlreadyInRepairError


def creer_reparation(data: dict) -> Reparation:
    date_val = data.get('date_reparation')
    if not date_val:
        raise ValueError("date_reparation est requis.")
    try:
        date_rep = date_val if isinstance(date_val, date_type) \
            else date_type.fromisoformat(str(date_val).strip())
    except ValueError:
        raise ValueError(f"Format de date invalide : {date_val!r}. Attendu : YYYY-MM-DD")
    # ── GARDE : machine déjà en réparation ───────────────────────────
    machine_id = data.get('machine_id')

    machine = MachineRepository.get_by_id(machine_id) if machine_id else None
    if not machine:
        raise ValueError("Machine introuvable.")
    
    if machine.statut == 'en_reparation':
        raise MachineAlreadyInRepairError(
            "Cette machine est déjà en réparation.",
            code="MACHINE_ALREADY_IN_REPAIR"
        )
    
    technicien_id = data.get('technicien_id') or None
    technicien_nom = data.get('technicien', '')

    if technicien_id and not technicien_nom:
        user = UserRepository.get_by_id(technicien_id)
        technicien_nom = f"{user.prenom} {user.nom}".strip() if user else ''

    reparations = ReparationRepository.get_by_machine(machine_id)
    if reparations:
        last = reparations[-1]
        if last.statut == 'en_cours':
            raise MachineAlreadyInRepairError(
                "Cette machine est déjà en réparation.",
                code="MACHINE_ALREADY_IN_REPAIR"
            )
             
    rep = Reparation(
        machine_id=data['machine_id'],
        technicien=technicien_nom,
        technicien_id=data.get('technicien_id') or None,
        date_reparation=date_rep,
        statut='en_cours',
        description=data.get('description', data.get('notes', ''))
    )
    ReparationRepository.add(rep)      # db.session.add() — pas de commit
    ReparationRepository.flush()    # génère l'id de la réparation avant d'ajouter les pièces (nécessaire pour la relation)

    pieces_connues = PieceRefRepository.get_all_as_dict()

    marque_id = machine.modele.marque_id if machine and machine.modele else None

    for p in data.get('pieces', []):
        if not p.get('quantite', 0):
            continue

        ref_brute = p.get('ref_piece', '').strip().upper()
        ref_corrigee, designation, _ = fuzzy_piece(ref_brute, pieces_connues, cutoff=0.80)

        piece_obj = PieceRefRepository.get_by_ref(ref_corrigee)
        if not piece_obj and p.get('is_new'):
            if not marque_id:
                raise ValueError("Impossible de créer une nouvelle référence de pièce sans marque associée.")
            piece_obj = PieceRef(
                ref_piece=ref_corrigee,
                designation=p.get('designation', designation),
                marque_id=marque_id
            )
            PieceRefRepository.add(piece_obj)
            PieceRefRepository.flush()           # génère piece_obj.id pour la relation avec PieceChangee

        if piece_obj:
            ReparationRepository.add_piece_changee(
                PieceChangee(
                    reparation_id=rep.id,
                    piece_ref_id=piece_obj.id,
                    quantite=int(p.get('quantite', 1))
                )
            )
    ReparationRepository.commit() 
    # Mettre la machine en réparation
    machine.statut = 'en_reparation'
    MachineRepository.save(machine)

    return rep

def modifier_reparation(rep_id: int, data: dict) -> Reparation:
    """
    PATCH partiel d'une réparation :
    - Champs de base (technicien, date_reparation, description)
    - Remplacement complet des pièces changées si 'pieces' est présent
    """
    rep = ReparationRepository.get_by_id(rep_id)

    if 'technicien' in data:
        rep.technicien = data['technicien']
    if 'date_reparation' in data:
        rep.date_reparation = data['date_reparation']
    if 'description' in data:
        rep.description = data['description']

    if 'pieces' in data:
        # Supprimer les anciennes pièces
        for p in list(rep.pieces):
            ReparationRepository.delete_piece_changee(p)
        ReparationRepository.flush()

        pieces_connues = PieceRefRepository.get_all_as_dict()

        for p in data['pieces']:
            if not p.get('quantite', 0):
                continue
            ref_brute = p.get('ref_piece', '').strip().upper()
            ref_corrigee, designation, _ = fuzzy_piece(ref_brute, pieces_connues, cutoff=0.80)

            piece_obj = PieceRefRepository.get_by_ref(ref_corrigee)
            if not piece_obj and p.get('is_new'):
                piece_obj = PieceRef(
                    ref_piece=ref_corrigee,
                    designation=p.get('designation', designation),
                    marque_id=p.get('marque_id')
                )
                PieceRefRepository.add(piece_obj)
                PieceRefRepository.flush()

            if piece_obj:
                ReparationRepository.add_piece_changee(
                    PieceChangee(
                        reparation_id=rep.id,
                        piece_ref_id=piece_obj.id,
                        quantite=int(p.get('quantite', 1))
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

def get_reparations_by_numero_serie(numero_serie: str):
    machine = MachineRepository.get_by_serie(numero_serie)
    if not machine:
        return None
    return ReparationRepository.get_by_machine(machine.id)

def get_reparations_by_technicien_id(technicien_id: int) -> list[Reparation]:
    return ReparationRepository.get_by_technicien_id(technicien_id)

def get_mes_reparations(user_id: int):
    try:
        uid = int(user_id)
        user = UserRepository.get_by_id(uid)
    except (ValueError, TypeError):
        # identity est un email ou username
        user = UserRepository.get_by_email(str(user_id))

    if not user:
        return None
    return ReparationRepository.get_by_technicien_id(user.id)

def suggest_piece_refs(query: str):
    return PieceRefRepository.search(query)

def suggest_modeles(query: str):
    return ModeleRepository.search(query)

def delete_reparation(rep_id: int) -> None:
    rep = ReparationRepository.get_by_id(rep_id)
    ReparationRepository.delete(rep)