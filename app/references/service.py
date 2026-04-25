from app.models.marque    import Marque
from app.models.modele    import Modele
from app.models.piece_ref import PieceRef
from app.repositories.marque_repository  import MarqueRepository
from app.repositories.modele_repository  import ModeleRepository
from app.repositories.piece_repository   import PieceRefRepository


# ── Marques ──────────────────────────────────────────────
def get_all_marques() -> list[Marque]:
    return MarqueRepository.get_all()

def get_marque_by_id(marque_id: int) -> Marque:
    return MarqueRepository.get_by_id(marque_id)

def create_marque(nom: str, url_logo: str = None) -> Marque:
    marque = Marque(nom=nom.strip().upper(), url_logo=url_logo)
    return MarqueRepository.save(marque)

def delete_marque(marque_id: int) -> None:
    marque = MarqueRepository.get_by_id(marque_id)
    MarqueRepository.delete(marque)

def update_marque_logo(marque_id: int, url_logo: str) -> Marque:
    marque = MarqueRepository.get_by_id(marque_id)
    marque.url_logo = url_logo
    return MarqueRepository.save(marque)


# ── Modeles ────────────────────────────────────────────
def get_all_modeles(marque_id: int = None) -> list[Modele]:
    return ModeleRepository.get_all(marque_id=marque_id)

def get_modele_by_id(modele_id: int) -> Modele:
    return ModeleRepository.get_by_id(modele_id)

def create_modele(nom: str, type_machine: str, marque_id: int) -> Modele:
    modele = Modele(
        nom          = nom.strip().upper(),
        type_machine = type_machine.strip().upper(),
        marque_id    = marque_id,
    )
    return ModeleRepository.save(modele)

def delete_modele(modele_id: int) -> None:
    modele = ModeleRepository.get_by_id(modele_id)
    ModeleRepository.delete(modele)


# ── PieceRef ───────────────────────────────────────────
def get_all_pieces(marque_id: int = None) -> list[PieceRef]:
    return PieceRefRepository.get_all(marque_id=marque_id)

def get_piece_by_id(piece_id: int) -> PieceRef:
    return PieceRefRepository.get_by_id(piece_id)

def create_piece(ref_piece: str, designation: str, marque_id: int) -> PieceRef:
    piece = PieceRef(
        ref_piece   = ref_piece.strip().upper(),
        designation = designation,
        marque_id   = marque_id,
    )
    return PieceRefRepository.save(piece)

def delete_piece(piece_id: int) -> None:
    piece = PieceRefRepository.get_by_id(piece_id)
    PieceRefRepository.delete(piece)


# ── Association Modele ↔ Piece ──────────────────────────
def get_pieces_by_modele(modele_id: int) -> list[PieceRef]:
    modele = ModeleRepository.get_by_id(modele_id)
    return ModeleRepository.get_pieces(modele)

def add_piece_to_modele(modele_id: int, piece_id: int) -> Modele:
    modele = ModeleRepository.get_by_id(modele_id)
    piece  = PieceRefRepository.get_by_id(piece_id)
    ModeleRepository.add_piece(modele, piece)
    return modele

def remove_piece_from_modele(modele_id: int, piece_id: int) -> Modele:
    modele = ModeleRepository.get_by_id(modele_id)
    piece  = PieceRefRepository.get_by_id(piece_id)
    ModeleRepository.remove_piece(modele, piece)
    return modele
