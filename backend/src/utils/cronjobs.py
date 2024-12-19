import os
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from src.models.dailyorder import DailyOrder
from src.models.oldorder import OldOrder
from src.models.preorder import PreOrder
from src.repositories.orders_repository import OrdersRepository, OrdersFilters


def register_cronjobs(app):
    """Register all cronjobs."""

    if (
        os.environ.get("WERKZEUG_RUN_MAIN")
        == "true"  # Never change a running system. :3
    ):  # register cronjobs only once
        scheduler = BackgroundScheduler()

        print("Registering cronjobs")

        scheduler.add_job(
            lambda: push_orders_to_next_table(app),
            "cron",
            hour="8",
            minute="0",
            timezone="Europe/Berlin",
        )

        scheduler.start()
        scheduler.print_jobs()


# TODO Error handling
def push_orders_to_next_table(app):
    """Push orders from the pre-orders table to the daily orders table and from the daily orders table to the old orders table."""

    with app.app_context():
        today = datetime.today().date()
        yesterday = today - timedelta(days=1)

        print("Running cronjob to push orders to the next table.")

        orders_yesterday = OrdersRepository.get_all_daily_orders(
            OrdersFilters(date_end=yesterday)
        )

        if len(orders_yesterday) > 0:
            # Push all orders from yesterday to the old orders table
            old_orders = [
                daily_order_to_old_order(daily_order)
                for daily_order in orders_yesterday
            ]
            OrdersRepository.create_bulk_orders(
                old_orders, commit=False
            )  # Create old orders
            OrdersRepository.bulk_delete_orders(
                orders_yesterday, commit=True
            )  # Delete daily orders

            print(f"Pushed {len(orders_yesterday)} orders to old orders table.")

        orders_today = OrdersRepository.get_pre_orders(OrdersFilters(date=today))

        if len(orders_today) > 0:
            # Push all orders from today to the daily orders table
            daily_orders = [
                pre_order_to_daily_order(pre_order) for pre_order in orders_today
            ]
            OrdersRepository.create_bulk_orders(
                daily_orders, commit=False
            )  # Create daily orders
            OrdersRepository.bulk_delete_orders(
                orders_today, commit=True
            )  # Delete pre-orders

            print(f"Pushed {len(orders_today)} orders to daily orders table.")


def pre_order_to_daily_order(pre_order: PreOrder) -> DailyOrder:
    """Helper function to convert a PreOrder to a DailyOrder."""

    return DailyOrder(
        person_id=pre_order.person_id,
        location_id=pre_order.location_id,
        date=pre_order.date,
        nothing=pre_order.nothing,
        main_dish=pre_order.main_dish,
        salad_option=pre_order.salad_option,
        handed_out=False,
    )


def daily_order_to_old_order(daily_order: DailyOrder) -> OldOrder:
    """Helper function to convert a DailyOrder to an OldOrder."""

    return OldOrder(
        person_id=daily_order.person_id,
        location_id=daily_order.location_id,
        date=daily_order.date,
        nothing=daily_order.nothing,
        main_dish=daily_order.main_dish,
        salad_option=daily_order.salad_option,
        handed_out=daily_order.handed_out,
    )
