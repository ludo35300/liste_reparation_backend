from app.extensions      import db
from app.models.piece_ref import PieceRef


class PieceRefRepository:

    @staticmethod
    def get_by_id(piece_id: int) -> PieceRef:
        return db.get_or_404(PieceRef, piece_id)

    @staticmethod
    def get_by_ref(ref_piece: str) -> PieceRef | None:
        return PieceRef.query.filter_by(
            ref_piece=ref_piece.strip().upper()
        ).first()

    @staticmethod
    def get_all(marque_id: int = None) -> list[PieceRef]:
        q = PieceRef.query.order_by(PieceRef.ref_piece)
        if marque_id:
            q = q.filter_by(marque_id=marque_id)
        return q.all()

    @staticmethod
    def search(query: str, limit: int = 10) -> list[PieceRef]:
        """Recherche partielle (autocomplete) sur ref_piece."""
        return (
            PieceRef.query
            .filter(PieceRef.ref_piece.ilike(f'%{query.strip().upper()}%'))
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_all_as_dict() -> dict[str, str]:
        """Retourne {ref_piece: designation} pour le fuzzy-matching."""
        return {p.ref_piece.upper(): p.designation for p in PieceRef.query.all()}

    @staticmethod
    def save(piece: PieceRef) -> PieceRef:
        db.session.add(piece)
        db.session.flush()
        return piece

    @staticmethod
    def delete(piece: PieceRef) -> None:
        db.session.delete(piece)
        db.session.commit()

    @staticmethod
    def add(piece: PieceRef) -> None:
        db.session.add(piece)

    @staticmethod
    def flush() -> None:
        db.session.flush()
