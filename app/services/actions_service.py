from datetime import date as date_type

from app.models.reparation_action import ReparationAction
from app.repositories.action_repository import ActionRepository
from app.repositories.reparation_repository import ReparationRepository
from app.repositories.machine_repository import MachineRepository
from app.repositories.piece_repository import PieceRefRepository


def get_actions(reparation_id: int) -> list[ReparationAction]:
    ReparationRepository.get_by_id(reparation_id)   # lève 404 si inexistante
    return ActionRepository.get_by_reparation(reparation_id)


def ajouter_action(reparation_id: int, data: dict) -> ReparationAction:
    reparation = ReparationRepository.get_by_id(reparation_id)

    # Validation croisée : type 'statut' exige statut_apres
    if data.get('type') == 'statut' and not data.get('statut_apres'):
        raise ValueError("statut_apres est requis pour une action de type 'statut'.")

    date_val = data.get('date_action')
    try:
        date_action = date_val if isinstance(date_val, date_type) \
            else date_type.fromisoformat(str(date_val).strip())
    except (ValueError, AttributeError):
        raise ValueError(f"Format de date invalide : {date_val!r}. Attendu : YYYY-MM-DD")

    action = ReparationAction(
        reparation_id = reparation.id,
        technicien_id = data.get('technicien_id'),
        type          = data['type'],
        titre         = data['titre'],
        description   = data.get('description', ''),
        technicien    = data.get('technicien', ''),
        date_action   = date_action,
        duree_minutes = data.get('duree_minutes'),
        statut_avant  = data.get('statut_avant'),
        statut_apres  = data.get('statut_apres'),
    )
    ActionRepository.add(action)
    ActionRepository.flush()   # génère action.id pour les pièces

    for p in data.get('pieces', []):
        piece_ref = PieceRefRepository.get_by_id(p['piece_ref_id'])
        if not piece_ref:
            raise ValueError(f"Pièce introuvable : id={p['piece_ref_id']}")
        

    # Si l'action change le statut de la machine → mettre à jour
    if data.get('statut_apres') and reparation.machine:
        MachineRepository.update_statut(reparation.machine_id, data['statut_apres'])

    ActionRepository.commit()
    return action


def modifier_action(reparation_id: int, action_id: int, data: dict) -> ReparationAction:
    action = ActionRepository.get_by_id(action_id)
    if action.reparation_id != reparation_id:
        raise ValueError("Cette action n'appartient pas à cette réparation.")

    for field in ('type', 'titre', 'description', 'technicien',
                  'technicien_id', 'duree_minutes', 'statut_avant', 'statut_apres'):
        if field in data:
            setattr(action, field, data[field])

    if 'date_action' in data:
        val = data['date_action']
        action.date_action = val if isinstance(val, date_type) \
            else date_type.fromisoformat(str(val).strip())

    ActionRepository.commit()
    return action


def supprimer_action(reparation_id: int, action_id: int) -> None:
    action = ActionRepository.get_by_id(action_id)
    if action.reparation_id != reparation_id:
        raise ValueError("Cette action n'appartient pas à cette réparation.")
    ActionRepository.delete(action)
