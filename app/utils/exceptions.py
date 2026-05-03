class ConflictError(Exception):
    """Levée quand une règle métier interdit l'opération (ex : doublon, état invalide)."""
    def __init__(self, message: str, code: str = 'CONFLICT'):
        super().__init__(message)
        self.code = code

class MachineAlreadyInRepairError(Exception):
    def __init__(self, message: str, code: str = 'MACHINE_ALREADY_IN_REPAIR'):
        super().__init__(message)
        self.code = code