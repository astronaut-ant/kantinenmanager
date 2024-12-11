from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID
from src.models.dailyorder import DailyOrder
from src.models.user import UserGroup
from src.repositories.users_repository import UsersRepository
from src.repositories.orders_repository import OrdersFilters, OrdersRepository
from src.utils.exceptions import (
    PersonNotPartOfGroup,
    PersonNotPartOfLocation,
    WrongUserError,
    WrongLocationError,
)


class DailyOrdersService:
    """Service to manage daily orders"""

    @staticmethod
    def get_daily_order(person_id: UUID, user_id: UUID) -> DailyOrder:
        order = OrdersRepository.get_daily_order_by_person_id(person_id)
        user = UsersRepository.get_user_by_id(user_id)
        if order:
            if not user:
                raise ValueError(f"Nutzer {person_id} existiert nicht.")
            if order.location_id != user.location_id:
                raise WrongLocationError(
                    f"Person {person_id} gehört nicht zum Standort {user.location_id}"
                )
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
                raise WrongLocationError(
                    f"Person {order.person_id} gehört nicht zum Standort {user.location_id}"
                )
            order.handed_out = handed_out
            OrdersRepository.update_order(order)
