from typing import List
from src.models.oldorder import OldOrder
from src.repositories.orders_repository import OrdersFilters, OrdersRepository


class OldOrdersService:

    @staticmethod
    def get_old_orders(filters: OrdersFilters) -> List[OldOrder]:
        """
        Get orders
        :param filters: Filters for old orders

        :return: List of old orders
        """
        return OrdersRepository.get_old_orders(filters)
