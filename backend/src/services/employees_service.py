"""Service for handling employee management."""

import csv
import re
from uuid import UUID
from src.models.user import UserGroup
from src.models.employee import Employee
from src.repositories.employees_repository import EmployeesRepository
from src.utils.error import ErrMsg, abort_with_err
from typing import Optional, List
from src.utils.exceptions import AlreadyExistsError, NotFoundError
from src.utils.pdf_creator import PDFCreationUtils


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
        employee_number: Optional[int] = None,
    ) -> list[Employee]:
        """Get all employees the user has access to based on their user group and id."""

        return EmployeesRepository.get_employees_by_user_scope(
            user_group,
            user_id,
            first_name=first_name,
            last_name=last_name,
            group_name=group_name,
            group_id=group_id,
            employee_number=employee_number,
        )

    @staticmethod
    def get_employee_by_id(
        employee_id: UUID, user_group: UserGroup, user_id: UUID
    ) -> Employee | None:
        """Retrieve an employee by their ID

        :param employee_id: The ID of the employee to retrieve

        :return: The employee with the given ID or None if no employee was found
        """

        employee = EmployeesRepository.get_employee_by_id_by_user_scope(
            employee_id, user_group, user_id
        )
        if not employee:
            raise NotFoundError(f"Mitarbeiter:in mit ID {employee_id}")
        return employee

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

        :raises AlreadyExistsError: If an employee with the given employee_number already exists
        :raises NotFoundError: If the group does not exist at the given location
        """

        if EmployeesRepository.get_employee_by_number(employee_number):
            raise AlreadyExistsError(ressource=f"Mitarbeiter:in {employee_number}")

        group = EmployeesRepository.get_group_by_name_and_location(
            group_name, location_name
        )
        if not group:
            raise NotFoundError(f"Gruppe '{group_name}' am Standort {location_name}")

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
            raise AlreadyExistsError(ressource=f"Mitarbeiter:in {employee_number}")

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

            match = re.match(
                r"([A-ZÄÖÜ][a-zäöüß0-9]+(?:[-][A-ZÄÖÜ][a-zäöüß0-9]+)*)([A-ZÄÖÜ][a-zäöüß0-9]+(?:[-][A-ZÄÖÜ][a-zäöüß0-9]+)*)?([A-ZÄÖÜ][a-zäöüß0-9]+(?:[-][A-ZÄÖÜ][a-zäöüß0-9]+)*)?([A-ZÄÖÜ][a-zäöüß0-9]+(?:[-][A-ZÄÖÜ][a-zäöüß0-9]+)*)?([A-ZÄÖÜ][a-zäöüß0-9]+(?:[-][A-ZÄÖÜ][a-zäöüß0-9]+)*)?((?:[A-Z][a-zäöüß0-9]+)(?:[-][A-Za-z0-9äöüß]+)*)",
                row["Kürzel"],
            )
            if match:
                firstname = match.group(1)
                if match.group(2):
                    firstname += " " + match.group(2)
                    if match.group(3):
                        firstname += " " + match.group(3)
                        if match.group(4):
                            firstname += " " + match.group(4)
                            if match.group(5):
                                firstname += " " + match.group(5)
                lastname = match.group(6)
            else:
                abort_with_err(
                    ErrMsg(
                        status_code=422,
                        title="Vorname und Nachname nicht trennbar",
                        description="Es konnte kein eindeutiger Vor- und Nachname erkannt werden",
                    )
                )

            if len(firstname) < 64 and len(lastname) < 64:
                group_name = (
                    re.match(
                        r"^([A-Za-zäöüÄÖÜß']+(?:[\s][A-Za-zäöüÄÖÜß']+)*)(\s-\s)*+",
                        row["Gruppen-Name 1"],
                    )
                ).group(1)
                group = EmployeesRepository.get_group_by_name_and_location(
                    group_name, row["Bereich"]
                )
                if group is None:
                    raise NotFoundError(f"Gruppe {row['Gruppen-Name 1']}")

                if EmployeesRepository.get_employee_by_number(row["Kunden-Nr."]):
                    raise AlreadyExistsError(
                        ressource=f"Mitarbeiter:in {row['Kunden-Nr.']}"
                    )

                employee = Employee(
                    first_name=firstname,
                    last_name=lastname,
                    employee_number=row["Kunden-Nr."],
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
            "message": "Mitarbeiter:innen erfolgreich erstellt",
            "count": len(employees),
        }

    @staticmethod
    def get_qr_code_for_all_employees_by_user_scope(
        user_group: UserGroup, user_id: UUID
    ):
        employees = EmployeesRepository.get_employees_by_user_scope(
            user_group=user_group, user_id=user_id
        )
        if not employees:
            raise NotFoundError("Mitarbeiter:innen")
        return PDFCreationUtils.create_batch_qr_codes(employees=employees)

    @staticmethod
    def get_qr_code_for_employees_list(
        employee_ids: List[UUID], user_group: UserGroup, user_id: UUID
    ):
        employees: List[Employee] = []

        for id in employee_ids:
            employee = EmployeesRepository.get_employee_by_id_by_user_scope(
                employee_id=id, user_group=user_group, user_id=user_id
            )
            if not employee:
                raise NotFoundError(f"Mitarbeiter:in mit ID {id}")
            employees.append(employee)

        if not employees:
            raise NotFoundError("Leere List oder Mitarbeiter:innen")
        return PDFCreationUtils.create_batch_qr_codes(employees=employees)
