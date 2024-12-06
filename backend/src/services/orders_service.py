from uuid import UUID
from src.services.auth_service import AuthService
from src.models.preorder import PreOrder
from src.models.user import UserGroup
from src.models.location import Location
from src.repositories.orders_repository import OrdersRepository
from src.utils.error import ErrMsg, abort_with_err
from typing import List


class OrdersService:

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
