from app.extensions import db
from app.models.reference import MachineTypeRef, PieceRef

# ── MachineTypeRef ─────────────────────────────────────────────

def get_all_machines():
    return MachineTypeRef.query.order_by(
        MachineTypeRef.marque,
        MachineTypeRef.modele
    ).all()   # ← tri sur vraies colonnes SQL, pas sur @property

def get_machine_by_id(machine_id: int):
    return MachineTypeRef.query.get_or_404(machine_id)

def create_machine(marque: str, modele: str, type_machine: str) -> MachineTypeRef:
    machine = MachineTypeRef(
        marque=marque.strip().upper(),
        modele=modele.strip().upper(),
        type_machine=type_machine.strip().upper()
    )
    db.session.add(machine)
    db.session.commit()
    return machine

def delete_machine(machine_id: int):
    machine = MachineTypeRef.query.get_or_404(machine_id)
    db.session.delete(machine)
    db.session.commit()

# ── PieceRef ───────────────────────────────────────────────────

def get_all_pieces():
    return PieceRef.query.order_by(PieceRef.ref_piece).all()

def get_piece_by_id(piece_id: int):
    return PieceRef.query.get_or_404(piece_id)

def create_piece(ref_piece: str, designation: str) -> PieceRef:
    piece = PieceRef(ref_piece=ref_piece, designation=designation)
    db.session.add(piece)
    db.session.commit()
    return piece

def delete_piece(piece_id: int):
    piece = PieceRef.query.get_or_404(piece_id)
    db.session.delete(piece)
    db.session.commit()

# ── Association Machine ↔ Pièce ────────────────────────────────

def add_piece_to_machine(machine_id: int, piece_id: int):
    machine = MachineTypeRef.query.get_or_404(machine_id)
    piece   = PieceRef.query.get_or_404(piece_id)
    if piece not in machine.pieces:
        machine.pieces.append(piece)
        db.session.commit()
    return machine

def remove_piece_from_machine(machine_id: int, piece_id: int):
    machine = MachineTypeRef.query.get_or_404(machine_id)
    piece   = PieceRef.query.get_or_404(piece_id)
    if piece in machine.pieces:
        machine.pieces.remove(piece)
        db.session.commit()
    return machine

def update_machine_logo(machine_id: int, url_logo: str) -> MachineTypeRef:
    machine = MachineTypeRef.query.get_or_404(machine_id)
    machine.url_logo = url_logo   # ← url_logo
    db.session.commit()
    return machine
    
