from app.extensions        import db
from app.models.reparation  import Reparation
from app.models.piece_changee import PieceChangee


class ReparationRepository:

    @staticmethod
    def get_by_id(rep_id: int) -> Reparation:
        """Retourne la réparation ou lève un 404."""
        return db.get_or_404(Reparation, rep_id)

    @staticmethod
    def get_all() -> list[Reparation]:
        return (
            Reparation.query
            .order_by(Reparation.date_reparation.desc())
            .all()
        )

    @staticmethod
    def get_by_machine(machine_id: int) -> list[Reparation]:
        return (
            Reparation.query
            .filter_by(machine_id=machine_id)
            .order_by(Reparation.date_reparation.desc())
            .all()
        )

    @staticmethod
    def get_by_technicien_id(technicien_id: int) -> list[Reparation]:
        return (
            Reparation.query
            .filter_by(technicien_id=technicien_id)
            .order_by(Reparation.date_reparation.desc())
            .all()
        )

    @staticmethod
    def save(reparation: Reparation) -> Reparation:
        db.session.add(reparation)
        db.session.flush()   # génère l'id avant les pièces
        return reparation

    @staticmethod
    def add_piece_changee(piece: PieceChangee) -> None:
        db.session.add(piece)

    @staticmethod
    def commit() -> None:
        db.session.commit()

    @staticmethod
    def delete(reparation: Reparation) -> None:
        db.session.delete(reparation)
        db.session.commit()

    @staticmethod
    def add(reparation: Reparation) -> None:
        db.session.add(reparation)

    @staticmethod
    def flush() -> None:
        db.session.flush()
