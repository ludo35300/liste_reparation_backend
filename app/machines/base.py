# app/machines/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ExplodedView:
    label: str
    pdf_url: str
    note: str | None = None


@dataclass
class MachineInfo:
    brand: str
    model: str
    description: str | None = None
    specs: dict | None = field(default_factory=dict)
    exploded_view: ExplodedView | None = None


class MachineHandler(ABC):
    """
    Interface commune à tous les handlers de modèles de machine.
    Implémenter can_handle() et get_info() pour chaque nouveau modèle.
    """

    @classmethod
    @abstractmethod
    def can_handle(cls, brand: str, model: str) -> bool:
        """Retourne True si ce handler reconnaît le couple (brand, model)."""
        ...

    @classmethod
    @abstractmethod
    def get_info(cls, numero_serie: str) -> MachineInfo:
        """Retourne les infos enrichies pour ce numéro de série."""
        ...