"""Repository to handle database operations for employee data."""

from sqlalchemy import select, func
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
    def get_employees_by_user_scope(
        user_group: UserGroup, user_id: UUID
    ) -> list[Employee]:
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

    @staticmethod
    def get_employee_by_number(employee_number: int) -> Employee | None:
        """Retrieve an employee by their employee number

        :param employee_number: The organisational number (not system uuid) of the employee to retrieve

        :return: The employee with the given employee number or None if no employee was found
        """
        return db.session.scalars(
            select(Employee).where(Employee.employee_number == employee_number)
        ).first()

    @staticmethod
    def get_group_by_name_and_location(
        group_name: str, location_name: str
    ) -> Group | None:
        """Retrieve a goup by their group name and name of the location they belong to

        :param group_name: The name of the group the employee is working at
        :param location_name: The name of the location the employee is working at

        :return: The group with the given name at the given location or None if no group was found
        """
        return db.session.scalars(
            select(Group)
            .join(Location)
            .where(func.lower(Group.group_name) == group_name.lower())
            .where(func.lower(Location.location_name) == location_name.lower())
        ).first()

    @staticmethod
    def get_employee_by_id_by_user_scope(
        employee_id: UUID, user_group: UserGroup, user_id: UUID
    ) -> Employee | None:
        """Retrieve an employee by their ID

        :param employee_id: The ID of the employee to retrieve

        :return: The employee with the given ID or None if no employee was found
        """
        if user_group == UserGroup.verwaltung:
            return db.session.scalars(
                select(Employee).where(Employee.id == employee_id)
            ).first()

        elif user_group == UserGroup.standortleitung:
            return db.session.scalars(
                select(Employee)
                .join(Group)
                .join(Location)
                .filter(Location.user_id_location_leader == user_id)
                .where(Employee.id == employee_id)
            ).first()

        elif user_group == UserGroup.gruppenleitung:
            return db.session.scalars(
                select(Employee)
                .join(Group)
                .filter(Group.user_id_groupleader == user_id)
                .where(Employee.id == employee_id)
            ).first()

        else:
            None

    @staticmethod
    def create_employee(employee: Employee):
        """Create a new employee in the database"""
        db.session.add(employee)
        db.session.commit()

        return employee.id
