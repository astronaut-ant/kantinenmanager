"""Tests for the DailyOrders class"""

import uuid
from .helper import *  # for fixtures # noqa: F403
from src.services.daily_orders_service import DailyOrdersService
from src.repositories.orders_repository import OrdersRepository
from src.repositories.users_repository import UsersRepository
from src.repositories.groups_repository import GroupsRepository
from src.schemas.daily_orders_schema import DailyOrderFullSchema
from src.utils.exceptions import (
    NotFoundError,
    AccessDeniedError,
    BadValueError,
)


def describe_get_daily_order():
    def it_gets_daily_order_for_person_id(mocker, daily_order, user_gruppenleitung):

        daily_order.person_id = user_gruppenleitung.id
        daily_order.location_id = user_gruppenleitung.location_id
        mocker.patch.object(
            OrdersRepository, "get_daily_order_by_person_id", return_value=daily_order
        )
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_gruppenleitung
        )

        order = DailyOrdersService.get_daily_order(
            daily_order.person_id, user_gruppenleitung.id
        )

        assert order == daily_order

    def it_raises_not_found_error_if_no_order(mocker, user_gruppenleitung):

        mocker.patch.object(
            OrdersRepository, "get_daily_order_by_person_id", return_value=None
        )
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_gruppenleitung
        )
        try:
            DailyOrdersService.get_daily_order(
                user_gruppenleitung.id, user_gruppenleitung.id
            )
        except NotFoundError as e:
            assert f"Bestellung für Person '{user_gruppenleitung.id}'" in str(e)

    def it_raises_not_found_error_if_no_user(
        mocker, daily_order, user_kuechenpersonal, user_gruppenleitung
    ):

        mocker.patch.object(
            OrdersRepository, "get_daily_order_by_person_id", return_value=daily_order
        )
        mocker.patch.object(UsersRepository, "get_user_by_id", return_value=None)
        try:
            DailyOrdersService.get_daily_order(
                user_gruppenleitung.id, user_kuechenpersonal.id
            )
        except NotFoundError as e:
            assert "konnte nicht gefunden werden" in str(e)

    def it_raises_access_denied_error_if_location_id_not_matching(
        mocker, daily_order, user_gruppenleitung, user_kuechenpersonal
    ):

        daily_order.location_id = user_gruppenleitung.location_id
        daily_order.person_id = user_gruppenleitung.id
        user_kuechenpersonal.location_id = uuid.uuid4()
        mocker.patch.object(
            OrdersRepository, "get_daily_order_by_person_id", return_value=daily_order
        )
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_gruppenleitung
        )
        try:
            DailyOrdersService.get_daily_order(
                daily_order.person_id, user_kuechenpersonal.id
            )
        except AccessDeniedError as e:
            assert f"den Standort {daily_order.location_id}" in str(e)


def describe_get_own_daily_order():
    def it_gets_own_daily_order(mocker, daily_order, user_gruppenleitung):
        daily_order.person_id = user_gruppenleitung.id
        mocker.patch.object(
            OrdersRepository, "get_daily_order_by_person_id", return_value=daily_order
        )

        order = DailyOrdersService.get_own_daily_order(user_gruppenleitung.id)

        assert order == daily_order

    def it_raises_not_found_error_if_no_order(mocker, user_gruppenleitung):
        mocker.patch.object(
            OrdersRepository, "get_daily_order_by_person_id", return_value=None
        )
        try:
            DailyOrdersService.get_own_daily_order(user_gruppenleitung.id)
        except NotFoundError as e:
            assert f"Bestellung für Person '{user_gruppenleitung.id}'" in str(e)


def describe_update_daily_order():
    def it_updates_daily_order(mocker, daily_order, user_kuechenpersonal):
        daily_order.person_id = user_kuechenpersonal.id
        daily_order.location_id = user_kuechenpersonal.location_id
        daily_order.handed_out = False
        mocker.patch.object(
            OrdersRepository, "get_daily_order_by_id", return_value=daily_order
        )
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_kuechenpersonal
        )
        mocker.patch.object(OrdersRepository, "update_order", return_value=None)

        order = DailyOrdersService.update_daily_order(
            daily_order.id, True, user_kuechenpersonal.id
        )

        assert order.handed_out == True  # noqa: E712

    def it_raises_not_found_error_if_no_order(
        mocker, daily_order, user_kuechenpersonal
    ):
        daily_order.id = 10
        mocker.patch.object(
            OrdersRepository, "get_daily_order_by_id", return_value=None
        )
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_kuechenpersonal
        )
        mocker.patch.object(OrdersRepository, "update_order", return_value=None)
        try:
            DailyOrdersService.update_daily_order(
                daily_order.id + 1, True, user_kuechenpersonal.id
            )
        except NotFoundError as e:
            assert (
                f"Bestellung {daily_order.id+1} konnte nicht gefunden werden oder"
                in str(e)
            )

    def it_raises_not_found_error_if_no_user(
        mocker, daily_order, user_kuechenpersonal, user_gruppenleitung
    ):
        daily_order.person_id = user_gruppenleitung.id
        mocker.patch.object(
            OrdersRepository, "get_daily_order_by_id", return_value=daily_order
        )
        mocker.patch.object(UsersRepository, "get_user_by_id", return_value=None)
        mocker.patch.object(OrdersRepository, "update_order", return_value=None)
        try:
            DailyOrdersService.update_daily_order(
                daily_order.id, True, user_kuechenpersonal.id
            )
        except NotFoundError as e:
            assert (
                f"Nutzer {daily_order.person_id} konnte nicht gefunden werden oder"
                in str(e)
            )

    def it_raises_access_denied_error_if_location_id_not_matching(
        mocker, daily_order, user_gruppenleitung, user_kuechenpersonal
    ):
        daily_order.person_id = user_gruppenleitung.id
        daily_order.location_id = user_gruppenleitung.location_id = uuid.uuid4()
        user_kuechenpersonal.location_id = uuid.uuid4()
        mocker.patch.object(
            OrdersRepository, "get_daily_order_by_id", return_value=daily_order
        )
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_kuechenpersonal
        )
        mocker.patch.object(OrdersRepository, "update_order", return_value=None)
        try:
            DailyOrdersService.update_daily_order(
                daily_order.id, True, user_kuechenpersonal.id
            )
        except AccessDeniedError as e:
            assert (
                f"Nutzer:in hat keinen Zugriff auf den Standort {daily_order.location_id}"
                in str(e)
            )

    def it_raises_bad_value_error_if_order_already_handed_out(
        mocker, daily_order, user_kuechenpersonal
    ):
        daily_order.person_id = user_kuechenpersonal.id
        daily_order.location_id = user_kuechenpersonal.location_id = uuid.uuid4()
        daily_order.handed_out = True
        mocker.patch.object(
            OrdersRepository, "get_daily_order_by_id", return_value=daily_order
        )
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_kuechenpersonal
        )
        mocker.patch.object(OrdersRepository, "update_order", return_value=None)
        try:
            DailyOrdersService.update_daily_order(
                daily_order.id, True, user_kuechenpersonal.id
            )
        except BadValueError as e:
            assert (
                f"Bestellung {daily_order.id} wurde bereits als True markiert" in str(e)
            )


def describe_get_daily_orders_filterd_by_user_scope():
    def it_gets_daily_orders_filtered_by_user_scope(
        mocker, daily_order, user_gruppenleitung
    ):
        daily_order.person_id = user_gruppenleitung.id
        daily_order.location_id = user_gruppenleitung.location_id
        mocker.patch.object(
            OrdersRepository,
            "get_daily_orders_filtered_by_user_scope",
            return_value=[daily_order],
        )

        orders = DailyOrdersService.get_daily_orders_filtered_by_user_scope(
            user_gruppenleitung.id
        )

        assert orders == [daily_order]

    def it_returns_an_empty_list_which_is_an_absolutely_useless_test_hello_readers_i_like_you(
        mocker, user_gruppenleitung
    ):
        mocker.patch.object(
            OrdersRepository, "get_daily_orders_filtered_by_user_scope", return_value=[]
        )

        orders = DailyOrdersService.get_daily_orders_filtered_by_user_scope(
            user_gruppenleitung.id
        )

        assert orders == []


def describe_get_daily_orders_for_group():
    def it_gets_daily_orders_for_own_group(
        mocker, daily_orders, group, user_gruppenleitung, location
    ):
        group.group_leader = user_gruppenleitung
        group.location = location
        user_gruppenleitung.location = location
        mock_get_orders = mocker.patch.object(
            OrdersRepository, "get_daily_orders_for_group", return_value=daily_orders
        )
        mocker.patch.object(GroupsRepository, "get_group_by_id", return_value=group)
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_gruppenleitung
        )

        orders = DailyOrdersService.get_daily_orders_for_group(
            group.id, user_gruppenleitung.id
        )

        assert orders == daily_orders
        mock_get_orders.assert_called_once_with(group.id)

    def it_gets_daily_orders_for_other_group_replacement_group_leader(
        mocker, daily_orders, group, user_gruppenleitung, location
    ):
        group.replacement_group_leader = user_gruppenleitung
        group.location = location
        user_gruppenleitung.location = location
        mock_get_orders = mocker.patch.object(
            OrdersRepository, "get_daily_orders_for_group", return_value=daily_orders
        )
        mocker.patch.object(GroupsRepository, "get_group_by_id", return_value=group)
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_gruppenleitung
        )

        orders = DailyOrdersService.get_daily_orders_for_group(
            group.id, user_gruppenleitung.id
        )

        assert orders == daily_orders
        mock_get_orders.assert_called_once_with(group.id)

    def it_raises_not_found_error_if_no_group(mocker, user_gruppenleitung):
        mocker.patch.object(GroupsRepository, "get_group_by_id", return_value=None)
        try:
            DailyOrdersService.get_daily_orders_for_group(
                uuid.uuid4(), user_gruppenleitung.id
            )
        except NotFoundError as e:
            assert "Gruppe mit ID" in str(e)

    def it_raises_access_denied_error_if_user_not_in_group(
        mocker, daily_orders, group, user_gruppenleitung, user_kuechenpersonal
    ):
        group.group_leader = user_gruppenleitung
        mocker.patch.object(
            OrdersRepository, "get_daily_orders_for_group", return_value=daily_orders
        )
        mocker.patch.object(GroupsRepository, "get_group_by_id", return_value=group)
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_kuechenpersonal
        )
        try:
            DailyOrdersService.get_daily_orders_for_group(
                group.id, user_kuechenpersonal.id
            )
        except AccessDeniedError as e:
            assert (
                f"Zugriff verweigert. Gruppe {group.id} gehört nicht zu Nutzer"
                in str(e)
            )


def describe_create_daily_orders():
    def it_creates_daily_orders(mocker, daily_orders):
        mock_create = mocker.patch.object(
            OrdersRepository, "create_daily_orders", return_value=None
        )

        orders = DailyOrdersService.create_daily_orders(daily_orders)

        mock_create.assert_called_once_with(daily_orders)
        assert orders == DailyOrderFullSchema(many=True).dump(daily_orders)


def get_all_daily_orders():
    def it_retuns_all_daily_orders(mocker, daily_orders):
        mock_create = mocker.patch.object(
            OrdersRepository, "get_all_daily_orders", return_value=daily_orders
        )

        orders = DailyOrdersService.get_all_daily_orders()
        assert orders == daily_orders
        mock_create.assert_called_once()
