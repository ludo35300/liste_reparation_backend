from sqlalchemy.orm import joinedload
from app.extensions    import db
from app.models.machine import Machine
from app.models.modele  import Modele


class MachineRepository:

    @staticmethod
    def get_by_id(machine_id: int) -> Machine:
        """Retourne la machine ou lève un 404."""
        return db.get_or_404(Machine, machine_id)

    @staticmethod
    def get_by_id_or_none(machine_id: int) -> Machine | None:
        return db.session.get(Machine, machine_id)

    @staticmethod
    def get_by_serie(numero_serie: str) -> Machine | None:
        return Machine.query.filter_by(
            numero_serie=numero_serie.strip().upper()
        ).first()

    @staticmethod
    def get_all() -> list[Machine]:
        return (
            Machine.query
            .options(joinedload(Machine.modele).joinedload(Modele.marque))
            .order_by(Machine.created_at.desc())
            .all()
        )

    @staticmethod
    def exists_by_serie(numero_serie: str) -> bool:
        return Machine.query.filter_by(
            numero_serie=numero_serie.strip().upper()
        ).first() is not None

    @staticmethod
    def save(machine: Machine) -> Machine:
        db.session.add(machine)
        db.session.commit()
        return machine

    @staticmethod
    def delete(machine: Machine) -> None:
        db.session.delete(machine)
        db.session.commit()

    @staticmethod
    def update_statut(machine_id: int, statut: str) -> None:
        machine = db.session.get(Machine, machine_id)
        if machine:
            machine.statut = statut

    @staticmethod
    def has_open_repair(machine_id: int) -> bool:
        """Retourne True si la machine a le statut 'en_reparation'."""
        from app.models.machine import Machine
        machine = db.session.get(Machine, machine_id)
        return machine is not None and machine.statut == 'en_reparation'

    @staticmethod
    def search_by_serie_partial(query: str) -> list[Machine]:
        q = query.strip().upper()
        if not q:
            return []

        return (
            Machine.query
            .options(joinedload(Machine.modele).joinedload(Modele.marque))
            .filter(Machine.numero_serie.ilike(f"%{q}%"))
            .order_by(Machine.created_at.desc())
            .all()
        )