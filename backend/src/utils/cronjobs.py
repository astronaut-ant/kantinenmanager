from datetime import datetime, timedelta
from time import sleep

from src.utils.error import abort_with_err, ErrMsg
from src.models.preorder import PreOrder
from src.models.dailyorder import DailyOrder
from src.models.oldorder import OldOrder
from src.repositories.orders_repository import OrdersRepository, OrdersFilters
from src.repositories.persons_repository import PersonsRepository
from src.repositories.locations_repository import LocationsRepository


def push_orders_to_next_table():
    # Pushes all orders from yesterday to the old orders table

    orders_old = []  # type: List[OldOrder]
    orders_new = []  # type: List[PreOrder]
    date = datetime.today().date()
    date_yesterday = date - timedelta(days=1)

    orders_yesterday = OrdersRepository.get_daily_orders()
    for daily_order in orders_yesterday:
        # person = PersonsRepository.get_person_by_id(daily_order.person_id)
        # location = LocationsRepository.get_location_by_id(daily_order.location_id)
        # sleep(2) dosnt help
        old_order = OldOrder(
            person_id=daily_order.person_id,
            location_id=daily_order.location_id,
            date=date_yesterday,
            main_dish=daily_order.main_dish,
            salad_option=daily_order.salad_option,
            handed_out=daily_order.handed_out,
        )
        print(old_order, daily_order.person_id, daily_order.location_id)
        # TODO: person and location are NOT None but the
        # old_order.person and old_order.location are None....
        # How the fck does this happpen? I have no idea
        orders_old.append(old_order)

    if len(orders_yesterday) != len(orders_old):
        abort_with_err(
            ErrMsg(
                status_code=500,
                title="Error while transfering orders",
                description="The number of orders in the old orders table does not match the number of orders in the daily orders table",
            )
        )
    try:
        if len(orders_old) > 0:
            OrdersRepository.create_bulk_orders(orders_old)
    except Exception as e:
        abort_with_err(
            ErrMsg(
                status_code=500,
                title="Error while transfering orders",
                description="An error occured while transfering the orders to the old orders table",
            )
        )
    OrdersRepository.bulk_delete_orders(orders_yesterday)

    # Pushes all pre-orders for today to the daily orders table

    pre_orders = OrdersRepository.get_pre_orders(OrdersFilters(date=date))
    for pre_order in pre_orders:
        # pre_person = PersonsRepository.get_person_by_id(pre_order.person_id)
        # pre_location = LocationsRepository.get_location_by_id(pre_order.location_id)
        # sleep(2) dosnt help
        daily_order = DailyOrder(
            person_id=pre_order.person_id,
            location_id=pre_order.location_id,
            main_dish=pre_order.main_dish,
            salad_option=pre_order.salad_option,
            handed_out=False,
        )
        print(daily_order, pre_order.person_id, pre_order.location_id)  
        # TODO: pre_person and pre_location are NOT Null but the
        # daily_order.person and daily_order.location are Null....
        # How the fck does this happpen? I have no idea
        orders_new.append(daily_order)

    if len(pre_orders) != len(orders_new):
        abort_with_err(
            ErrMsg(
                status_code=500,
                title="Error while transfering orders",
                description="The number of orders in the daily orders table does not match the number of pre-orders for today",
            )
        )

    try:
        if len(orders_new) > 0:
            OrdersRepository.create_bulk_orders(orders_new)
    except Exception as e:
        abort_with_err(
            ErrMsg(
                status_code=500,
                title="Error while transfering orders",
                description="An error occured while transfering the orders to the old orders table",
            )
        )
    OrdersRepository.bulk_delete_orders(pre_orders)
