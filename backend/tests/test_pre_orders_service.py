"""Tests for the PreOrdersService class"""

import pytest
import uuid
from datetime import datetime, timedelta
from .helper import *  # for fixtures # noqa: F403
from src.services.pre_orders_service import PreOrdersService
from src.repositories.orders_repository import OrdersFilters, OrdersRepository
from src.repositories.users_repository import UsersRepository
from src.repositories.employees_repository import EmployeesRepository
from src.repositories.groups_repository import GroupsRepository
from src.models.user import UserGroup
from src.models.maindish import MainDish
from src.schemas.pre_orders_schemas import (
    PreOrderFullSchema,
    PreOrdersByGroupLeaderSchema,
)
from src.utils.exceptions import (
    AlreadyExistsError,
    NotFoundError,
    AccessDeniedError,
    ActionNotPossibleError,
    BadValueError,
)


def describe_get_pre_order_by_id():
    def it_returns_pre_order_if_found(
        mocker,
        user_verwaltung,
        pre_order,
        employee,
    ):
        pre_order.person = employee
        employee.type = "employee"

        mock_get_by_id = mocker.patch.object(
            OrdersRepository, "get_pre_order_by_id", return_value=pre_order
        )
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_verwaltung
        )

        pre_order_res = PreOrdersService.get_pre_order_by_id(
            pre_order.id, user_verwaltung.id, UserGroup.verwaltung
        )

        assert pre_order_res == PreOrderFullSchema().dump(pre_order)
        mock_get_by_id.assert_called_once_with(pre_order.id)

    def it_raises_not_found_error_if_preorder_missing(
        mocker,
        user_verwaltung,
        employee,
    ):
        mocker.patch.object(OrdersRepository, "get_pre_order_by_id", return_value=None)
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_verwaltung
        )

        with pytest.raises(NotFoundError):
            PreOrdersService.get_pre_order_by_id(
                9999, user_verwaltung.id, UserGroup.verwaltung
            )

    def it_raises_access_denied_error_if_kuechenpersonal_wrong_location(
        mocker,
        user_kuechenpersonal,
        pre_order,
        employee,
    ):
        pre_order.person = employee
        employee.type = "employee"

        mocker.patch.object(
            OrdersRepository, "get_pre_order_by_id", return_value=pre_order
        )
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_kuechenpersonal
        )

        with pytest.raises(AccessDeniedError):
            PreOrdersService.get_pre_order_by_id(
                pre_order.id, user_kuechenpersonal.id, UserGroup.kuechenpersonal
            )

    def it_raises_access_denied_error_if_gruppenleitung_wrong_group(
        mocker,
        user_gruppenleitung,
        pre_order,
        employee,
        group,
    ):
        pre_order.person = employee
        employee.group_id = uuid.uuid4()
        employee.type = "employee"

        group.group_leader = user_gruppenleitung

        mocker.patch.object(
            OrdersRepository, "get_pre_order_by_id", return_value=pre_order
        )
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_gruppenleitung
        )

        with pytest.raises(AccessDeniedError):
            PreOrdersService.get_pre_order_by_id(
                pre_order.id, user_gruppenleitung.id, UserGroup.gruppenleitung
            )

    def it_raises_access_denied_error_if_user_not_own(
        mocker,
        user_verwaltung,
        pre_order,
        user_kuechenpersonal,
    ):
        pre_order.person = user_kuechenpersonal
        user_kuechenpersonal.type = "user"

        mocker.patch.object(
            OrdersRepository, "get_pre_order_by_id", return_value=pre_order
        )
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_verwaltung
        )

        with pytest.raises(AccessDeniedError):
            PreOrdersService.get_pre_order_by_id(
                pre_order.id, user_verwaltung.id, UserGroup.verwaltung
            )

    def it_returns_pre_order_for_user_if_own_order(
        mocker,
        user_verwaltung,
        pre_order,
    ):
        pre_order.person = user_verwaltung
        user_verwaltung.type = "user"

        mock_get_by_id = mocker.patch.object(
            OrdersRepository, "get_pre_order_by_id", return_value=pre_order
        )
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_verwaltung
        )

        res = PreOrdersService.get_pre_order_by_id(
            pre_order.id, user_verwaltung.id, UserGroup.verwaltung
        )

        assert res == PreOrderFullSchema().dump(pre_order)
        mock_get_by_id.assert_called_once_with(pre_order.id)


def describe_get_pre_orders_by_group_leader():
    def it_raises_not_found_error_if_group_leader_not_exists(
        mocker,
        user_gruppenleitung,
    ):
        mocker.patch.object(UsersRepository, "get_user_by_id", return_value=None)

        with pytest.raises(NotFoundError):
            PreOrdersService.get_pre_orders_by_group_leader(
                user_gruppenleitung.id, user_gruppenleitung.id, UserGroup.gruppenleitung
            )

    def it_returns_pre_orders_for_all_groups_of_leader(
        mocker,
        user_verwaltung,
        user_gruppenleitung,
        group,
        group_alt,
        employees,
        employees_alt,
        pre_orders,
        pre_orders_alt,
    ):

        for pre_order in pre_orders:
            pre_order.last_changed = None
        for pre_order in pre_orders_alt:
            pre_order.last_changed = None

        group.group_leader = user_gruppenleitung
        group.user_id_group_leader = user_gruppenleitung.id
        group.group_leader_replacement = None
        group_alt.group_leader_replacement = user_gruppenleitung
        group_alt.user_id_replacement = user_gruppenleitung.id
        group_alt.group_leader = user_verwaltung

        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_gruppenleitung
        )
        mock_group_return = mocker.patch.object(
            GroupsRepository,
            "get_groups_by_group_leader",
            return_value=[
                {
                    "id": group.id,
                    "group_name": group.group_name,
                    "group_number": group.group_number,
                    "is_home_group": True,
                },
                {
                    "id": group_alt.id,
                    "group_name": group_alt.group_name,
                    "group_number": group_alt.group_number,
                    "is_home_group": False,
                },
            ],
        )
        mock_employee_group = mocker.patch.object(
            EmployeesRepository,
            "get_employees_by_user_scope",
            side_effect=[employees, employees_alt],
        )
        mocker.patch.object(
            OrdersRepository,
            "get_pre_orders",
            side_effect=[pre_orders, pre_orders_alt],
        )

        res = PreOrdersService.get_pre_orders_by_group_leader(
            user_gruppenleitung.id, user_gruppenleitung.id, UserGroup.gruppenleitung
        )

        mock_group_return.assert_called_once_with(user_gruppenleitung.id)
        mock_employee_group.assert_has_calls(
            [
                mocker.call(
                    user_group=UserGroup.gruppenleitung,
                    user_id=user_gruppenleitung.id,
                    group_id=group.id,
                ),
                mocker.call(
                    user_group=UserGroup.gruppenleitung,
                    user_id=user_gruppenleitung.id,
                    group_id=group_alt.id,
                ),
            ]
        )
        replystring = {
            "first_name": user_gruppenleitung.first_name,
            "groups": [
                {
                    "employees": [
                        {
                            "employee_number": employee.employee_number,
                            "first_name": employee.first_name,
                            "id": str(employee.id),
                            "last_name": employee.last_name,
                        }
                        for employee in employees
                    ],
                    "group_name": group.group_name,
                    "group_number": group.group_number,
                    "id": str(group.id),
                    "is_home_group": True,
                    "orders": [
                        {
                            "date": pre_order.date,
                            "id": pre_order.id,
                            "last_changed": pre_order.last_changed,
                            "location_id": pre_order.location_id,
                            "main_dish": pre_order.main_dish,
                            "nothing": pre_order.nothing,
                            "person_id": pre_order.person_id,
                            "salad_option": pre_order.salad_option,
                        }
                        for pre_order in pre_orders
                    ],
                },
                {
                    "employees": [
                        {
                            "employee_number": employee.employee_number,
                            "first_name": employee.first_name,
                            "id": str(employee.id),
                            "last_name": employee.last_name,
                        }
                        for employee in employees_alt
                    ],
                    "group_name": group_alt.group_name,
                    "group_number": group_alt.group_number,
                    "id": str(group_alt.id),
                    "is_home_group": False,
                    "orders": [
                        {
                            "date": pre_order.date,
                            "id": pre_order.id,
                            "last_changed": pre_order.last_changed,
                            "location_id": pre_order.location_id,
                            "main_dish": pre_order.main_dish,
                            "nothing": pre_order.nothing,
                            "person_id": pre_order.person_id,
                            "salad_option": pre_order.salad_option,
                        }
                        for pre_order in pre_orders_alt
                    ],
                },
            ],
            "id": str(user_gruppenleitung.id),
            "last_name": user_gruppenleitung.last_name,
            "username": user_gruppenleitung.username,
        }

        validated_data = PreOrdersByGroupLeaderSchema().dump(replystring)
        assert res == validated_data


def describe_get_pre_orders():
    def it_returns_pre_orders(mocker, pre_orders):
        mocker.patch.object(OrdersRepository, "get_pre_orders", return_value=pre_orders)

        res = PreOrdersService.get_pre_orders(
            filters=OrdersFilters(),
            user_id=uuid.uuid4(),
            user_group=UserGroup.verwaltung,
        )
        assert res == PreOrderFullSchema(many=True).dump(pre_orders)

    def it_handles_empty_results(mocker, pre_orders):
        mock_get_pre_orders = mocker.patch.object(
            OrdersRepository, "get_pre_orders", return_value=[]
        )

        res = PreOrdersService.get_pre_orders(
            filters=OrdersFilters(),
            user_id=uuid.uuid4(),
            user_group=UserGroup.verwaltung,
        )
        assert res == []
        mock_get_pre_orders.assert_called_once()


def describe_create_update_bulk_preorders():
    def it_creates_new_preorders(mocker, pre_orders, user_gruppenleitung, employees):

        employees_ids = [employee.id for employee in employees]
        mocker.patch.object(
            OrdersRepository, "get_employees_to_order_for", return_value=employees_ids
        )
        mocker.patch.object(OrdersRepository, "employee_in_location", return_value=True)
        mocker.patch.object(
            OrdersRepository, "preorder_already_exists", return_value=None
        )
        mock_create = mocker.patch.object(
            OrdersRepository, "create_bulk_orders", return_value=None
        )
        mocker.patch.object(OrdersRepository, "update_order", return_value=None)

        dict_pre_orders = [
            {
                "date": pre_order.date,
                "location_id": pre_order.location_id,
                "main_dish": pre_order.main_dish,
                "nothing": pre_order.nothing,
                "person_id": pre_order.person_id,
                "salad_option": pre_order.salad_option,
            }
            for pre_order in pre_orders
        ]

        res = PreOrdersService.create_update_bulk_preorders(
            dict_pre_orders, user_gruppenleitung.id
        )
        mock_create.assert_called_once()
        assert res == None  # noqa: E711

    def it_updates_existing_preorders(
        mocker, pre_orders, user_gruppenleitung, employees
    ):

        employees_ids = [employee.id for employee in employees]
        mocker.patch.object(
            OrdersRepository, "get_employees_to_order_for", return_value=employees_ids
        )
        mocker.patch.object(OrdersRepository, "employee_in_location", return_value=True)
        mocker.patch.object(
            OrdersRepository,
            "preorder_already_exists",
            side_effect=[
                pre_orders[0],
                pre_orders[1],
                pre_orders[2],
                pre_orders[3],
                pre_orders[4],
            ],
        )
        mock_create = mocker.patch.object(
            OrdersRepository, "create_bulk_orders", return_value=None
        )
        mock_update = mocker.patch.object(
            OrdersRepository, "update_order", return_value=None
        )

        dict_pre_orders = [
            {
                "date": pre_order.date,
                "location_id": pre_order.location_id,
                "main_dish": pre_order.main_dish,
                "nothing": pre_order.nothing,
                "person_id": pre_order.person_id,
                "salad_option": pre_order.salad_option,
            }
            for pre_order in pre_orders
        ]

        res = PreOrdersService.create_update_bulk_preorders(
            dict_pre_orders, user_gruppenleitung.id
        )
        mock_create.assert_called_once_with([])
        mock_update.assert_called_once()
        assert res == None  # noqa: E711

    def it_raises_bad_value_error_if_date_in_past(
        mocker, pre_orders, user_gruppenleitung, employees
    ):

        employees_ids = [employee.id for employee in employees]
        mocker.patch.object(
            OrdersRepository, "get_employees_to_order_for", return_value=employees_ids
        )
        mocker.patch.object(OrdersRepository, "employee_in_location", return_value=True)
        mocker.patch.object(
            OrdersRepository, "preorder_already_exists", return_value=None
        )
        mocker.patch.object(OrdersRepository, "create_bulk_orders", return_value=None)
        mocker.patch.object(OrdersRepository, "update_order", return_value=None)

        dict_pre_orders = [
            {
                "date": datetime.today().date() - timedelta(days=1),
                "location_id": pre_order.location_id,
                "main_dish": pre_order.main_dish,
                "nothing": pre_order.nothing,
                "person_id": pre_order.person_id,
                "salad_option": pre_order.salad_option,
            }
            for pre_order in pre_orders
        ]

        try:
            PreOrdersService.create_update_bulk_preorders(
                dict_pre_orders, user_gruppenleitung.id
            )
        except BadValueError as e:
            assert "liegt in der Vergangenheit." in str(e)

    def it_raises_bad_value_error_if_date_more_than_14_days_in_future(
        mocker, pre_orders, user_gruppenleitung, employees
    ):

        employees_ids = [employee.id for employee in employees]
        mocker.patch.object(
            OrdersRepository, "get_employees_to_order_for", return_value=employees_ids
        )
        mocker.patch.object(OrdersRepository, "employee_in_location", return_value=True)
        mocker.patch.object(
            OrdersRepository, "preorder_already_exists", return_value=None
        )
        mocker.patch.object(OrdersRepository, "create_bulk_orders", return_value=None)
        mocker.patch.object(OrdersRepository, "update_order", return_value=None)

        dict_pre_orders = [
            {
                "date": datetime.today().date() + timedelta(days=21),
                "location_id": pre_order.location_id,
                "main_dish": pre_order.main_dish,
                "nothing": pre_order.nothing,
                "person_id": pre_order.person_id,
                "salad_option": pre_order.salad_option,
            }
            for pre_order in pre_orders
        ]

        try:
            PreOrdersService.create_update_bulk_preorders(
                dict_pre_orders, user_gruppenleitung.id
            )
        except BadValueError as e:
            assert "liegt mehr als 14 Tage in der Zukunft." in str(e)

    def it_raises_bad_value_error_if_today_after_8_pm(
        mocker, pre_orders, user_gruppenleitung, employees
    ):

        employees_ids = [employee.id for employee in employees]
        mocker.patch.object(
            OrdersRepository, "get_employees_to_order_for", return_value=employees_ids
        )
        mocker.patch.object(OrdersRepository, "employee_in_location", return_value=True)
        mocker.patch.object(
            OrdersRepository, "preorder_already_exists", return_value=None
        )
        mocker.patch.object(OrdersRepository, "create_bulk_orders", return_value=None)
        mocker.patch.object(OrdersRepository, "update_order", return_value=None)

        dict_pre_orders = [
            {
                "date": datetime.today().date(),
                "location_id": pre_order.location_id,
                "main_dish": pre_order.main_dish,
                "nothing": pre_order.nothing,
                "person_id": pre_order.person_id,
                "salad_option": pre_order.salad_option,
            }
            for pre_order in pre_orders
        ]

        try:
            PreOrdersService.create_update_bulk_preorders(
                dict_pre_orders, user_gruppenleitung.id
            )
        except BadValueError as e:
            assert "Es ist nach 8 Uhr. Bestellungen sind nicht mehr möglich." in str(e)

    def it_raises_bad_value_error_if_weekend(
        mocker, pre_orders, user_gruppenleitung, employees
    ):

        employees_ids = [employee.id for employee in employees]
        mocker.patch.object(
            OrdersRepository, "get_employees_to_order_for", return_value=employees_ids
        )
        mocker.patch.object(OrdersRepository, "employee_in_location", return_value=True)
        mocker.patch.object(
            OrdersRepository, "preorder_already_exists", return_value=None
        )
        mocker.patch.object(OrdersRepository, "create_bulk_orders", return_value=None)
        mocker.patch.object(OrdersRepository, "update_order", return_value=None)

        wochentag = datetime.today().weekday()
        forward = 6 - wochentag
        if forward == 0:
            forward = 1

        dict_pre_orders = [
            {
                "date": datetime.today().date() + timedelta(days=forward),
                "location_id": pre_order.location_id,
                "main_dish": pre_order.main_dish,
                "nothing": pre_order.nothing,
                "person_id": pre_order.person_id,
                "salad_option": pre_order.salad_option,
            }
            for pre_order in pre_orders
        ]

        try:
            PreOrdersService.create_update_bulk_preorders(
                dict_pre_orders, user_gruppenleitung.id
            )
        except BadValueError as e:
            assert "ist kein Werktag." in str(e)

    def it_raises_action_not_possible_if_person_not_in_employees(
        mocker, pre_orders, user_gruppenleitung, employees
    ):

        mocker.patch.object(
            OrdersRepository, "get_employees_to_order_for", return_value=[]
        )
        mocker.patch.object(OrdersRepository, "employee_in_location", return_value=True)
        mocker.patch.object(
            OrdersRepository, "preorder_already_exists", return_value=None
        )
        mocker.patch.object(OrdersRepository, "create_bulk_orders", return_value=None)
        mocker.patch.object(OrdersRepository, "update_order", return_value=None)

        dict_pre_orders = [
            {
                "date": pre_order.date,
                "location_id": pre_order.location_id,
                "main_dish": pre_order.main_dish,
                "nothing": pre_order.nothing,
                "person_id": pre_order.person_id,
                "salad_option": pre_order.salad_option,
            }
            for pre_order in pre_orders
        ]

        try:
            PreOrdersService.create_update_bulk_preorders(
                dict_pre_orders, user_gruppenleitung.id
            )
        except ActionNotPossibleError as e:
            assert "gehört zu keiner der Gruppen von" in str(e)

    def it_raises_action_not_possible_if_person_not_in_location(
        mocker, pre_orders, user_gruppenleitung, employees
    ):

        employees_ids = [employee.id for employee in employees]
        mocker.patch.object(
            OrdersRepository, "get_employees_to_order_for", return_value=employees_ids
        )
        mocker.patch.object(
            OrdersRepository, "employee_in_location", return_value=False
        )
        mocker.patch.object(
            OrdersRepository, "preorder_already_exists", return_value=None
        )
        mocker.patch.object(OrdersRepository, "create_bulk_orders", return_value=None)
        mocker.patch.object(OrdersRepository, "update_order", return_value=None)

        dict_pre_orders = [
            {
                "date": pre_order.date,
                "location_id": pre_order.location_id,
                "main_dish": pre_order.main_dish,
                "nothing": pre_order.nothing,
                "person_id": pre_order.person_id,
                "salad_option": pre_order.salad_option,
            }
            for pre_order in pre_orders
        ]

        try:
            PreOrdersService.create_update_bulk_preorders(
                dict_pre_orders, user_gruppenleitung.id
            )
        except ActionNotPossibleError as e:
            assert "gehört nicht zum Standort" in str(e)

    def it_raises_bad_value_if_nothing_is_true_but_main_dish_or_salad_is_not_none(
        mocker, pre_orders, user_gruppenleitung, employees
    ):

        employees_ids = [employee.id for employee in employees]
        mocker.patch.object(
            OrdersRepository, "get_employees_to_order_for", return_value=employees_ids
        )
        mocker.patch.object(OrdersRepository, "employee_in_location", return_value=True)
        mocker.patch.object(
            OrdersRepository, "preorder_already_exists", return_value=None
        )
        mocker.patch.object(OrdersRepository, "create_bulk_orders", return_value=None)
        mocker.patch.object(OrdersRepository, "update_order", return_value=None)

        dict_pre_orders = [
            {
                "date": pre_order.date,
                "location_id": pre_order.location_id,
                "main_dish": pre_order.main_dish,
                "nothing": True,
                "person_id": pre_order.person_id,
                "salad_option": True,
            }
            for pre_order in pre_orders
        ]

        try:
            PreOrdersService.create_update_bulk_preorders(
                dict_pre_orders, user_gruppenleitung.id
            )
        except BadValueError as e:
            assert (
                "Wenn 'nichts' ausgewählt ist, dürfen keine Essensoptionen ausgewählt werden."
                in str(e)
            )


def describe_create_preoder_user():
    def it_creates_preorder_for_user(mocker, pre_order, user_gruppenleitung):

        pre_order.person_id = user_gruppenleitung.id
        mocker.patch.object(
            OrdersRepository, "preorder_already_exists", return_value=None
        )
        mock_create = mocker.patch.object(
            OrdersRepository, "create_single_order", return_value=pre_order
        )

        dict_pre_order = {
            "date": pre_order.date,
            "location_id": pre_order.location_id,
            "main_dish": pre_order.main_dish,
            "nothing": pre_order.nothing,
            "person_id": pre_order.person_id,
            "salad_option": pre_order.salad_option,
        }

        res = PreOrdersService.create_preorder_user(
            dict_pre_order, user_gruppenleitung.id
        )
        mock_create.assert_called_once()
        assert res == PreOrderFullSchema().dump(pre_order)

    def it_raises_bad_value_error_if_date_in_past(
        mocker, pre_order, user_gruppenleitung
    ):

        pre_order.person_id = user_gruppenleitung.id
        mocker.patch.object(
            OrdersRepository, "preorder_already_exists", return_value=None
        )
        mocker.patch.object(
            OrdersRepository, "create_single_order", return_value=pre_order
        )

        dict_pre_order = {
            "date": datetime.today().date() - timedelta(days=21),
            "location_id": pre_order.location_id,
            "main_dish": pre_order.main_dish,
            "nothing": pre_order.nothing,
            "person_id": pre_order.person_id,
            "salad_option": pre_order.salad_option,
        }
        try:
            PreOrdersService.create_preorder_user(
                dict_pre_order, user_gruppenleitung.id
            )
        except BadValueError as e:
            assert "liegt in der Vergangenheit." in str(e)

    def it_raises_bad_value_error_if_date_more_than_14_days_in_future(
        mocker, pre_order, user_gruppenleitung
    ):

        pre_order.person_id = user_gruppenleitung.id
        mocker.patch.object(
            OrdersRepository, "preorder_already_exists", return_value=None
        )
        mocker.patch.object(
            OrdersRepository, "create_single_order", return_value=pre_order
        )

        dict_pre_order = {
            "date": datetime.today().date() + timedelta(days=21),
            "location_id": pre_order.location_id,
            "main_dish": pre_order.main_dish,
            "nothing": pre_order.nothing,
            "person_id": pre_order.person_id,
            "salad_option": pre_order.salad_option,
        }
        try:
            PreOrdersService.create_preorder_user(
                dict_pre_order, user_gruppenleitung.id
            )
        except BadValueError as e:
            assert "liegt mehr als 14 Tage in der Zukunft." in str(e)

    def it_raises_bad_value_error_if_today_after_8_pm(
        mocker, pre_order, user_gruppenleitung
    ):

        pre_order.person_id = user_gruppenleitung.id
        mocker.patch.object(
            OrdersRepository, "preorder_already_exists", return_value=None
        )
        mocker.patch.object(
            OrdersRepository, "create_single_order", return_value=pre_order
        )

        dict_pre_order = {
            "date": datetime.today().date(),
            "location_id": pre_order.location_id,
            "main_dish": pre_order.main_dish,
            "nothing": pre_order.nothing,
            "person_id": pre_order.person_id,
            "salad_option": pre_order.salad_option,
        }
        try:
            PreOrdersService.create_preorder_user(
                dict_pre_order, user_gruppenleitung.id
            )
        except BadValueError as e:
            assert "Es ist nach 8 Uhr. Bestellungen sind nicht mehr möglich." in str(e)

    def it_raises_bad_value_error_if_weekend(mocker, pre_order, user_gruppenleitung):

        pre_order.person_id = user_gruppenleitung.id
        mocker.patch.object(
            OrdersRepository, "preorder_already_exists", return_value=None
        )
        mocker.patch.object(
            OrdersRepository, "create_single_order", return_value=pre_order
        )

        wochentag = datetime.today().weekday()
        forward = 6 - wochentag
        if forward == 0:
            forward = 1

        dict_pre_order = {
            "date": datetime.today().date() + timedelta(days=forward),
            "location_id": pre_order.location_id,
            "main_dish": pre_order.main_dish,
            "nothing": pre_order.nothing,
            "person_id": pre_order.person_id,
            "salad_option": pre_order.salad_option,
        }
        try:
            PreOrdersService.create_preorder_user(
                dict_pre_order, user_gruppenleitung.id
            )
        except BadValueError as e:
            assert "ist kein Werktag." in str(e)

    def it_raises_access_denied_for_other_person(
        mocker, pre_order, user_gruppenleitung, user_kuechenpersonal
    ):

        pre_order.person_id = user_kuechenpersonal.id
        mocker.patch.object(
            OrdersRepository, "preorder_already_exists", return_value=None
        )
        mocker.patch.object(
            OrdersRepository, "create_single_order", return_value=pre_order
        )

        dict_pre_order = {
            "date": pre_order.date,
            "location_id": pre_order.location_id,
            "main_dish": pre_order.main_dish,
            "nothing": pre_order.nothing,
            "person_id": pre_order.person_id,
            "salad_option": pre_order.salad_option,
        }
        try:
            PreOrdersService.create_preorder_user(
                dict_pre_order, user_gruppenleitung.id
            )
        except AccessDeniedError as e:
            assert "hat keinen Zugriff auf" in str(e)

    def it_raises_bad_value_if_nothing_is_true_but_main_dish_or_salad_is_not_none(
        mocker, pre_order, user_gruppenleitung
    ):

        pre_order.person_id = user_gruppenleitung.id
        mocker.patch.object(
            OrdersRepository, "preorder_already_exists", return_value=None
        )
        mocker.patch.object(
            OrdersRepository, "create_single_order", return_value=pre_order
        )

        dict_pre_order = {
            "date": pre_order.date,
            "location_id": pre_order.location_id,
            "main_dish": MainDish.rot,
            "nothing": True,
            "person_id": pre_order.person_id,
            "salad_option": True,
        }
        try:
            PreOrdersService.create_preorder_user(
                dict_pre_order, user_gruppenleitung.id
            )
        except BadValueError as e:
            assert (
                "Wenn 'nichts' ausgewählt ist, dürfen keine Essensoptionen ausgewählt werden."
                in str(e)
            )


def describe_update_preorder_user():
    def it_updates_preorder_for_user(mocker, pre_order, user_gruppenleitung):

        pre_order.person_id = user_gruppenleitung.id
        pre_order.id = 1
        mock_update = mocker.patch.object(
            OrdersRepository, "get_pre_order_by_id", return_value=pre_order
        )
        mocker.patch.object(
            OrdersRepository, "preorder_already_exists_different_id", return_value=None
        )
        mocker.patch.object(OrdersRepository, "update_order", return_value=None)

        dict_pre_order = {
            "date": pre_order.date,
            "location_id": pre_order.location_id,
            "main_dish": pre_order.main_dish,
            "nothing": pre_order.nothing,
            "person_id": pre_order.person_id,
            "salad_option": pre_order.salad_option,
        }

        res = PreOrdersService.update_preorder_user(
            dict_pre_order, pre_order.id, user_gruppenleitung.id
        )
        mock_update.assert_called_once()
        assert res == PreOrderFullSchema().dump(pre_order)

    def it_raises_not_found_error_if_preorder_missing(
        mocker, pre_order, user_gruppenleitung
    ):

        mocker.patch.object(OrdersRepository, "get_pre_order_by_id", return_value=None)
        mocker.patch.object(
            OrdersRepository, "preorder_already_exists_different_id", return_value=None
        )
        mocker.patch.object(OrdersRepository, "update_order", return_value=None)

        dict_pre_order = {
            "date": pre_order.date,
            "location_id": pre_order.location_id,
            "main_dish": pre_order.main_dish,
            "nothing": pre_order.nothing,
            "person_id": pre_order.person_id,
            "salad_option": pre_order.salad_option,
        }

        try:
            PreOrdersService.update_preorder_user(
                dict_pre_order, pre_order.id, user_gruppenleitung.id
            )
        except NotFoundError as e:
            assert "konnte nicht gefunden werden oder existiert nicht." in str(e)

    def it_raises_bad_value_error_if_date_in_past(
        mocker, pre_order, user_gruppenleitung
    ):

        pre_order.person_id = user_gruppenleitung.id
        pre_order.id = 1
        mocker.patch.object(
            OrdersRepository, "get_pre_order_by_id", return_value=pre_order
        )
        mocker.patch.object(
            OrdersRepository, "preorder_already_exists_different_id", return_value=None
        )
        mocker.patch.object(OrdersRepository, "update_order", return_value=None)

        dict_pre_order = {
            "date": datetime.today().date() - timedelta(days=21),
            "location_id": pre_order.location_id,
            "main_dish": pre_order.main_dish,
            "nothing": pre_order.nothing,
            "person_id": pre_order.person_id,
            "salad_option": pre_order.salad_option,
        }

        try:
            PreOrdersService.update_preorder_user(
                dict_pre_order, pre_order.id, user_gruppenleitung.id
            )
        except BadValueError as e:
            assert "liegt in der Vergangenheit." in str(e)

    def it_raises_bad_value_error_if_date_more_than_14_days_in_future(
        mocker, pre_order, user_gruppenleitung
    ):

        pre_order.person_id = user_gruppenleitung.id
        pre_order.id = 1
        mocker.patch.object(
            OrdersRepository, "get_pre_order_by_id", return_value=pre_order
        )
        mocker.patch.object(
            OrdersRepository, "preorder_already_exists_different_id", return_value=None
        )
        mocker.patch.object(OrdersRepository, "update_order", return_value=None)

        dict_pre_order = {
            "date": datetime.today().date() + timedelta(days=21),
            "location_id": pre_order.location_id,
            "main_dish": pre_order.main_dish,
            "nothing": pre_order.nothing,
            "person_id": pre_order.person_id,
            "salad_option": pre_order.salad_option,
        }

        try:
            PreOrdersService.update_preorder_user(
                dict_pre_order, pre_order.id, user_gruppenleitung.id
            )
        except BadValueError as e:
            assert "liegt mehr als 14 Tage in der Zukunft." in str(e)

    def it_raises_bad_value_error_if_today_after_8_pm(
        mocker, pre_order, user_gruppenleitung
    ):

        pre_order.person_id = user_gruppenleitung.id
        pre_order.id = 1
        mocker.patch.object(
            OrdersRepository, "get_pre_order_by_id", return_value=pre_order
        )
        mocker.patch.object(
            OrdersRepository, "preorder_already_exists_different_id", return_value=None
        )
        mocker.patch.object(OrdersRepository, "update_order", return_value=None)

        dict_pre_order = {
            "date": datetime.today().date(),
            "location_id": pre_order.location_id,
            "main_dish": pre_order.main_dish,
            "nothing": pre_order.nothing,
            "person_id": pre_order.person_id,
            "salad_option": pre_order.salad_option,
        }

        try:
            PreOrdersService.update_preorder_user(
                dict_pre_order, pre_order.id, user_gruppenleitung.id
            )
        except BadValueError as e:
            assert "Es ist nach 8 Uhr. Bestellungen sind nicht mehr möglich." in str(e)

    def it_raises_bad_value_error_if_weekend(mocker, pre_order, user_gruppenleitung):

        pre_order.person_id = user_gruppenleitung.id
        pre_order.id = 1
        mocker.patch.object(
            OrdersRepository, "get_pre_order_by_id", return_value=pre_order
        )
        mocker.patch.object(
            OrdersRepository, "preorder_already_exists_different_id", return_value=None
        )
        mocker.patch.object(OrdersRepository, "update_order", return_value=None)

        wochentag = datetime.today().weekday()
        forward = 6 - wochentag
        if forward == 0:
            forward = 1

        dict_pre_order = {
            "date": datetime.today().date() + timedelta(days=forward),
            "location_id": pre_order.location_id,
            "main_dish": pre_order.main_dish,
            "nothing": pre_order.nothing,
            "person_id": pre_order.person_id,
            "salad_option": pre_order.salad_option,
        }

        try:
            PreOrdersService.update_preorder_user(
                dict_pre_order, pre_order.id, user_gruppenleitung.id
            )
        except BadValueError as e:
            assert "ist kein Werktag." in str(e)

    def it_raises_access_denied_for_other_person_on_old_order(
        mocker, pre_order, user_gruppenleitung, user_kuechenpersonal
    ):

        pre_order.person_id = user_kuechenpersonal.id
        pre_order.id = 1
        mocker.patch.object(
            OrdersRepository, "get_pre_order_by_id", return_value=pre_order
        )
        mocker.patch.object(
            OrdersRepository, "preorder_already_exists_different_id", return_value=None
        )
        mocker.patch.object(OrdersRepository, "update_order", return_value=None)

        dict_pre_order = {
            "date": pre_order.date,
            "location_id": pre_order.location_id,
            "main_dish": pre_order.main_dish,
            "nothing": pre_order.nothing,
            "person_id": pre_order.person_id,
            "salad_option": pre_order.salad_option,
        }

        try:
            PreOrdersService.update_preorder_user(
                dict_pre_order, pre_order.id, user_gruppenleitung.id
            )
        except AccessDeniedError as e:
            assert "hat keinen Zugriff auf" in str(e)

    def it_raises_access_denied_for_other_person_on_change(
        mocker, pre_order, user_gruppenleitung, user_kuechenpersonal
    ):

        pre_order.person_id = user_gruppenleitung.id
        pre_order.id = 1
        mocker.patch.object(
            OrdersRepository, "get_pre_order_by_id", return_value=pre_order
        )
        mocker.patch.object(
            OrdersRepository, "preorder_already_exists_different_id", return_value=None
        )
        mocker.patch.object(OrdersRepository, "update_order", return_value=None)

        dict_pre_order = {
            "date": pre_order.date,
            "location_id": pre_order.location_id,
            "main_dish": pre_order.main_dish,
            "nothing": pre_order.nothing,
            "person_id": user_kuechenpersonal.id,
            "salad_option": pre_order.salad_option,
        }

        try:
            PreOrdersService.update_preorder_user(
                dict_pre_order, pre_order.id, user_gruppenleitung.id
            )
        except AccessDeniedError as e:
            assert "hat keinen Zugriff auf" in str(e)

    def it_raises_already_exists_if_same_order_details(
        mocker, pre_order, user_gruppenleitung, pre_order_alt
    ):

        pre_order.person_id = user_gruppenleitung.id
        pre_order.id = 1
        pre_order.date = (datetime.today().date() + timedelta(days=1),)
        pre_order_alt.person_id = user_gruppenleitung.id
        pre_order_alt.id = 2
        mocker.patch.object(
            OrdersRepository, "get_pre_order_by_id", return_value=pre_order
        )
        mocker.patch.object(
            OrdersRepository,
            "preorder_already_exists_different_id",
            return_value=pre_order_alt,
        )
        mocker.patch.object(OrdersRepository, "update_order", return_value=None)

        dict_pre_order = {
            "date": pre_order_alt.date,
            "location_id": pre_order.location_id,
            "main_dish": pre_order.main_dish,
            "nothing": pre_order.nothing,
            "person_id": pre_order.person_id,
            "salad_option": pre_order.salad_option,
        }

        try:
            PreOrdersService.update_preorder_user(
                dict_pre_order, pre_order.id, user_gruppenleitung.id
            )
        except AlreadyExistsError as e:
            assert (
                "Für diese Person existiert an diesem Tag bereits die Bestellung"
                in str(e)
            )

    def it_raises_bad_value_if_nothing_is_true_but_main_dish_or_salad_is_not_none(
        mocker, pre_order, user_gruppenleitung
    ):

        pre_order.person_id = user_gruppenleitung.id
        pre_order.id = 1
        mocker.patch.object(
            OrdersRepository, "get_pre_order_by_id", return_value=pre_order
        )
        mocker.patch.object(
            OrdersRepository, "preorder_already_exists_different_id", return_value=None
        )
        mocker.patch.object(OrdersRepository, "update_order", return_value=None)

        dict_pre_order = {
            "date": pre_order.date,
            "location_id": pre_order.location_id,
            "main_dish": MainDish.rot,
            "nothing": True,
            "person_id": pre_order.person_id,
            "salad_option": True,
        }

        try:
            PreOrdersService.update_preorder_user(
                dict_pre_order, pre_order.id, user_gruppenleitung.id
            )
        except BadValueError as e:
            assert (
                "Wenn 'nichts' ausgewählt ist, dürfen keine Essensoptionen ausgewählt werden."
                in str(e)
            )


def describe_delete_preorder_user():
    def it_deletes_preorder_for_user(mocker, pre_order, user_gruppenleitung):

        pre_order.person_id = user_gruppenleitung.id
        pre_order.id = 1
        mock_delete = mocker.patch.object(
            OrdersRepository, "get_pre_order_by_id", return_value=pre_order
        )
        mocker.patch.object(OrdersRepository, "delete_order", return_value=None)

        PreOrdersService.delete_preorder_user(pre_order.id, user_gruppenleitung.id)
        mock_delete.assert_called_once()

    def it_raises_not_found_error_if_preorder_missing(mocker, user_gruppenleitung):

        mocker.patch.object(OrdersRepository, "get_pre_order_by_id", return_value=None)
        mocker.patch.object(OrdersRepository, "delete_order", return_value=None)

        try:
            PreOrdersService.delete_preorder_user(1, user_gruppenleitung.id)
        except NotFoundError as e:
            assert "konnte nicht gefunden werden oder existiert nicht." in str(e)

    def it_raises_access_denied_for_other_person(
        mocker, pre_order, user_gruppenleitung, user_kuechenpersonal
    ):

        pre_order.person_id = user_kuechenpersonal.id
        pre_order.id = 1
        mocker.patch.object(
            OrdersRepository, "get_pre_order_by_id", return_value=pre_order
        )
        mocker.patch.object(OrdersRepository, "delete_order", return_value=None)

        try:
            PreOrdersService.delete_preorder_user(pre_order.id, user_gruppenleitung.id)
        except AccessDeniedError as e:
            assert "hat keinen Zugriff auf" in str(e)
