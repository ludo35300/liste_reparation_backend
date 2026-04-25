# app/machines/__init__.py
from .base import MachineHandler, MachineInfo, ExplodedView
from .santos_40a import Santos40AHandler

# Registre : ordre = priorité de matching
_HANDLERS: list[type[MachineHandler]] = [
    Santos40AHandler,
    # Santos43Handler,  # à venir
]


def resolve_machine_info(
    brand: str,
    model: str,
    numero_serie: str,
) -> MachineInfo | None:
    """
    Retourne les infos enrichies pour le couple (brand, model).
    Retourne None si aucun handler ne reconnaît la machine.
    """
    for handler in _HANDLERS:
        if handler.can_handle(brand, model):
            return handler.get_info(numero_serie)
    return None