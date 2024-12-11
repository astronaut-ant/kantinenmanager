from datetime import datetime, timedelta
from time import sleep

from src.models.preorder import PreOrder
from src.models.dailyorder import DailyOrder
from src.models.oldorder import OldOrder
from src.repositories.orders_repository import OrdersRepository, OrdersFilters
from src.repositories.persons_repository import PersonsRepository
from src.repositories.locations_repository import LocationsRepository
from src.utils.exceptions import OrderTransferError


def push_orders_to_next_table(app):
    with app.app_context():

        # Pushes all orders from yesterday to the old orders table

        orders_old = []  # type: List[OldOrder]
        orders_new = []  # type: List[PreOrder]
        date = datetime.today().date()
        date_yesterday = date - timedelta(days=1)

        orders_yesterday = OrdersRepository.get_daily_orders()
        for daily_order in orders_yesterday:
            old_order = OldOrder(
                person_id=daily_order.person_id,
                location_id=daily_order.location_id,
                date=date_yesterday,
                main_dish=daily_order.main_dish,
                salad_option=daily_order.salad_option,
                handed_out=daily_order.handed_out,
            )
            orders_old.append(old_order)

        if len(orders_yesterday) != len(orders_old):
            OrderTransferError()
        try:
            if len(orders_old) > 0:
                OrdersRepository.create_bulk_orders(orders_old)
        except Exception as e:
            OrderTransferError()

        try:
            OrdersRepository.bulk_delete_orders(orders_yesterday)
        except Exception as e:
            OrderTransferError()

        # Pushes all pre-orders for today to the daily orders table

        pre_orders = OrdersRepository.get_pre_orders(OrdersFilters(date=date))
        for pre_order in pre_orders:
            daily_order = DailyOrder(
                person_id=pre_order.person_id,
                location_id=pre_order.location_id,
                main_dish=pre_order.main_dish,
                salad_option=pre_order.salad_option,
                handed_out=False,
            )
            orders_new.append(daily_order)

        if len(pre_orders) != len(orders_new):
            OrderTransferError

        try:
            if len(orders_new) > 0:
                OrdersRepository.create_bulk_orders(orders_new)
        except Exception as e:
            OrderTransferError()

        try:
            OrdersRepository.bulk_delete_orders(pre_orders)
        except Exception as e:
            OrderTransferError()
        return ()
