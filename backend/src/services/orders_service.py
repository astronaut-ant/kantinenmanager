from datetime import datetime
from uuid import UUID
from src.models.preorder import PreOrder
from src.models.user import UserGroup
from src.repositories.orders_repository import OrdersRepository
from src.utils.error import ErrMsg, abort_with_err
from typing import List, Optional


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
    def create_bulk_orders(
        orders: List[PreOrder], user_group: UserGroup, user_id: UUID
    ) -> List[UUID]:
        """
        Create orders
        :param orders: List of orders
        :param user_group: User group of the user
        :param group_id: Group id of the user
        :return: List of order ids
        """
        try:
            return OrdersRepository.create_bulk_orders(orders, user_group, user_id)
        except ValueError as err:
            abort_with_err(
                ErrMsg(
                    status_code=401,
                    title="Person gehört nicht zur Gruppe",
                    description="Eine der Personen gehört nicht zur Gruppe.",
                )
            )
