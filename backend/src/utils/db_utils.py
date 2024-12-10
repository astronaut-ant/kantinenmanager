from mocks.mock_orders_users import MOCK_ORDERS_USERS
from mocks.mock_employees import MOCK_EMPLOYEES
from mocks.mock_groups import MOCK_GROUPS
from mocks.mock_locations import MOCK_LOCATIONS
from mocks.mock_users import MOCK_USERS
from src.models.user import UserGroup
from src.services.employees_service import EmployeesService
from src.services.groups_service import GroupsService
from src.services.locations_service import LocationsService
from src.services.orders_service import OrdersService
from src.services.users_service import UsersService
from src.utils.exceptions import (
    EmployeeAlreadyExistsError,
    GroupAlreadyExists,
    LocationAlreadyExistsError,
    OrderAlreadyExistsForPersonAndDate,
    UserAlreadyExistsError,
)


def insert_mock_data(app):
    """Insert mock data into the database."""

    with app.app_context():
        insert_user_mock_data()
        insert_location_mock_data()
        update_user_location_mock_data()
        insert_group_mock_data()
        insert_employee_mock_data()
        insert_order_users_mock_data()


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
    standortleitung_user_dict = {
        user.username: user.id
        for user in UsersService.get_users()
        if user.user_group == UserGroup.standortleitung
    }

    for location in MOCK_LOCATIONS:
        name = location["location_name"]
        leader = standortleitung_user_dict[location["location_leader"]]

        try:
            location_id = LocationsService.create_location(name, leader)
            print(f"Inserted location with ID {location_id}")
        except LocationAlreadyExistsError:
            continue


def update_user_location_mock_data():
    """Update mock users with their location data in the database."""
    location_dict = {
        location.location_name: location
        for location in LocationsService.get_locations()
    }
    user_dict = {user.username: user for user in UsersService.get_users()}

    for mock_user in MOCK_USERS:
        user = user_dict[mock_user["username"]]
        location = location_dict[mock_user["location_name"]]

        UsersService.update_user(
            user=user,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            user_group=user.user_group,
            location=location,
        )
        # print(f"Updated user {user.username} with location {location.location_name}")


def insert_group_mock_data():
    """Insert mock group data into the database."""
    gruppenleitung_users_dict = {
        user.username: user.id
        for user in UsersService.get_users()
        if user.user_group == UserGroup.gruppenleitung
    }
    location_dict = {
        location.location_name: location.id
        for location in LocationsService.get_locations()
    }

    for group in MOCK_GROUPS:
        name = group["group_name"]
        leader = gruppenleitung_users_dict[group["group_leader"]]
        location_id = location_dict[group["location_name"]]

        replacement = None
        if replacement := group.get("replacement"):
            replacement = gruppenleitung_users_dict[replacement]

        try:
            group_id = GroupsService.create_group(
                name, leader, location_id, replacement
            )
            print(f"Inserted group with ID {group_id} and leader {leader}")
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


def insert_order_users_mock_data():
    """Insert mock orders for users."""
    users_dict = {user.username: user for user in UsersService.get_users()}

    for order in MOCK_ORDERS_USERS:
        user = users_dict[order["user"]]

        data = {
            "person_id": user.id,
            "location_id": user.location_id,
            "date": order["date"],
            "main_dish": order["main_dish"],
            "salad_option": order["salad_option"],
        }

        try:
            OrdersService.create_order_user(data, user.user_group, user.id)
            print(f"Inserted order for user {user.username}")

        except OrderAlreadyExistsForPersonAndDate:
            continue
