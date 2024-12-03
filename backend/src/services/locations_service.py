from uuid import UUID
from src.models.location import Location
from src.utils.exceptions import LocationAlreadyExistsError
from src.repositories.locations_repository import LocationsRepository


class LocationsService:
    """class for managing locations and location leaders"""

    @staticmethod
    def create_location(location_name: str, location_leader_id: UUID) -> UUID:
        """Create a new location in the database.

        :param location_name: The name of the new location
        :param location_leader_id: The ID of the location leader

        :return: the ID of the new location

        :raises LocationAlreadyExistsError: If a location with the given name already exists
        """

        if LocationsRepository.get_location_by_name(location_name):
            raise LocationAlreadyExistsError(
                f"Location with name {location_name} already exists"
            )

        location = Location(
            location_name=location_name, location_leader_id=location_leader_id
        )

        id = LocationsRepository.create_location(location)

        return id
