from uuid import UUID
from typing import List, Optional
from src.models.group import Group
from src.models.location import Location
from src.repositories.locations_repository import LocationsRepository
from src.repositories.users_repository import UsersRepository
from src.utils.exceptions import (
    LocationAlreadyExistsError,
    LeaderDoesNotExist,
    NotFoundError,
)


class LocationsService:
    """Service for handling location management."""

    @staticmethod
    def get_locations(prejoin_location_leader=False) -> list[Location]:
        """Get all locations."""

        return LocationsRepository.get_locations(
            prejoin_location_leader=prejoin_location_leader
        )

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

        location_leader = UsersRepository.get_user_by_id(user_id_location_leader)
        if not location_leader:
            raise LeaderDoesNotExist(
                f"Gruppenleiter mit ID {user_id_location_leader} existiert nicht"
            )
        if LocationsRepository.get_location_by_leader(location_leader.id):
            raise LocationAlreadyExistsError(
                f"User {location_leader.username} ist bereits Standortleiter"
            )

        location_id = LocationsRepository.create_location(
            location_name, user_id_location_leader
        )
        return location_id

    @staticmethod
    def update_location(
        location_id: UUID, location_name: str, user_id_location_leader: UUID
    ) -> Location:
        """Update a location

        :param locatio_id: ID of the location to update
        :param location_name: The (new) name of the location
        :param user_id_location_leader: The (new) ID of the location leader

        :return: The updated location
        """
        location = LocationsService.get_location_by_id(location_id)

        if location == None:
            raise NotFoundError

        if (
            location_name != location.location_name
            and LocationsRepository.get_location_by_name(location_name)
        ):
            raise LocationAlreadyExistsError(
                f"Ein anderer Standort mit Name {location_name} existiert bereits."
            )

        if (
            user_id_location_leader != location.user_id_location_leader
            and LocationsRepository.get_location_by_leader(user_id_location_leader)
        ):
            raise LocationAlreadyExistsError(
                f"User mit ID {user_id_location_leader} ist bereits Standortleiter eines anderen Standorts."
            )

        location.location_name = location_name
        location.user_id_location_leader = user_id_location_leader

        LocationsRepository.update_location(location)

        return location

    @staticmethod
    def delete_location(location: Location):
        """Delete a location

        :param location: The location to delete
        """

        LocationsRepository.delete_location(location)

    @staticmethod
    def get_groups_of_location(location_id: UUID) -> Optional[List[Group]]:
        """Get all groups of a location

        :param location_id: The ID of the location
        :return: The groups of the location
        """

        return LocationsRepository.get_groups_of_location(location_id)
