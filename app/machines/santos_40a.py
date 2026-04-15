# app/machines/santos_40a.py
import re
from .base import MachineHandler, MachineInfo, ExplodedView


# Vues éclatées Santos 40A selon plages de numéros de série.
# Source : https://www.santos.fr (page produit 40A)
# Les plages sont à affiner si Santos publie des révisions supplémentaires.
# Format : (serial_min, serial_max, ExplodedView)
_EXPLODED_VIEWS: list[tuple[int, int, ExplodedView]] = [
    (
        0,
        9_999_999,
        ExplodedView(
            label="Santos 40A / 40A PPM — Vue éclatée",
            pdf_url="https://www.santos.fr/media/ftp/Users_manuals/FR_French/SANTOS_40-manu-FR-last.pdf",
            note="Manuel incluant la vue éclatée complète (40A et 06/06A)",
        ),
    ),
    # Exemple de future plage si Santos publie une révision :
    # (1_300_000, 9_999_999, ExplodedView(
    #     label="Santos 40A — Révision 2025",
    #     pdf_url="https://www.santos.fr/media/ftp/Exploded_views/40/SANTOS_40A_view_250101.pdf",
    #     note="À partir de janvier 2025",
    # )),
]

_SPECS = {
    "Diamètre meules": "Ø 63,5 mm",
    "Dose": "6,5 à 9 g",
    "Trémie": "2,2 kg",
    "Débit moyen": "8 kg/h",
    "Niveau sonore": "63 dB",
    "Moteur": "Asynchrone professionnel",
    "Fabrication": "100% France",
}


def _parse_serial(numero_serie: str) -> int | None:
    """Extrait la partie numérique d'un numéro de série Santos."""
    digits = re.sub(r'\D', '', numero_serie)
    return int(digits) if digits else None


def _get_exploded_view(numero_serie: str) -> ExplodedView | None:
    serial_int = _parse_serial(numero_serie)
    if serial_int is None:
        return None
    for serial_min, serial_max, view in _EXPLODED_VIEWS:
        if serial_min <= serial_int <= serial_max:
            return view
    return None


class Santos40AHandler(MachineHandler):

    # Patterns reconnus comme Santos 40A
    _BRAND_PATTERN = re.compile(r'santos', re.IGNORECASE)
    _MODEL_PATTERN  = re.compile(r'40\s?a(?:\s?ppm)?|40\s?an', re.IGNORECASE)

    @classmethod
    def can_handle(cls, brand: str, model: str) -> bool:
        return bool(
            cls._BRAND_PATTERN.search(brand or '')
            and cls._MODEL_PATTERN.search(model or '')
        )

    @classmethod
    def get_info(cls, numero_serie: str) -> MachineInfo:
        return MachineInfo(
            brand="Santos",
            model="40A / 40A PPM",
            description=(
                "Moulin espresso bar silencieux (63 dB), "
                "doseur volumétrique automatique, 100% fabriqué en France."
            ),
            specs=_SPECS,
            exploded_view=_get_exploded_view(numero_serie),
        )