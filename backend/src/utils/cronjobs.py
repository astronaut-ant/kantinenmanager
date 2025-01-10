import pytz
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from src.repositories.orders_repository import OrdersRepository


def register_cronjobs(app):
    """Register all cronjobs."""

    scheduler = BackgroundScheduler()

    print("Registering cronjobs")

    scheduler.add_job(
        lambda: push_orders_to_next_table(app),
        "cron",
        hour="8",
        minute="00",
        timezone="Europe/Berlin",
    )

    scheduler.start()
    scheduler.print_jobs()


# TODO Error handling
def push_orders_to_next_table(app):
    """Push orders from the pre-orders table to the daily orders table and from the daily orders table to the old orders table."""

    with app.app_context():
        timezone = pytz.timezone("Europe/Berlin")
        today = datetime.now(timezone).date()

        print("Running cronjob to push orders to the next table.")

        OrdersRepository.push_dailyorders_to_oldorders(today)
        OrdersRepository.push_preorders_to_dailyorders(today)
        OrdersRepository.clean_preorders(today)
