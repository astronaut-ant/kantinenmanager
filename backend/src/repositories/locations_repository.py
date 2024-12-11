from sqlalchemy import select, func
from src.models.user import User
from src.database import db
from uuid import UUID
from src.models.location import Location
from src.models.group import Group
from typing import List, Optional


class LocationsRepository:
    """Repository to handle database operations for location data."""

    @staticmethod
    def get_locations() -> list[Location]:
        """Retrieve all locations

        :return: A list of all locations"""
        return db.session.scalars(select(Location)).all()

    @staticmethod
    def get_location_by_id(location_id: UUID) -> Location | None:
        """Retrieve a location by its ID

        :param location_id: The ID of the location to retrieve

        :return: The location with the given ID or None if no location was found
        """
        return db.session.scalars(
            select(Location).where(Location.id == location_id)
        ).first()

    @staticmethod
    def get_location_by_name(location_name: str) -> Location | None:
        """Retrieve a location by its name

        :param location_name: The name of the location to retrieve

        :return: The location with the given name or None if no location was found
        """
        return db.session.scalars(
            select(Location).where(Location.location_name == location_name)
        ).first()

    @staticmethod
    def get_user_by_id(user_id: UUID) -> User | None:
        """Retrieve a user by their ID

        :param user_id: The ID of the user to retrieve

        :return: The user with the given ID or None if no user was found
        """
        return db.session.scalars(select(User).where(User.id == user_id)).first()

    @staticmethod
    def create_location(location_name: str, user_id_location_leader: UUID) -> UUID:
        """Create a new location

        :param location_name: The name of the location
        :param user_id_location_leader: The ID of the location leader

        :return: The ID of the created location
        """
        new_location = Location(
            location_name=location_name, user_id_location_leader=user_id_location_leader
        )
        db.session.add(new_location)
        db.session.commit()
        return new_location.id

    @staticmethod
    def update_location(location: Location):
        """Update a location

        :param location: The location to update
        """
        db.session.commit()

    @staticmethod
    def delete_location(location: Location):
        """Delete a location

        :param location: The location to delete
        """
        db.session.delete(location)
        db.session.commit()

    @staticmethod
    def get_groups_of_location(location_id: UUID) -> List[Group]:
        """Retrieve all groups of a location

        :param location_id: The ID of the location

        :return: A list of all groups of the location
        """
        return db.session.scalars(
            select(Group).where(Group.location_id == location_id)
        ).all()
