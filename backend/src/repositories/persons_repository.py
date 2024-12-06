"""Repository to handle database operations for person data."""

from sqlalchemy import select, func
from src.models.user import User
from src.database import db
from uuid import UUID
from src.models.user import UserGroup
from src.models.person import Person


class PersonsRepository:
    """Repository to handle database operations for person data."""

    @staticmethod
    def get_person_by_id(person_id: UUID) -> Person | None:
        """Retrieve a person by their id

        :param person_id: The id of the person to retrieve

        :return: The person with the given id or None if no person was found
        """
        return db.session.scalars(select(Person).where(Person.id == person_id)).first()
