import pytz
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from src.repositories.orders_repository import OrdersRepository


def register_cronjobs(app):
    """Register all cronjobs."""

    scheduler = BackgroundScheduler()

    app.logger.info("Registering cronjobs")

    scheduler.add_job(
        lambda: push_orders_to_next_table(app),
        "cron",
        hour="8",
        minute="00",
        timezone="Europe/Berlin",
    )

    scheduler.start()
    scheduler.print_jobs()


def push_orders_to_next_table(app):
    """Push orders from the pre-orders table to the daily orders table and from the daily orders table to the old orders table."""

    with app.app_context():
        timezone = pytz.timezone("Europe/Berlin")
        today = datetime.now(timezone).date()

        app.logger.info("Running cronjob to push orders to the next table.")

        try:
            OrdersRepository.push_dailyorders_to_oldorders(today)
            OrdersRepository.push_preorders_to_dailyorders(today)
            OrdersRepository.clean_preorders(today)
            raise Exception("Test")
        except Exception as e:
            app.logger.error(f"Error while pushing orders to next table: {e}")
            raise e
