from uuid import UUID
from src.services.auth_service import AuthService
from src.models.user import UserGroup
from src.models.location import Location
from src.repositories.locations_repository import LocationsRepository
from src.utils.exceptions import (
    LocationAlreadyExistsError,
    GroupLeaderDoesNotExistError,
)


class LocationsService:
    """Service for handling location management."""

    @staticmethod
    def get_locations() -> list[Location]:
        """Get all locations."""

        return LocationsRepository.get_locations()

    @staticmethod
    def get_location_by_id(location_id: UUID) -> Location | None:
        """Retrieve a location by its ID

        :param location_id: The ID of the location to retrieve

        :return: The location with the given ID or None if no location was found
        """

        return LocationsRepository.get_location_by_id(location_id)

    @staticmethod
    def create_location(location_name: str, user_id_location_leader: UUID) -> UUID:
        """Create a new location

        :param location_name: The name of the location
        :param user_id_location_leader: The ID of the location leader

        :return: The id of the created location
        """

        if LocationsRepository.get_location_by_name(location_name):
            raise LocationAlreadyExistsError(
                f"Standort {location_name} existiert bereits"
            )
        if not LocationsRepository.get_user_by_id(user_id_location_leader):
            raise GroupLeaderDoesNotExistError(
                f"Gruppenleiter mit ID {user_id_location_leader} existiert nicht"
            )

        location_id = LocationsRepository.create_location(
            location_name, user_id_location_leader
        )
        return location_id

    @staticmethod
    def update_location(
        location: Location, location_name: str, user_id_location_leader: UUID
    ):
        """Update a location

        :param locatio: The location to update
        :param location_name: The (new) name of the location
        :param user_id_location_leader: The (new) ID of the location leader

        """
        if (
            location_name != location.location_name
            and LocationsRepository.get_location_by_name(location_name)
        ):
            raise LocationAlreadyExistsError(
                f"Standort {location_name} existiert bereits"
            )
        location.location_name = location_name
        location.user_id_location_leader = user_id_location_leader

        LocationsRepository.update_location(location)

    @staticmethod
    def delete_location(location: Location):
        """Delete a location

        :param location: The location to delete
        """

        LocationsRepository.delete_location(location)
