from uuid import UUID


class LocationAlreadyExistsError(Exception):
    """Exception raised when a location with the same name already exists."""

    pass


class GroupDoesNotExistError(Exception):
    """Exception raised when a group does not exist at a given location."""

    def __init__(self, group_id: UUID):
        super().__init__(f"Die Gruppe mit der ID {group_id} existiert nicht.")
