import random

from mocks.mock_employees import MOCK_EMPLOYEES
from mocks.mock_groups import MOCK_GROUPS
from mocks.mock_locations import MOCK_LOCATIONS
from mocks.mock_users import MOCK_USERS
from src.models.user import UserGroup
from src.services.employees_service import EmployeesService
from src.services.groups_service import GroupsService
from src.services.locations_service import LocationsService
from src.services.users_service import UsersService
from src.utils.exceptions import (
    EmployeeAlreadyExistsError,
    GroupAlreadyExists,
    LocationAlreadyExistsError,
    UserAlreadyExistsError,
)


def insert_mock_data(app):
    """Insert mock data into the database."""

    with app.app_context():
        insert_user_mock_data()
        insert_location_mock_data()
        insert_group_mock_data()
        insert_employee_mock_data()


def insert_user_mock_data():
    """Insert mock user data into the database."""

    for user in MOCK_USERS:
        try:
            user_id, _ = UsersService.create_user(
                user["first_name"],
                user["last_name"],
                user["username"],
                user["password"],
                user["user_group"],
            )
            print(f"Inserted user with ID {user_id}")
        except UserAlreadyExistsError:
            continue


def insert_location_mock_data():
    """Insert mock location data into the database.

    Leaders are randomly assigned from the list of standortleitung users.
    """
    standortleitung_users = list(
        filter(
            lambda u: u.user_group == UserGroup.standortleitung,
            UsersService.get_users(),
        )
    )

    for location in MOCK_LOCATIONS:
        name = location["location_name"]
        random_leader = random.choice(standortleitung_users).id

        try:
            location_id = LocationsService.create_location(name, random_leader)
            print(f"Inserted location with ID {location_id}")
        except LocationAlreadyExistsError:
            continue


def insert_group_mock_data():
    """Insert mock group data into the database."""
    gruppenleitung_users = list(
        filter(
            lambda u: u.user_group == UserGroup.gruppenleitung, UsersService.get_users()
        )
    )
    location_dict = {
        location.location_name: location.id
        for location in LocationsService.get_locations()
    }

    for group in MOCK_GROUPS:
        name = group["group_name"]
        leader = random.choice(gruppenleitung_users).id
        location_id = location_dict[group["location_name"]]

        try:
            group_id = GroupsService.create_group(name, leader, location_id)
            print(f"Inserted group with ID {group_id}")
        except GroupAlreadyExists:
            continue


def insert_employee_mock_data():
    """Insert mock employee data into the database."""

    for employee in MOCK_EMPLOYEES:
        try:
            employee_id = EmployeesService.create_employee(
                employee["first_name"],
                employee["last_name"],
                employee["employee_number"],
                employee["group_name"],
                employee["location_name"],
            )
            print(f"Inserted employee with ID {employee_id}")
        except EmployeeAlreadyExistsError:
            continue
