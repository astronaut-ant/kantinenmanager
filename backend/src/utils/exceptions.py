class AccessDeniedError(Exception):
    """Exception raised when a user is not allowed to access a resource."""

    def __init__(self, ressource: str):
        super().__init__(f"Nutzer hat keinen Zugriff auf {ressource}.", code=400)


class NotFoundError(Exception):
    """Exception raised when an object is not found in the database."""

    def __init__(self, ressource: str):
        super().__init__(f"{ressource} nicht gefunden oder existiert nicht.", code=404)


class AlreadyExistsError(Exception):
    """Exception raised when an object already exists in the database."""

    def __init__(self, ressource: str):
        super().__init__(f"{ressource} existiert bereits.", code=400)


###########################################################################


class LocationAlreadyExistsError(Exception):
    """Exception raised when a location with the same name already exists."""

    pass


class UserAlreadyExistsError(Exception):
    """Exception raised when a username is already taken."""

    pass


class UserBlockedError(Exception):
    """Exception raised when a user is blocked."""

    pass


class UserCannotBeDeletedError(Exception):
    """Exception raised when a user cannot be deleted."""

    pass


class EmployeeAlreadyExistsError(Exception):
    """Exception raised when an employee number already exists."""

    pass


class GroupDoesNotExistError(Exception):
    """Exception raised when a group does not exist at a given location."""

    pass


class EmployeeDoesNotExistError(Exception):
    """Exception raised when an employee ID does not exist."""

    pass


class NameNotAppropriateError(Exception):
    """Exception raised when a Name is to long or not splitable"""

    pass


class FileNotProcessableError(Exception):
    """Exception raised when a File has wrong contents and cannot be read"""

    pass


class PersonDoesNotExistError(Exception):
    """Exception raised when a person does not exist at a given location."""

    pass


class LocationAlreadyExistsError(Exception):
    """Exception raised when a location already exists."""

    pass


class LeaderDoesNotExist(Exception):
    """Exception raised when a leader does not exist."""

    pass


class LocationDoesNotExist(Exception):
    """Exception raised when a location does not exist."""

    pass


class OrderAlreadyExistsForPersonAndDate(Exception):
    """Exception raised when an order already exists for a person and date."""

    pass


class PersonNotPartOfGroup(Exception):
    """Exception raised when a person is not part of the group."""

    pass


class PersonNotPartOfLocation(Exception):
    """Exception raised when a person is not part of the location."""

    pass


class GroupAlreadyExists(Exception):
    """Exception raised when a group that should be created already exists."""

    pass


class WrongUserError(Exception):
    """Exception raised when a user is not allowed to create an order for another user."""

    pass


class WrongLocationError(Exception):
    """Exception raised when a user is not allowed to create an order for another user."""

    pass


class OrderTransferError(Exception):
    """Exception raised when the transfer of orders failed."""

    pass


class AccessDeniedError(Exception):
    """Exception raised when the user has no access to the requested resource."""

    pass
