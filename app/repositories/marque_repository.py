from app.extensions   import db
from app.models.marque import Marque


class MarqueRepository:

    @staticmethod
    def get_by_id(marque_id: int) -> Marque:
        return db.get_or_404(Marque, marque_id)

    @staticmethod
    def get_by_nom(nom: str) -> Marque | None:
        return Marque.query.filter_by(nom=nom.strip().upper()).first()

    @staticmethod
    def get_all() -> list[Marque]:
        return Marque.query.order_by(Marque.nom).all()

    @staticmethod
    def save(marque: Marque) -> Marque:
        db.session.add(marque)
        db.session.commit()
        return marque

    @staticmethod
    def delete(marque: Marque) -> None:
        db.session.delete(marque)
        db.session.commit()
