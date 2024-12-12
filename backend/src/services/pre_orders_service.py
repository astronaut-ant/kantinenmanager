from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID
from src.models.preorder import PreOrder
from src.models.user import UserGroup
from src.repositories.orders_repository import OrdersFilters, OrdersRepository
from src.utils.exceptions import (
    PersonNotPartOfGroup,
    PersonNotPartOfLocation,
    WrongUserError,
)


class PreOrdersService:
    """
    Service class for orders
    """

    @staticmethod
    def get_pre_order_by_id(id: int) -> Optional[PreOrder]:
        """
        Get pre order by id
        """

        return OrdersRepository.get_pre_order_by_id(id)

    @staticmethod
    def get_pre_orders_by_group_leader(person_id: UUID) -> List[PreOrder]:
        """
        Get pre orders by person id of th group leader
        """

        return OrdersRepository.get_pre_orders_by_group_leader(person_id)

    @staticmethod
    def get_pre_orders(filters: OrdersFilters) -> List[PreOrder]:
        """
        Get orders
        :param filters: Filters for orders
        :return: List of orders
        """

        return OrdersRepository.get_pre_orders(filters)

    @staticmethod
    def create_update_bulk_preorders(
        orders: List[dict], user_group: UserGroup, user_id: UUID
    ):
        """
        Create orders
        :param orders: List of orders
        :param user_group: User group of the user
        :param group_id: Group id of the user
        :return: List of order ids
        """
        bulk_orders = []
        employee_ids = OrdersRepository.get_employees_to_order_for(user_id)

        for order in orders:
            if order["date"] < datetime.now().date():
                raise ValueError(f"Datum {order['date']} liegt in der Vergangenheit.")
            if order["date"] > datetime.now().date() + timedelta(days=14):
                raise ValueError(
                    f"Datum {order['date']} liegt mehr als 14 Tage in der Zukunft."
                )
            if order["date"].weekday() > 5:  # 0 = Montag, 6 = Sonntag
                raise ValueError(f"Datum {order['date']} ist kein Werktag.")
            if order["person_id"] not in employee_ids:
                raise PersonNotPartOfGroup(
                    f"Person {order["person_id"]} gehört zu keiner der Gruppen von {user_id}"
                )
            if not OrdersRepository.employee_in_location(
                order["person_id"], order["location_id"]
            ):
                raise PersonNotPartOfLocation(
                    f"Person {order["person_id"]} gehört nicht zum Standort {order["location_id"]}"
                )
            # Überprüfen, ob die Bestellung bereits existiert. Falls ja, aktualisiere oder lösche diese
            order_exists = OrdersRepository.preorder_already_exists(
                order["person_id"], order["date"]
            )
            if order_exists:
                order_exists.nothing = order["nothing"]
                order_exists.main_dish = order["main_dish"]
                order_exists.salad_option = order["salad_option"]
                order_exists.location_id = order["location_id"]
                OrdersRepository.update_order(order_exists)
            else:
                bulk_orders.append(PreOrder(**order))

        OrdersRepository.create_bulk_orders(bulk_orders)

    @staticmethod
    def create_preorder_user(order: dict, user_id: UUID):
        """
        Create order
        :param order: Order
        :param user_group: User group of the user
        :param group_id: Group id of the user
        :return: Order id
        """
        if order["date"] < datetime.now().date():
            raise ValueError(f"Das Datum {order['date']} liegt in der Vergangenheit.")
        if order["date"] > datetime.now().date() + timedelta(days=14):
            raise ValueError(
                f"Das Datum {order['date']} liegt mehr als 14 Tage in der Zukunft."
            )
        if order["date"].weekday() > 5:  # 0 = Montag, 6 = Sonntag
            raise ValueError(f"Das Datum {order['date']} ist kein Werktag.")
        if user_id != order["person_id"]:
            raise WrongUserError(
                f"Person {order['person_id']} gehört zu keiner der Gruppen von {user_id}"
            )
        OrdersRepository.create_single_order(PreOrder(**order))

    @staticmethod
    def update_preorder_user(new_order: dict, preorder_id: UUID, user_id: UUID):
        """
        Update order
        :param new_order: dict
        :param preorder_id: new_order id
        :param user_id: User id
        """
        if new_order["date"] < datetime.now().date():
            raise ValueError(
                f"Das Datum {new_order['date']} liegt in der Vergangenheit."
            )
        if new_order["date"] > datetime.now().date() + timedelta(days=14):
            raise ValueError(
                f"Das Datum {new_order['date']} liegt mehr als 14 Tage in der Zukunft."
            )
        if new_order["date"].weekday() > 5:
            raise ValueError(f"Das Datum {new_order['date']} ist kein Werktag.")
        if user_id != new_order["person_id"]:
            raise WrongUserError(
                f"Person {new_order['person_id']} gehört zu keiner der Gruppen von {user_id}"
            )
        if not (new_order["main_dish"] and new_order["salad_option"]):
            return OrdersRepository.delete_order(new_order)
        old_order = OrdersRepository.get_pre_order_by_id(preorder_id)
        old_order.nothing = new_order["nothing"]
        old_order.date = new_order["date"]
        old_order.main_dish = new_order["main_dish"]
        old_order.salad_option = new_order["salad_option"]
        OrdersRepository.update_order()

    @staticmethod
    def delete_preorder_user(preorder_id: UUID, user_id: UUID):
        """
        Delete order
        :param preorder_id: Preorder id
        :param user_id: User id
        """
        preorder = OrdersRepository.get_pre_order_by_id(preorder_id)
        if user_id != preorder.person_id:
            raise WrongUserError(
                f"Person {preorder.person_id} gehört zu keiner der Gruppen von {user_id}"
            )
        OrdersRepository.delete_order(preorder)
