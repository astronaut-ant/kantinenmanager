from datetime import datetime, time
from typing import List
from zoneinfo import ZoneInfo
from mocks.mock_daily_orders import (
    MOCK_DAILY_ORDERS_EMPLOYEES,
    MOCK_DAILY_ORDERS_USERS,
)
from src.models.dailyorder import DailyOrder
from src.services.daily_orders_service import DailyOrdersService
from mocks.mock_orders_employees import MOCK_ORDERS_EMPLOYEES
from mocks.mock_orders_users import MOCK_ORDERS_USERS
from mocks.mock_employees import MOCK_EMPLOYEES
from mocks.mock_groups import MOCK_GROUPS
from mocks.mock_locations import MOCK_LOCATIONS
from mocks.mock_users import MOCK_USERS
from src.models.user import UserGroup
from src.services.employees_service import EmployeesService
from src.services.groups_service import GroupsService
from src.services.locations_service import LocationsService
from src.services.pre_orders_service import PreOrdersService
from src.repositories.orders_repository import OrdersFilters
from src.services.users_service import UsersService
from src.utils.exceptions import AlreadyExistsError


def insert_mock_data(app):
    """Insert mock data into the database."""

    with app.app_context():
        insert_user_mock_data()
        insert_location_mock_data()
        update_user_location_mock_data()
        insert_group_mock_data()
        insert_employee_mock_data()
        insert_order_users_mock_data()
        insert_order_employees_mock_data()
        insert_daily_orders_mock_data()


def insert_user_mock_data():
    """Insert mock user data into the database."""

    for user in MOCK_USERS:
        try:
            user_id, _ = UsersService.create_user(
                first_name=user["first_name"],
                last_name=user["last_name"],
                username=user["username"],
                password=user["password"],
                user_group=user["user_group"],
            )
            print(f"Inserted user with ID {user_id}")
        except AlreadyExistsError:
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
        except AlreadyExistsError:
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
                group_name=name,
                group_number=group["index"],
                user_id_group_leader=leader,
                location_id=location_id,
                user_id_replacement=replacement,
            )
            print(f"Inserted group with ID {group_id} and leader {leader}")
        except AlreadyExistsError:
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
        except AlreadyExistsError:
            continue


def insert_order_users_mock_data():
    """Insert mock orders for users."""
    users_dict = {user.username: user for user in UsersService.get_users()}

    for block in MOCK_ORDERS_USERS:
        date = datetime.now().date() + block["timedelta"]
        if date.weekday() >= 5:
            # Not a workday
            continue

        orders = block["orders"]
        if len(orders) == 0:
            continue

        first_user = users_dict[orders[0]["user"]]
        existing_orders = PreOrdersService.get_pre_orders(
            OrdersFilters(date=date, person_id=first_user.id),
            user_id=first_user.id,
            user_group=first_user.user_group,
        )
        if len(existing_orders) > 0:
            # Orders for this date already exist
            continue

        for order in orders:
            user = users_dict[order["user"]]
            data = {
                "date": date,
                "location_id": user.location_id,
                "main_dish": order["main_dish"],
                "salad_option": order["salad_option"],
                "person_id": user.id,
                "nothing": order["nothing"],
            }

            try:
                PreOrdersService.create_preorder_user(data, user.id)
                print(f"Inserted order for user {user.username}")

            except Exception as e:
                print(f"Failed to insert order for user {user.username}: {e}")
                continue


def insert_order_employees_mock_data():
    """Insert mock orders for employees."""
    admin = UsersService.get_user_by_username("admin")

    employees_dict = {
        employee.employee_number: employee
        for employee in EmployeesService.get_employees(UserGroup.verwaltung, admin.id)
    }
    groups_dict = {
        group.id: group
        for group in GroupsService.get_groups(admin.id, UserGroup.verwaltung)
    }

    for block in MOCK_ORDERS_EMPLOYEES:
        date = datetime.now().date() + block["timedelta"]
        if date.weekday() >= 5:
            # Not a workday
            continue

        orders = block["orders"]
        if len(orders) == 0:
            continue

        first_employee = employees_dict[orders[0]["employee_number"]]

        existing_orders = PreOrdersService.get_pre_orders(
            OrdersFilters(date=date, person_id=first_employee.id),
            user_id=admin.id,
            user_group=admin.user_group,
        )
        if len(existing_orders) > 0:
            # Orders for this date already exist
            continue

        for order in orders:
            employee = employees_dict[order["employee_number"]]
            group = groups_dict[employee.group_id]

            data = {
                "date": date,
                "location_id": group.location_id,
                "main_dish": order["main_dish"],
                "nothing": order["nothing"],
                "person_id": employee.id,
                "salad_option": order["salad_option"],
            }

            try:
                PreOrdersService.create_update_bulk_preorders(
                    [data], group.user_id_replacement or group.user_id_group_leader
                )
            except Exception as e:
                print(
                    f"Failed to insert order for employee {employee.employee_number}: {e}"
                )
                continue


def insert_daily_orders_mock_data():
    """Insert mock daily orders."""

    if datetime.now(tz=ZoneInfo("Europe/Berlin")).time() < time(8, 2):
        print("Skipping daily orders insertion before 8:02 to avoid conflicts")
        return

    admin = UsersService.get_user_by_username("admin")

    if len(DailyOrdersService.get_all_daily_orders()) > 0:
        return

    user_dict = {user.username: user for user in UsersService.get_users()}

    employees_dict = {
        employee.employee_number: employee
        for employee in EmployeesService.get_employees(UserGroup.verwaltung, admin.id)
    }

    groups_dict = {
        group.id: group
        for group in GroupsService.get_groups(admin.id, UserGroup.verwaltung)
    }

    date = datetime.now().date()

    orders: List[DailyOrder] = []

    for order in MOCK_DAILY_ORDERS_USERS:
        person = user_dict[order["user"]]

        orders.append(
            DailyOrder(
                person_id=person.id,
                location_id=person.location_id,
                date=date,
                main_dish=order["main_dish"],
                salad_option=order["salad_option"],
                nothing=order["nothing"],
            )
        )

    for order in MOCK_DAILY_ORDERS_EMPLOYEES:
        person = employees_dict[order["employee_number"]]
        location = groups_dict[person.group_id].location_id

        orders.append(
            DailyOrder(
                person_id=person.id,
                location_id=location,
                date=date,
                main_dish=order["main_dish"],
                salad_option=order["salad_option"],
                nothing=order["nothing"],
            )
        )

    DailyOrdersService.create_daily_orders(orders)

    print(f"Inserted {len(orders)} daily orders for persons")
