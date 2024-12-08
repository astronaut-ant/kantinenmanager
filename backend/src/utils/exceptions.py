from uuid import UUID


class LocationAlreadyExistsError(Exception):
    """Exception raised when a location with the same name already exists."""

    pass


class UserAlreadyExistsError(Exception):
    """Exception raised when a username is already taken."""

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


class GroupLeaderDoesNotExistError(Exception):
    """Exception raised when a group leader does not exist."""

    pass


class GroupLeaderDoesNotExist(Exception):
    """Exception raised when a group leader does not exist."""

    pass


class LocationDoesNotExist(Exception):
    """Exception raised when a location does not exist."""

    pass


class OrderAlreadyExistsForPersonAndDate(Exception):
    """Exception raised when an order already exists for a person and date."""

    pass
