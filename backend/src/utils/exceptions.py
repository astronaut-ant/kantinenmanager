class UserAlreadyExistsError(Exception):
    """Exception raised when a username is already taken."""

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
