from datetime import datetime, timedelta
from uuid import UUID
from src.models.preorder import PreOrder
from src.models.dailyorder import DailyOrder
from src.models.oldorder import OldOrder
from src.models.user import UserGroup
from src.repositories.users_repository import UsersRepository
from src.repositories.orders_repository import OrdersRepository
from src.utils.error import ErrMsg, abort_with_err
from typing import List, Optional
from src.utils.exceptions import (
    PersonNotPartOfGroup,
    PersonNotPartOfLocation,
    WrongUserError,
    WrongLocationError
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
    def create_update_bulk_preorders(orders: List[dict], user_group: UserGroup, user_id: UUID):
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
            if order["date"] > datetime.now().date()+timedelta(days=14):
                raise ValueError(f"Datum {order['date']} liegt mehr als 14 Tage in der Zukunft.")
            if order["date"].weekday() < 5:     # 0 = Montag, 6 = Sonntag
                raise ValueError(f"Datum {order['date']} ist kein Werktag.")
            if not (order["person_id"] in employee_ids):
                raise PersonNotPartOfGroup(
                    f"Person {order["person_id"]} gehört zu keiner der Gruppen von {user_id}"
                )
            if not OrdersRepository.employee_in_location(order["person_id"], order["location_id"]):
                raise PersonNotPartOfLocation(
                    f"Person {order["person_id"]} gehört nicht zum Standort {order["location_id"]}"
                )
            # Überprüfen, ob die Bestellung bereits existiert. Falls ja, aktualisiere oder lösche diese
            order_exists = OrdersRepository.preorder_already_exists(order["person_id"], order["date"])
            if order_exists:
                if not (order["main_dish"] and order["salad_option"]):  # 'leere' Bestellungen löschen
                    OrdersRepository.delete_order(order_exists)
                else:
                    order_exists.main_dish = order["main_dish"]
                    order_exists.salad_option = order["salad_option"]
                    order_exists.location_id = order["location_id"]
                    OrdersRepository.update_order(order_exists)
                continue
            # Ignoriere Bestellung, wenn sie 'leer' ist
            if not (order["main_dish"] and order["salad_option"]):
                continue
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
        if order["date"] > datetime.now().date()+timedelta(days=14):
            raise ValueError(f"Das Datum {order['date']} liegt mehr als 14 Tage in der Zukunft.")
        if order["date"].weekday() < 5:     # 0 = Montag, 6 = Sonntag
            raise ValueError(f"Das Datum {order['date']} ist kein Werktag.")
        if user_id != order["person_id"]:
            raise WrongUserError(f"Person {order['person_id']} gehört zu keiner der Gruppen von {user_id}")
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
            raise ValueError(f"Das Datum {new_order['date']} liegt in der Vergangenheit.")
        if new_order["date"] > datetime.now().date()+timedelta(days=14):
            raise ValueError(f"Das Datum {new_order['date']} liegt mehr als 14 Tage in der Zukunft.")
        if new_order["date"].weekday() < 5:
            raise ValueError(f"Das Datum {new_order['date']} ist kein Werktag.")
        if user_id != new_order["person_id"]:
            raise WrongUserError(f"Person {new_order['person_id']} gehört zu keiner der Gruppen von {user_id}")
        if not (new_order["main_dish"] and new_order["salad_option"]):
            return OrdersRepository.delete_order(new_order)
        old_order = OrdersRepository.get_preorder_by_id(preorder_id)
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
        preorder = OrdersRepository.get_preorder_by_id(preorder_id)
        if user_id != preorder.person_id:
            raise WrongUserError(f"Person {preorder.person_id} gehört zu keiner der Gruppen von {user_id}")
        OrdersRepository.delete_order(preorder)

    @staticmethod
    def get_daily_order(person_id: UUID, user_id: UUID) -> DailyOrder:
        order = OrdersRepository.get_daily_order_by_person_id(person_id)
        user = UsersRepository.get_user_by_id(user_id)
        if order:
            if not user:
                raise ValueError(f"Nutzer {person_id} existiert nicht.")
            if order.location_id != user.location_id:
                raise WrongLocationError(f"Person {person_id} gehört nicht zum Standort {user.location_id}")
            return order
        else:
            return None
    
    @staticmethod
    def update_daily_order(daily_order_id: UUID, handed_out: bool, user_id: UUID):
        order = OrdersRepository.get_daily_order_by_id(daily_order_id)
        user = UsersRepository.get_user_by_id(user_id)
        if order:
            if not user:
                raise ValueError(f"Nutzer {order.person_id} existiert nicht.")
            if order.location_id != user.location_id:
                raise WrongLocationError(f"Person {order.person_id} gehört nicht zum Standort {user.location_id}")
            order.handed_out = handed_out
            OrdersRepository.update_order(order)
