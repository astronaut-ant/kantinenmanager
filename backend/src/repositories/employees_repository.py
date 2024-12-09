"""Repository to handle database operations for employee data."""

from sqlalchemy import select, func, or_
from src.models.user import User
from src.database import db
from uuid import UUID
from src.models.user import UserGroup
from src.models.employee import Employee
from src.models.group import Group
from src.models.location import Location
from typing import List, Optional


class EmployeesRepository:
    """Repository to handle database operations for employee data."""

    @staticmethod
    def get_employees_by_user_scope(
        user_group: UserGroup,
        user_id: UUID,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        group_name: Optional[str] = None,
        group_id: Optional[UUID] = None,
        employee_number: Optional[int] = None,
    ) -> List[Employee]:
        """Retrieve all employees the user has access to based on their user group and id.

        :param user_group: The user group of the user
        :param user_id: The ID of the user
        :param first_name: The first name of the employee to retrieve (optional)
        :param last_name: The last name of the employee to retrieve (optional)

        :return: A list of all employees the user has access to and that fit the optional name parameters
        """
        if user_group in [
            UserGroup.verwaltung,
            UserGroup.standortleitung,
            UserGroup.gruppenleitung,
        ]:
            query = select(Employee)

            if user_group == UserGroup.verwaltung:
                query = query
            elif user_group == UserGroup.standortleitung:
                query = (
                    query.join(Group)
                    .join(Location)
                    .filter(Location.user_id_location_leader == user_id)
                )
            elif user_group == UserGroup.gruppenleitung:
                query = query.join(Group).filter(
                    or_(
                        Group.user_id_group_leader == user_id,
                        Group.user_id_replacement == user_id,
                    )
                )

            if first_name:
                query = query.filter(
                    func.lower(Employee.first_name) == first_name.lower()
                )
            if last_name:
                query = query.filter(
                    func.lower(Employee.last_name) == last_name.lower()
                )
            if group_name:
                query = query.join(Group).filter(
                    func.lower(Group.group_name) == group_name.lower()
                )
            if group_id:
                query = query.filter(Employee.group_id == group_id)
            if employee_number:
                query = query.filter(Employee.employee_number == employee_number)

            return db.session.scalars(query).all()
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
            .where(
                func.lower(Group.group_name) == group_name.lower(),
                func.lower(Location.location_name) == location_name.lower(),
            )
        ).first()

    @staticmethod
    def get_employee_by_id_by_user_scope(
        employee_id: UUID, user_group: UserGroup, user_id: UUID
    ) -> Employee | None:
        """Retrieve an employee by their ID

        :param employee_id: The ID of the employee to retrieve

        :return: The employee with the given ID or None if no employee was found
        """
        if (
            user_group == UserGroup.verwaltung
            or user_group == UserGroup.kuechenpersonal
        ):
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
    def get_employee_by_name_by_user_scope(
        first_name: str, last_name: str, user_group: UserGroup, user_id: UUID
    ) -> Employee | None:
        """Retrieve an employee by their name

        :param first_name: The first name of the employee to retrieve
        :param last_name: The last name of the employee to retrieve

        :return: The employee with the given name or None if no employee was found
        """
        if (
            user_group == UserGroup.verwaltung
            or user_group == UserGroup.kuechenpersonal
        ):
            return db.session.scalars(
                select(Employee)
                .where(Employee.first_name == first_name)
                .where(Employee.last_name == last_name)
            ).first()

        elif user_group == UserGroup.standortleitung:
            return db.session.scalars(
                select(Employee)
                .join(Group)
                .join(Location)
                .filter(Location.user_id_location_leader == user_id)
                .where(Employee.first_name == first_name)
                .where(Employee.last_name == last_name)
            ).first()

        elif user_group == UserGroup.gruppenleitung:
            return db.session.scalars(
                select(Employee)
                .join(Group)
                .filter(Group.user_id_groupleader == user_id)
                .where(Employee.first_name == first_name)
                .where(Employee.last_name == last_name)
            ).first()

        else:
            None

    @staticmethod
    def create_employee(employee: Employee) -> UUID:
        """Create a new employee in the database"""
        db.session.add(employee)
        db.session.commit()

        return employee.id

    @staticmethod
    def get_user_by_employee_number(employee_number: int) -> Employee | None:
        """Retrieve the employee associated with an employee number

        :param employee_number: The employee number of the employee

        :return: The employee associated with the given employee number or None if no employee was found
        """
        return db.session.scalars(
            select(Employee).where(Employee.employee_number == employee_number)
        ).first()

    @staticmethod
    def update_employee(employee: Employee):
        """Update an employee in the database"""

        # SQLAlchemy automatically tracks changes to objects
        # we only need to commit the session to save the changes

        db.session.commit()

    @staticmethod
    def delete_employee(employee: Employee):
        """Delete a employee from the database"""

        db.session.delete(employee)
        db.session.commit()

    @staticmethod
    def bulk_create_employees(employees: Employee):
        """Create a bunch of new employees in the database

        :param employees: List of the Employees which will be created
        """
        for employee in employees:
            db.session.add(employee)

        db.session.commit()
