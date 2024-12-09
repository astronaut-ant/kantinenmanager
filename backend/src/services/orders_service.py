from datetime import datetime
from uuid import UUID
from src.models.preorder import PreOrder
from src.models.user import UserGroup
from src.repositories.orders_repository import OrdersRepository
from src.utils.error import ErrMsg, abort_with_err
from typing import List, Optional
from src.utils.exceptions import (
    OrderAlreadyExistsForPersonAndDate,
    PersonNotPartOfGroup,
    PersonNotPartOfLocation,
    WrongUserError,
)


class OrdersFilters:
    """
    Filters for orders

    All filters are optional.

    :param person_id: Person id
    :param location_id: Location id
    :param group_id: Group id
    :param date: Date
    :param date_start: Start date
    :param date_end: End date
    """

    def __init__(
        self,
        person_id: Optional[UUID] = None,
        location_id: Optional[UUID] = None,
        group_id: Optional[UUID] = None,
        date: Optional[datetime] = None,
        date_start: Optional[datetime] = None,
        date_end: Optional[datetime] = None,
    ):
        """
        Constructor

        :param person_id: Person id
        :param location_id: Location id
        :param group_id: Group id
        :param date: Date
        :param date_start: Start date
        :param date_end: End date
        """
        self.person_id = person_id
        self.location_id = location_id
        self.group_id = group_id
        self.date = date
        self.date_start = date_start
        self.date_end = date_end

    def __repr__(self):
        return f"OrdersFilters(person_id={self.person_id}, location_id={self.location_id}, group_id={self.group_id}, date={self.date}, date_start={self.date_start}, date_end={self.date_end})"


class OrdersService:
    """
    Service class for orders
    """

    @staticmethod
    def get_orders(filters: OrdersFilters) -> List[any]:  # TODO
        """
        Get orders
        :param filters: Filters for orders
        :return: List of orders
        """

        return []

    @staticmethod
    def create_bulk_orders(orders: List[dict], user_group: UserGroup, user_id: UUID):
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
            if not (order["main_dish"] and order["salad_option"]):
                continue
            if order["date"] < datetime.now().date():
                raise ValueError(
                    f"Das Datum {order['date']} liegt in der Vergangenheit."
                )
            if not (order["person_id"] in employee_ids):
                raise PersonNotPartOfGroup(
                    f"Person {order["person_id"]} gehört zu keiner der Gruppen von {user_id}"
                )
            if not OrdersRepository.employee_belongs_to_location(
                order["person_id"], order["location_id"]
            ):
                raise PersonNotPartOfLocation(
                    f"Person {order["person_id"]} gehört nicht zum Standort {order["location_id"]}"
                )
            if OrdersRepository.order_already_exists(order["person_id"], order["date"]):
                raise OrderAlreadyExistsForPersonAndDate(
                    f"Bestelllung für den {order["date"]} existiert bereits bei Person {order["person_id"]}."
                )
            bulk_orders.append(PreOrder(**order))

        OrdersRepository.create_bulk_orders(bulk_orders)

    @staticmethod
    def create_order_user(order: dict, user_group: UserGroup, user_id: UUID):
        """
        Create order
        :param order: Order
        :param user_group: User group of the user
        :param group_id: Group id of the user
        :return: Order id
        """
        if not (order["main_dish"] and order["salad_option"]):
            return
        if order["date"] < datetime.now().date():
            raise ValueError(f"Das Datum {order['date']} liegt in der Vergangenheit.")
        if user_id != order["person_id"]:
            raise WrongUserError(
                f"Person {order['person_id']} gehört zu keiner der Gruppen von {user_id}"
            )
        if OrdersRepository.order_already_exists(order["person_id"], order["date"]):
            raise OrderAlreadyExistsForPersonAndDate(
                f"Bestelllung für den {order['date']} existiert bereits bei Person {order['person_id']}."
            )
        OrdersRepository.create_order_user(PreOrder(**order), user_group, user_id)
