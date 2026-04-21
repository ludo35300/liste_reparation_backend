from app.extensions      import db
from app.models.marque   import Marque
from app.models.modele   import Modele
from app.models.piece_ref import PieceRef

# ── Marques ────────────────────────────────────────────────────
def get_all_marques():
    return Marque.query.order_by(Marque.nom).all()

def get_marque_by_id(marque_id: int):
    return db.get_or_404(Marque, marque_id)

def create_marque(nom: str, url_logo: str = None) -> Marque:
    marque = Marque(nom=nom.strip().upper(), url_logo=url_logo)
    db.session.add(marque)
    db.session.commit()
    return marque

def delete_marque(marque_id: int):
    marque = db.get_or_404(Marque, marque_id)
    db.session.delete(marque)
    db.session.commit()

def update_marque_logo(marque_id: int, url_logo: str) -> Marque:
    marque = db.get_or_404(Marque, marque_id)
    marque.url_logo = url_logo
    db.session.commit()
    return marque

# ── Modeles ────────────────────────────────────────────────────
def get_all_modeles(marque_id: int = None):
    q = Modele.query.order_by(Modele.nom)
    if marque_id:
        q = q.filter_by(marque_id=marque_id)
    return q.all()

def get_modele_by_id(modele_id: int):
    return db.get_or_404(Modele, modele_id)

def create_modele(nom: str, type_machine: str, marque_id: int) -> Modele:
    modele = Modele(
        nom=nom.strip().upper(),
        type_machine=type_machine.strip().upper(),
        marque_id=marque_id
    )
    db.session.add(modele)
    db.session.commit()
    return modele

def delete_modele(modele_id: int):
    modele = db.get_or_404(Modele, modele_id)
    db.session.delete(modele)
    db.session.commit()

# ── PieceRef ────────────────────────────────────────────────────
def get_all_pieces(marque_id: int = None):
    q = PieceRef.query.order_by(PieceRef.ref_piece)
    if marque_id:
        q = q.filter_by(marque_id=marque_id)
    return q.all()

def get_piece_by_id(piece_id: int):
    return db.get_or_404(PieceRef, piece_id)

def create_piece(ref_piece: str, designation: str, marque_id: int) -> PieceRef:
    piece = PieceRef(
        ref_piece=ref_piece.strip().upper(),
        designation=designation,
        marque_id=marque_id
    )
    db.session.add(piece)
    db.session.commit()
    return piece

def delete_piece(piece_id: int):
    piece = db.get_or_404(PieceRef, piece_id)
    db.session.delete(piece)
    db.session.commit()

# ── Association Modele ↔ Piece ──────────────────────────────────
def get_pieces_by_modele(modele_id: int):
    modele = db.get_or_404(Modele, modele_id)
    return modele.pieces

def add_piece_to_modele(modele_id: int, piece_id: int) -> Modele:
    modele = db.get_or_404(Modele, modele_id)
    piece  = db.get_or_404(PieceRef, piece_id)
    if piece not in modele.pieces:
        modele.pieces.append(piece)
        db.session.commit()
    return modele

def remove_piece_from_modele(modele_id: int, piece_id: int) -> Modele:
    modele = db.get_or_404(Modele, modele_id)
    piece  = db.get_or_404(PieceRef, piece_id)
    if piece in modele.pieces:
        modele.pieces.remove(piece)
        db.session.commit()
    return modele
