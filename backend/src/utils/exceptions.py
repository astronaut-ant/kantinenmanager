class AccessDeniedError(Exception):
    """Exception raised when a user is not allowed to access a resource."""

    def __init__(self, ressource):
        super().__init__(f"Nutzer:in hat keinen Zugriff auf {ressource}.")


class NotFoundError(Exception):
    """Exception raised when an object is not found in the database."""

    def __init__(self, ressource):
        super().__init__(
            f"{ressource} konnte nicht gefunden werden oder existiert nicht."
        )


class AlreadyExistsError(Exception):
    """Exception raised when an object already exists in the database."""

    def __init__(self, ressource, details=""):
        super().__init__(f"Konflikt: {ressource} existiert bereits{details}.")


class ActionNotPossibleError(Exception):
    """Exception raised when an action is not possible."""

    def __init__(self, message):
        super().__init__(f"Aktion aufgrund von Konflikt nicht möglich: {message}")


class BadValueError(Exception):
    """Exception raised when a value is not valid."""

    def __init__(self, message):
        super().__init__(f"Ungültiger Wert: {message}")


class UserBlockedError(Exception):
    """Exception raised when a user is blocked."""

    def __init__(self, message):
        super().__init__(f"Blockiert: {message}")
