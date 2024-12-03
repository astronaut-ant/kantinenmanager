from sqlalchemy import select, func
from src.models.location import Location
from src.database import db
from uuid import UUID


class LocationsRepository:
    """Repository to handle database operations for location data."""

    @staticmethod
    def create_location(location: Location) -> UUID:
        """Create a new location in the database.

        :param location: The location to create

        :return: the ID of the new location
        """
        db.session.add(location)
        db.session.commit()
        return location.id

    @staticmethod
    def get_location_by_name(location_name: str) -> Location:
        """Get a location by its name.

        :param location_name: The name of the location to get

        :return: the location with the given name
        """
        return db.session.query(Location).filter(Location.name == location_name).first()
