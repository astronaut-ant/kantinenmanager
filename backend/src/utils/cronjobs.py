from datetime import datetime, timedelta
from time import sleep

from src.models.preorder import PreOrder
from src.models.dailyorder import DailyOrder
from src.models.oldorder import OldOrder
from src.repositories.orders_repository import OrdersRepository, OrdersFilters
from src.repositories.persons_repository import PersonsRepository
from src.repositories.locations_repository import LocationsRepository
from src.utils.exceptions import OrderTransferError


def push_orders_to_next_table(app, ignore_errors=False):
    with app.app_context():
        # Checks if the date in the old_orders and pre_orders table matches the expected.

        orders_old = []  # type: List[OldOrder]
        orders_new = []  # type: List[PreOrder]
        date = datetime.today().date()
        date_yesterday = date - timedelta(days=1)
        if ignore_errors == False:
            if (
                OrdersRepository.get_old_orders(OrdersFilters(date=date_yesterday))
                != []
            ):
                print("Tables unset")
                raise OrderTransferError()
            if OrdersRepository.get_pre_orders(OrdersFilters(date=date)) == []:
                print("Tables unset")
                raise OrderTransferError()

        # Pushes all orders from yesterday to the old orders table

        orders_yesterday = OrdersRepository.get_all_daily_orders()
        for daily_order in orders_yesterday:
            old_order = OldOrder(
                person_id=daily_order.person_id,
                location_id=daily_order.location_id,
                nothing=daily_order.nothing,
                date=date_yesterday,
                main_dish=daily_order.main_dish,
                salad_option=daily_order.salad_option,
                handed_out=daily_order.handed_out,
            )
            orders_old.append(old_order)

        if len(orders_yesterday) != len(orders_old):
            raise OrderTransferError()
        try:
            if len(orders_old) > 0:
                OrdersRepository.create_bulk_orders(orders_old)
        except Exception as e:
            raise OrderTransferError()

        try:
            OrdersRepository.bulk_delete_orders(orders_yesterday)
        except Exception as e:
            raise OrderTransferError()

        # Pushes all pre-orders for today to the daily orders table

        pre_orders = OrdersRepository.get_pre_orders(OrdersFilters(date=date))
        for pre_order in pre_orders:
            daily_order = DailyOrder(
                person_id=pre_order.person_id,
                location_id=pre_order.location_id,
                nothing=pre_order.nothing,
                main_dish=pre_order.main_dish,
                salad_option=pre_order.salad_option,
                handed_out=False,
            )
            orders_new.append(daily_order)

        if len(pre_orders) != len(orders_new):
            raise OrderTransferError

        try:
            if len(orders_new) > 0:
                OrdersRepository.create_bulk_orders(orders_new)
        except Exception as e:
            raise OrderTransferError()

        try:
            OrdersRepository.bulk_delete_orders(pre_orders)
        except Exception as e:
            raise OrderTransferError()
        return ()
