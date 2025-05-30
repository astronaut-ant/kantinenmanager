from datetime import datetime

from src.utils.exceptions import BadValueError, NotFoundError
from src.models.dish_price import DishPrice
from src.repositories.dish_prices_repository import DishPricesRepository


class DishPricesService:
    """Service for handling dish prices."""

    @staticmethod
    def get_prices() -> list[DishPrice]:
        """Get all dish prices."""

        return DishPricesRepository.get_prices()

    @staticmethod
    def get_price_valid_at_date(date: datetime) -> DishPrice | None:
        """Retrieve a dish price by its date

        :param date: The date of the dish price to retrieve

        :return: The dish price with the given date or None if no dish price was found
        """

        return DishPricesRepository.get_price_valid_at_date(date)

    @staticmethod
    def get_current_price() -> DishPrice | None:
        """Retrieve the dish price for today

        :return: The dish price for today or None if no dish price was found
        """
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        return DishPricesService.get_price_valid_at_date(today)

    @staticmethod
    def create_price(
        date: datetime, main_dish_price: float, salad_price: float, prepayment: float
    ) -> DishPrice:
        """Create a new dish price.

        :param date: The date of the dish price
        :param main_dish_price: The price of the main dish
        :param salad_price: The price of the salad
        :param prepayment: The price of the prepayment

        :return: The created dish price
        """

        if DishPricesRepository.get_price_by_date(date):
            raise BadValueError(f"Es existiert bereits ein Preis für das Datum {date}")

        if main_dish_price < 0 or salad_price < 0:
            raise BadValueError("Preise dürfen nicht negativ sein")

        if prepayment < 0:
            raise BadValueError("Vorauszahlung darf nicht negativ sein")

        price = DishPrice(
            date=date,
            main_dish_price=main_dish_price,
            salad_price=salad_price,
            prepayment=prepayment,
        )
        DishPricesRepository.create_price(price)

        return price

    @staticmethod
    def update_price(
        old_date: datetime,
        date: datetime,
        main_dish_price: float,
        salad_price: float,
        prepayment: float,
    ) -> DishPrice:
        """Update an existing dish price.

        :param date: The date of the dish price
        :param main_dish_price: The price of the main dish
        :param salad_price: The price of the salad
        :param prepayment: The price of the prepayment

        :return: The updated dish price
        """

        price = DishPricesRepository.get_price_by_date(old_date)

        if price is None:
            raise NotFoundError(f"Preis für Datum {old_date} existiert nicht")

        if old_date != date and DishPricesRepository.get_price_by_date(date):
            raise BadValueError(f"Es existiert bereits ein Preis für das Datum {date}")

        if main_dish_price < 0 or salad_price < 0:
            raise BadValueError("Preise dürfen nicht negativ sein")

        if prepayment < 0:
            raise BadValueError("Vorauszahlung darf nicht negativ sein")

        price.date = date
        price.main_dish_price = main_dish_price
        price.salad_price = salad_price
        price.prepayment = prepayment

        DishPricesRepository.update_price(price)

        return price

    @staticmethod
    def delete_price(date: datetime):
        """Delete a dish price.

        :param date: The date of the dish price
        """

        price = DishPricesRepository.get_price_by_date(date)

        if price is None:
            raise NotFoundError(f"Dish price for date {date} does not exist")

        DishPricesRepository.delete_price(price)
