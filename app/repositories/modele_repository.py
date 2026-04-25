from app.extensions   import db
from app.models.modele import Modele
from app.models.piece_ref import PieceRef


class ModeleRepository:

    @staticmethod
    def get_by_id(modele_id: int) -> Modele:
        return db.get_or_404(Modele, modele_id)

    @staticmethod
    def get_all(marque_id: int = None) -> list[Modele]:
        q = Modele.query.order_by(Modele.nom)
        if marque_id:
            q = q.filter_by(marque_id=marque_id)
        return q.all()

    @staticmethod
    def search(query: str, limit: int = 10) -> list[Modele]:
        """Recherche partielle (autocomplete) sur le nom du modèle."""
        return (
            Modele.query
            .filter(Modele.nom.ilike(f'%{query.strip().upper()}%'))
            .limit(limit)
            .all()
        )

    @staticmethod
    def save(modele: Modele) -> Modele:
        db.session.add(modele)
        db.session.commit()
        return modele

    @staticmethod
    def delete(modele: Modele) -> None:
        db.session.delete(modele)
        db.session.commit()

    # ── Association Modele ↔ PieceRef ─────────────────────────
    @staticmethod
    def get_pieces(modele: Modele) -> list[PieceRef]:
        return modele.pieces

    @staticmethod
    def add_piece(modele: Modele, piece: PieceRef) -> None:
        if piece not in modele.pieces:
            modele.pieces.append(piece)
            db.session.commit()

    @staticmethod
    def remove_piece(modele: Modele, piece: PieceRef) -> None:
        if piece in modele.pieces:
            modele.pieces.remove(piece)
            db.session.commit()
