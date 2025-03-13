from typing import List
from src.models.oldorder import OldOrder
from src.repositories.orders_repository import OrdersFilters, OrdersRepository
from src.utils.exceptions import NotFoundError


class OldOrdersService:

    @staticmethod
    def get_old_orders(filters: OrdersFilters) -> List[OldOrder]:
        """
        Get orders
        :param filters: Filters for old orders

        :return: List of old orders
        """
        old_orders = OrdersRepository.get_old_orders(filters)
        if old_orders == []:
            raise NotFoundError("No old orders found")
        else:
            return old_orders
