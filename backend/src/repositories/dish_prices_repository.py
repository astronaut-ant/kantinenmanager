from datetime import datetime
from sqlalchemy import select

from src.models.dish_price import DishPrice
from src.database import db


class DishPricesRepository:
    """Repository for handling dish prices."""

    @staticmethod
    def get_prices() -> list[DishPrice]:
        """Get all dish prices saved in the database.

        :return: A list of all dish prices with all properties
        """

        return db.session.scalars(select(DishPrice)).all()

    @staticmethod
    def get_price_by_date(date: datetime) -> DishPrice | None:
        """Retrieve a dish price by its date

        :param date: The date of the dish price to retrieve

        :return: The dish price with the given date or None if no dish price was found
        """

        return db.session.scalars(
            select(DishPrice).where(DishPrice.date == date)
        ).first()

    @staticmethod
    def get_newest_price() -> DishPrice | None:
        """Retrieve the newest dish price

        :return: The newest dish price or None if no dish price was found
        """

        return db.session.scalars(
            select(DishPrice).order_by(DishPrice.date.desc()).limit(1)
        ).first()

    @staticmethod
    def get_todays_price() -> DishPrice | None:
        """Retrieve the dish price for today

        :return: The dish price for today or None if no dish price was found
        """

        return db.session.scalars(
            select(DishPrice)
            .where(DishPrice.date <= datetime.now().date())
            .order_by(DishPrice.date.desc())
            .limit(1)
        ).first()

    @staticmethod
    def create_price(price: DishPrice):
        """Create a new dish price in the database.

        :param price: The dish price to create
        """

        db.session.add(price)
        db.session.commit()

    @staticmethod
    def update_price(price: DishPrice):
        """Update an existing dish price in the database.

        :param price: The dish price to update
        """

        db.session.commit()

    @staticmethod
    def delete_price(price: DishPrice):
        """Delete a dish price from the database.

        :param price: The dish price to delete
        """

        db.session.delete(price)
        db.session.commit()
