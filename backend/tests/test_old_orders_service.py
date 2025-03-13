"""Tests for the very small and useless OldOrdersService class"""

import uuid
import pytest
from .helper import *  # for fixtures # noqa: F403
from src.services.old_orders_service import OldOrdersService
from src.repositories.orders_repository import OrdersRepository, OrdersFilters
from src.utils.exceptions import NotFoundError


def describe_get_old_orders():
    def it_returns_old_orders_if_found(mocker, old_orders):
        for order in old_orders:
            order.group_id = uuid.uuid4()
        mock_get_orders = mocker.patch.object(
            OrdersRepository, "get_old_orders", return_value=old_orders
        )

        filters = OrdersFilters(group_id=uuid.uuid4())
        res = OldOrdersService.get_old_orders(filters)

        assert res == old_orders
        mock_get_orders.assert_called_once_with(filters)

    def it_raises_not_found_error_if_no_orders_exist(mocker):
        mock_get_orders = mocker.patch.object(
            OrdersRepository, "get_old_orders", return_value=[]
        )

        filters = OrdersFilters(group_id=uuid.uuid4())
        with pytest.raises(NotFoundError, match="No old orders found"):
            OldOrdersService.get_old_orders(filters)

        mock_get_orders.assert_called_once_with(filters)
