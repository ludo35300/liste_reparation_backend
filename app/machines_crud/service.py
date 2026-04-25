from app.models.machine          import Machine
from app.models.modele           import Modele
from app.repositories.machine_repository import MachineRepository
from app.machines                import resolve_machine_info


def get_all_machines() -> list[Machine]:
    return MachineRepository.get_all()


def get_machine_by_id(machine_id: int) -> Machine:
    return MachineRepository.get_by_id(machine_id)


def get_machine_by_serie(numero_serie: str) -> Machine | None:
    return MachineRepository.get_by_serie(numero_serie)


def create_machine(data: dict) -> Machine:
    numero_serie = data['numero_serie'].strip().upper()
    if MachineRepository.exists_by_serie(numero_serie):
        raise ValueError(f"Numéro de série '{numero_serie}' déjà enregistré")

    machine = Machine(
        numero_serie = numero_serie,
        modele_id    = data.get('modele_id'),
        statut       = data.get('statut', 'en_attente'),
        date_entree  = data.get('date_entree'),
        notes        = data.get('notes', ''),
    )
    return MachineRepository.save(machine)


def update_machine(machine_id: int, data: dict) -> Machine:
    machine = MachineRepository.get_by_id(machine_id)
    for field in ('statut', 'notes', 'modele_id', 'date_entree'):
        if field in data:
            setattr(machine, field, data[field])
    return MachineRepository.save(machine)


def delete_machine(machine_id: int) -> None:
    machine = MachineRepository.get_by_id(machine_id)
    MachineRepository.delete(machine)


def get_machine_info(machine_id: int) -> dict:
    """Retourne les infos enrichies (specs, vue éclatée) via le registre handlers."""
    machine = MachineRepository.get_by_id(machine_id)
    info = None
    if machine.modele:
        info = resolve_machine_info(
            brand        = machine.modele.marque.nom if machine.modele.marque else '',
            model        = machine.modele.nom,
            numero_serie = machine.numero_serie,
        )
    return {
        "machine_id":    machine.id,
        "numero_serie":  machine.numero_serie,
        "modele":        machine.modele.label if machine.modele else None,
        "statut":        machine.statut,
        "info_enrichie": {
            "brand":         info.brand if info else None,
            "model":         info.model if info else None,
            "description":   info.description if info else None,
            "specs":         info.specs if info else {},
            "exploded_view": {
                "label":   info.exploded_view.label,
                "pdf_url": info.exploded_view.pdf_url,
                "note":    info.exploded_view.note,
            } if (info and info.exploded_view) else None,
        }
    }
