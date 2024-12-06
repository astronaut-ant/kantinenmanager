"""Service for handling employee management."""

import csv, re
from uuid import UUID
from src.services.auth_service import AuthService
from src.models.user import UserGroup
from src.models.employee import Employee
from src.repositories.employees_repository import EmployeesRepository
from src.utils.error import ErrMsg, abort_with_err
from typing import Optional
from src.utils.exceptions import (
    EmployeeAlreadyExistsError,
    GroupDoesNotExistError,
    EmployeeDoesNotExistError,
    NameNotAppropriateError,
    FileNotProcessableError,
)


class EmployeesService:
    """Service for handling employee management."""

    @staticmethod
    def get_employees(
        user_group: UserGroup,
        user_id: UUID,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        group_name: Optional[str] = None,
        group_id: Optional[UUID] = None,
    ) -> list[Employee]:
        """Get all employees the user has access to based on their user group and id."""

        return EmployeesRepository.get_employees_by_user_scope(
            user_group,
            user_id,
            first_name=first_name,
            last_name=last_name,
            group_name=group_name,
            group_id=group_id,
        )

    @staticmethod
    def get_employee_by_id(
        employee_id: UUID, user_group: UserGroup, user_id: UUID
    ) -> Employee | None:
        """Retrieve an employee by their ID

        :param employee_id: The ID of the employee to retrieve

        :return: The employee with the given ID or None if no employee was found
        """

        return EmployeesRepository.get_employee_by_id_by_user_scope(
            employee_id, user_group, user_id
        )

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
        return EmployeesRepository.create_employee(employee)

    @staticmethod
    def update_employee(
        employee: Employee,
        first_name: str,
        last_name: str,
        employee_number: int,
        group_name: str,
        location_name: str,
    ):
        """Update an employee in the database.

        :param user: The employee to update
        :param first_name: The new first name of the employee
        :param last_name: The new last name of the employee
        :param employee_number: The new number of the employee
        :param group_name: The new group of the employee
        :param location_name: The new location of the employee
        """

        if (
            employee_number != employee.employee_number
            and EmployeesRepository.get_user_by_employee_number(employee_number)
        ):
            raise EmployeeAlreadyExistsError(
                f"User with employee number {employee_number} already exists"
            )

        employee.first_name = first_name
        employee.last_name = last_name
        employee.employee_number = employee_number
        employee.group = EmployeesRepository.get_group_by_name_and_location(
            group_name, location_name
        )

        EmployeesRepository.update_employee(employee)

    @staticmethod
    def delete_employee(employee: Employee):
        """Delete an employee from the database.

        :param eemployee: The employee to delete
        """

        EmployeesRepository.delete_employee(employee)

    @staticmethod
    def bulk_create_employees(file):
        """Creates new Emplyoees from a csv-file with utf-8 and komma or iso-8859-1 with semicolons

        :param reader: The File in csv-format
        """

        try:
            file.stream.seek(0)
            reader = csv.DictReader(file.stream.read().decode("utf-8").splitlines())
        except UnicodeDecodeError:
            file.stream.seek(0)
            reader = csv.DictReader(
                file.stream.read().decode("iso-8859-1").splitlines(), delimiter=";"
            )

        employees = []

        for row in reader:
            print(row)
            if (
                not row.get("Kunden-Nr.")
                or not row.get("Kürzel")
                or not row.get("Bereich")
                or not row.get("Gruppe-Nr.")
                or not row.get("Gruppen-Name 1")
                or not row.get("Gruppen-Name 2")
            ):
                abort_with_err(
                    ErrMsg(
                        status_code=400,
                        title="Falsche Daten oder unlesbares Format",
                        description="Die Daten in der CSV entsprechen nicht der normalen Vorlage",
                    )
                )

            match = re.match(r"([A-Z][a-z]+)([A-Z][a-z]*[1-9]*)", row["Kürzel"])
            if match:
                firstname = match.group(1)
                lastname = match.group(2)
            else:
                print("Zeile: ", row)
                abort_with_err(
                    ErrMsg(
                        status_code=422,
                        title="Vorname und Nachname nicht trennbar",
                        description="Es konnte kein eindeutiger Vor- und Nachname erkannt werden",
                    )
                )

            if len(firstname) < 64 and len(lastname) < 64:

                group = EmployeesRepository.get_group_by_name_and_location(
                    row["Gruppen-Name 1"], row["Bereich"]
                )
                print(group)
                if group is None:
                    raise GroupDoesNotExistError

                if EmployeesRepository.get_employee_by_number(row["Kunden-Nr."]):
                    raise EmployeeAlreadyExistsError

                first_name = firstname
                last_name = lastname
                employee_number = row["Kunden-Nr."]

                employee = Employee(
                    first_name=first_name,
                    last_name=last_name,
                    employee_number=employee_number,
                    group_id=group.id,
                )
                employees.append(employee)
            else:
                abort_with_err(
                    ErrMsg(
                        status_code=422,
                        title="Zu langer Name",
                        description="Sowohl Vorname als auch Nachname dürfen nicht länger als 64 Zeichen sein",
                    )
                )

        EmployeesRepository.bulk_create_employees(employees)

        return {
            "message": "Mitarbeiter erfolgreich erstellt",
            "count": len(employees),
        }
