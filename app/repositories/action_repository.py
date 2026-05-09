from app.extensions import db
from app.models.reparation_action import ReparationAction


class ActionRepository:

    @staticmethod
    def get_by_id(action_id: int) -> ReparationAction:
        return db.get_or_404(ReparationAction, action_id)

    @staticmethod
    def get_by_reparation(reparation_id: int) -> list[ReparationAction]:
        return (
            ReparationAction.query
            .filter_by(reparation_id=reparation_id)
            .order_by(ReparationAction.date_action.asc(),
                      ReparationAction.created_at.asc())
            .all()
        )

    @staticmethod
    def add(action: ReparationAction) -> None:
        db.session.add(action)

    @staticmethod
    def flush() -> None:
        db.session.flush()

    @staticmethod
    def commit() -> None:
        db.session.commit()

    @staticmethod
    def delete(action: ReparationAction) -> None:
        db.session.delete(action)
        db.session.commit()
