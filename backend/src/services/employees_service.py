"""Service for handling employee management."""

from uuid import UUID
from src.services.auth_service import AuthService
from src.models.user import UserGroup
from src.models.employee import Employee
from src.repositories.employees_repository import EmployeesRepository


class EmployeeAlreadyExistsError(Exception):
    """Exception raised when an employee number already exists."""

    pass


class GroupDoesNotExistError(Exception):
    """Exception raised when a group does not exist at a given location."""

    pass


class EmployeesService:
    """Service for handling employee management."""

    @staticmethod
    def get_employees(user_group: UserGroup, user_id: UUID) -> list[Employee]:
        """Get all employees the user has access to based on their user group and id."""

        return EmployeesRepository.get_employees_by_user_scope(user_group, user_id)

    @staticmethod
    def get_employee_by_id(employee_id: UUID) -> Employee | None:
        """Retrieve an employee by their ID

        :param employee_id: The ID of the employee to retrieve

        :return: The employee with the given ID or None if no employee was found
        """

        return EmployeesRepository.get_employee_by_id_by_user_scope(employee_id)

    @staticmethod
    def create_employee(
        first_name: str,
        last_name: str,
        employee_number: int,
        group_name: str,
        location_name: str,
    ) -> UUID:
        """Create a new employee in the database.

        :param first_name: The first name of the new employee
        :param last_name: The last name of the new employee
        :param employee_number: The employee number of the new employee
        :param group_name: The name of the group the employee belongs to
        :param location_name: The name of the location the employee belongs to

        :return: the ID of the new employee

        :raises EmployeeAlreadyExistsError: If an employee with the given employee_number already exists
        :raises GroupDoesNotExistError: If the group does not exist at the given location
        """

        if EmployeesRepository.get_employee_by_number(employee_number):
            raise EmployeeAlreadyExistsError(
                f"Employee with number {employee_number} already exists"
            )

        group = EmployeesRepository.get_group_by_name_and_location(
            group_name, location_name
        )
        if not group:
            raise GroupDoesNotExistError(
                f"Group {group_name} at location {location_name} does not exist"
            )

        employee = Employee(
            first_name=first_name,
            last_name=last_name,
            employee_number=employee_number,
            group_id=group.id,
        )

        id = EmployeesRepository.create_employee(employee)

        return id
