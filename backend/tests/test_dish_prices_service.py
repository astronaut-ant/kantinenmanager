"""Tests for the DishPricesService."""

import pytest

from datetime import datetime, timedelta
from src.utils.exceptions import BadValueError, NotFoundError
from src.services.dish_prices_service import DishPricesService
from src.repositories.dish_prices_repository import DishPricesRepository
from .helper import *  # for fixtures # noqa: F403


def describe_get_prices():
    def it_returns_all_prices(mocker, dish_price):
        mocker.patch.object(
            DishPricesRepository, "get_prices", return_value=[dish_price]
        )

        prices = DishPricesService.get_prices()

        assert prices == [dish_price]


def describe_get_price_valid_at_date():
    def it_calls_repository(mocker, dish_price):
        mock_get_price_valid_at_date = mocker.patch.object(
            DishPricesRepository, "get_price_valid_at_date", return_value=dish_price
        )

        date = datetime.now()

        price = DishPricesService.get_price_valid_at_date(date)

        assert price == dish_price
        mock_get_price_valid_at_date.assert_called_once_with(date)


def describe_get_current_price():
    def it_gets_current_price(mocker, dish_price):
        mock_get_price_valid_at_date = mocker.patch.object(
            DishPricesService, "get_price_valid_at_date", return_value=dish_price
        )

        date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        price = DishPricesService.get_current_price()

        assert price == dish_price
        mock_get_price_valid_at_date.assert_called_once_with(date)


def describe_create_price():
    def it_raises_when_date_exists_already(mocker, dish_price):
        mocker.patch.object(
            DishPricesRepository, "get_price_by_date", return_value=dish_price
        )

        with pytest.raises(BadValueError) as e:
            DishPricesService.create_price(dish_price.date, 1, 1, 1)

        assert (
            str(e.value)
            == f"Ungültiger Wert: Es existiert bereits ein Preis für das Datum {dish_price.date}"
        )

    def it_raises_when_main_price_is_negative(mocker, dish_price):
        mocker.patch.object(
            DishPricesRepository, "get_price_by_date", return_value=None
        )

        with pytest.raises(BadValueError) as e:
            DishPricesService.create_price(dish_price.date, -1, 10, 10)

        assert str(e.value) == "Ungültiger Wert: Preise dürfen nicht negativ sein"

    def it_raises_when_salad_price_is_negative(mocker, dish_price):
        mocker.patch.object(
            DishPricesRepository, "get_price_by_date", return_value=None
        )

        with pytest.raises(BadValueError) as e:
            DishPricesService.create_price(dish_price.date, 10, -1, 10)

        assert str(e.value) == "Ungültiger Wert: Preise dürfen nicht negativ sein"

    def it_raises_when_prepayment_is_negative(mocker, dish_price):
        mocker.patch.object(
            DishPricesRepository, "get_price_by_date", return_value=None
        )

        with pytest.raises(BadValueError) as e:
            DishPricesService.create_price(dish_price.date, 10, 10, -1)

        assert str(e.value) == "Ungültiger Wert: Vorauszahlung darf nicht negativ sein"

    def it_creates_price(mocker, dish_price):
        mocker.patch.object(
            DishPricesRepository, "get_price_by_date", return_value=None
        )
        mock_create_price = mocker.patch.object(DishPricesRepository, "create_price")

        price = DishPricesService.create_price(dish_price.date, 10, 10, 10)

        assert price.date == dish_price.date
        assert price.main_dish_price == 10
        assert price.salad_price == 10
        assert price.prepayment == 10
        mock_create_price.assert_called_once_with(price)


def describe_update_price():
    def it_raises_when_price_does_not_exist(mocker, dish_price):
        mocker.patch.object(
            DishPricesRepository, "get_price_by_date", return_value=None
        )

        with pytest.raises(NotFoundError):
            DishPricesService.update_price(dish_price.date, dish_price.date, 1, 1, 1)

    def it_raises_when_date_exists_already(mocker, dish_price):
        mocker.patch.object(
            DishPricesRepository, "get_price_by_date", return_value=dish_price
        )

        new_date = (datetime.now() + timedelta(days=1)).date()

        with pytest.raises(BadValueError) as e:
            DishPricesService.update_price(dish_price.date, new_date, 1, 1, 1)

        assert (
            str(e.value)
            == f"Ungültiger Wert: Es existiert bereits ein Preis für das Datum {new_date}"
        )

    def it_does_not_check_date_when_date_is_the_same(mocker, dish_price):
        mock_get_price_by_date = mocker.patch.object(
            DishPricesRepository, "get_price_by_date", return_value=dish_price
        )
        mocker.patch.object(DishPricesRepository, "update_price")

        DishPricesService.update_price(dish_price.date, dish_price.date, 1, 1, 1)

        mock_get_price_by_date.assert_called_once()

    def it_raises_when_main_price_is_negative(mocker, dish_price):
        mocker.patch.object(
            DishPricesRepository, "get_price_by_date", return_value=dish_price
        )

        with pytest.raises(BadValueError) as e:
            DishPricesService.update_price(dish_price.date, dish_price.date, -1, 10, 10)

        assert str(e.value) == "Ungültiger Wert: Preise dürfen nicht negativ sein"

    def it_raises_when_salad_price_is_negative(mocker, dish_price):
        mocker.patch.object(
            DishPricesRepository, "get_price_by_date", return_value=dish_price
        )

        with pytest.raises(BadValueError) as e:
            DishPricesService.update_price(dish_price.date, dish_price.date, 10, -1, 10)

        assert str(e.value) == "Ungültiger Wert: Preise dürfen nicht negativ sein"

    def it_raises_when_prepayment_is_negative(mocker, dish_price):
        mocker.patch.object(
            DishPricesRepository, "get_price_by_date", return_value=dish_price
        )

        with pytest.raises(BadValueError) as e:
            DishPricesService.update_price(dish_price.date, dish_price.date, 10, 10, -1)

        assert str(e.value) == "Ungültiger Wert: Vorauszahlung darf nicht negativ sein"

    def it_updates_price(mocker, dish_price):
        mocker.patch.object(
            DishPricesRepository, "get_price_by_date", side_effect=[dish_price, None]
        )
        mock_update_price = mocker.patch.object(DishPricesRepository, "update_price")

        new_date = (datetime.now() + timedelta(days=10)).date()

        price = DishPricesService.update_price(
            dish_price.date, new_date, 1000, 1000, 1000
        )

        assert price.date == new_date
        assert price.main_dish_price == 1000
        assert price.salad_price == 1000
        assert price.prepayment == 1000
        mock_update_price.assert_called_once_with(price)


def describe_delete_price():
    def it_raises_when_price_does_not_exist(mocker):
        mocker.patch.object(
            DishPricesRepository, "get_price_by_date", return_value=None
        )

        with pytest.raises(NotFoundError):
            DishPricesService.delete_price(datetime.now().date())

    def it_deletes_price(mocker, dish_price):
        mocker.patch.object(
            DishPricesRepository, "get_price_by_date", return_value=dish_price
        )
        mock_delete_price = mocker.patch.object(DishPricesRepository, "delete_price")

        DishPricesService.delete_price(dish_price.date)

        mock_delete_price.assert_called_once_with(dish_price)
