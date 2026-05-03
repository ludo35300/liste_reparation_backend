class ConflictError(Exception):
    """Levée quand une règle métier interdit l'opération (ex : doublon, état invalide)."""
    def __init__(self, message: str, code: str = 'CONFLICT'):
        super().__init__(message)
        self.code = code