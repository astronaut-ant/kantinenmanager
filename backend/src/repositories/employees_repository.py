"""Repository to handle database operations for employee data."""

from sqlalchemy import select
from src.models.user import User
from src.database import db
from uuid import UUID
from src.models.user import UserGroup
from src.models.employee import Employee
from src.models.group import Group
from src.models.location import Location


class EmployeesRepository:
    """Repository to handle database operations for employee data."""

    @staticmethod
    def get_employees_by_user_scope(user_group: UserGroup, user_id: UUID) -> list:
        """Retrieve all employees the user has access to based on their user group and id.

        :param user_group: The user group of the user
        :param user_id: The ID of the user

        :return: A list of all employees the user has access to"""
        # TODO: Test this method

        if user_group == UserGroup.verwaltung:
            return db.session.scalars(select(Employee)).all()

        elif user_group == UserGroup.standortleitung:
            return db.session.scalars(
                select(Employee)
                .join(Group)
                .join(Location)
                .filter(Location.user_id_location_leader == user_id)
            ).all()

        elif user_group == UserGroup.gruppenleitung:
            return db.session.scalars(
                select(Employee)
                .join(Group)
                .filter(Group.user_id_groupleader == user_id)
            ).all()

        else:
            return []
