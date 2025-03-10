"""Tests for the dish prices routes."""

from sqlalchemy import select
from .helper import *  # for fixtures # noqa: F403
from .helper import login
from datetime import datetime, timedelta
from src.models.dish_price import DishPrice


def _datetime_to_date_string(date: datetime) -> str:
    """Convert a datetime object to a date string in the format 'YYYY-MM-DD'."""
    return date.isoformat()[:10]


def describe_dish_prices():
    def describe_get():
        def it_returns_all_prices(
            client, db, dish_price, dish_price_alt, user_verwaltung
        ):
            db.session.add_all([dish_price, dish_price_alt, user_verwaltung])
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get("/api/dish_prices")

            assert res.status_code == 200
            assert len(res.json) == 2

    def describe_get_by_date():
        def it_returns_price_for_exact_date(
            client, db, dish_price, user_verwaltung, today
        ):
            dish_price.date = today
            db.session.add(dish_price)
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get(f"/api/dish_prices/{_datetime_to_date_string(today)}")

            a = db.session.execute(select(DishPrice)).scalars().all()
            print(a)

            assert res.status_code == 200
            assert res.json["date"] == _datetime_to_date_string(today)

        def it_returns_active_price_for_date(
            client, db, dish_price, dish_price_alt, user_verwaltung, today
        ):
            date_alt = today - timedelta(days=10)
            dish_price.date = today
            dish_price_alt.date = date_alt
            db.session.add_all([dish_price, dish_price_alt, user_verwaltung])
            db.session.commit()
            login(user=user_verwaltung, client=client)

            req_date = today - timedelta(days=5)

            res = client.get(f"/api/dish_prices/{_datetime_to_date_string(req_date)}")

            assert res.status_code == 200
            assert res.json["date"] == _datetime_to_date_string(date_alt)

        def it_returns_active_price_for_date_in_future(
            client, db, dish_price, dish_price_alt, user_verwaltung, today
        ):
            date_alt = today - timedelta(days=10)
            dish_price.date = today
            dish_price_alt.date = date_alt
            db.session.add_all([dish_price, dish_price_alt, user_verwaltung])
            db.session.commit()
            login(user=user_verwaltung, client=client)

            req_date = today + timedelta(days=5)

            res = client.get(f"/api/dish_prices/{_datetime_to_date_string(req_date)}")

            assert res.status_code == 200
            assert res.json["date"] == _datetime_to_date_string(today)

        def it_returns_404_for_non_existing_date(
            client, db, dish_price, user_verwaltung, today
        ):
            dish_price.date = today
            db.session.add_all([dish_price, user_verwaltung])
            db.session.commit()
            login(user=user_verwaltung, client=client)

            req_date = today - timedelta(days=5)

            res = client.get(f"/api/dish_prices/{_datetime_to_date_string(req_date)}")

            assert res.status_code == 404
            assert res.json["title"] == "Preis existiert nicht"

        def it_raises_validation_error_for_only_year(client, db, user_verwaltung):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get("/api/dish_prices/2025")

            assert res.status_code == 400
            assert res.json["title"] == "Validierungsfehler"
            assert res.json["description"] == "Ungültiges Datum"

        def it_raises_validation_error_for_invalid_date(client, db, user_verwaltung):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get("/api/dish_prices/2025-02-30")

            assert res.status_code == 400
            assert res.json["title"] == "Validierungsfehler"
            assert res.json["description"] == "Ungültiges Datum"

        def it_raises_validation_error_for_invalid_date2(client, db, user_verwaltung):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get("/api/dish_prices/2025-00-00")

            assert res.status_code == 400
            assert res.json["title"] == "Validierungsfehler"
            assert res.json["description"] == "Ungültiges Datum"

        def it_raises_validation_error_for_invalid_month(client, db, user_verwaltung):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get("/api/dish_prices/2025-13-01")

            assert res.status_code == 400
            assert res.json["title"] == "Validierungsfehler"
            assert res.json["description"] == "Ungültiges Datum"

        def it_raises_validation_error_for_invalid_date_format(
            client, db, user_verwaltung
        ):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get("/api/dish_prices/01-01-2025")

            assert res.status_code == 400
            assert res.json["title"] == "Validierungsfehler"
            assert res.json["description"] == "Ungültiges Datum"

    def describe_get_current():
        def it_returns_current_price(
            client, db, dish_price, dish_price_alt, user_verwaltung, today
        ):
            date_alt = today - timedelta(days=10)
            dish_price.date = today
            dish_price_alt.date = date_alt
            db.session.add_all([dish_price, dish_price_alt, user_verwaltung])
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get("/api/dish_prices/current")

            assert res.status_code == 200
            assert res.json["date"] == _datetime_to_date_string(today)

        def it_returns_404_for_no_price(client, db, user_verwaltung):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get("/api/dish_prices/current")

            assert res.status_code == 404
            assert res.json["title"] == "Preis existiert nicht"

    def describe_post():
        def it_creates_price(client, db, user_verwaltung, today):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            main_dish_price = 1
            salad_price = 2
            prepayment = 3

            res = client.post(
                "/api/dish_prices",
                json={
                    "date": _datetime_to_date_string(today),
                    "main_dish_price": main_dish_price,
                    "salad_price": salad_price,
                    "prepayment": prepayment,
                },
            )

            assert res.status_code == 201
            assert res.json["date"] == _datetime_to_date_string(today)
            assert res.json["main_dish_price"] == main_dish_price
            assert res.json["salad_price"] == salad_price
            assert res.json["prepayment"] == prepayment

        def it_raises_for_existing_date(client, db, dish_price, user_verwaltung, today):
            dish_price.date = today
            db.session.add_all([dish_price, user_verwaltung])
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.post(
                "/api/dish_prices",
                json={
                    "date": _datetime_to_date_string(today),
                    "main_dish_price": 1,
                    "salad_price": 2,
                    "prepayment": 3,
                },
            )

            assert res.status_code == 400
            assert res.json["title"] == "Fehler beim Erstellen"
            assert (
                res.json["description"]
                == f"Ungültiger Wert: Es existiert bereits ein Preis für das Datum {today}"
            )

        def it_raises_for_negative_main_price(client, db, user_verwaltung, today):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.post(
                "/api/dish_prices",
                json={
                    "date": _datetime_to_date_string(today),
                    "main_dish_price": -1,
                    "salad_price": 2,
                    "prepayment": 3,
                },
            )

            assert res.status_code == 400
            assert res.json["title"] == "Fehler beim Erstellen"
            assert (
                res.json["description"]
                == "Ungültiger Wert: Preise dürfen nicht negativ sein"
            )

        def it_raises_for_negative_salad_price(client, db, user_verwaltung, today):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.post(
                "/api/dish_prices",
                json={
                    "date": _datetime_to_date_string(today),
                    "main_dish_price": 1,
                    "salad_price": -2,
                    "prepayment": 3,
                },
            )

            assert res.status_code == 400
            assert res.json["title"] == "Fehler beim Erstellen"
            assert (
                res.json["description"]
                == "Ungültiger Wert: Preise dürfen nicht negativ sein"
            )

        def it_raises_for_negative_prepayment(client, db, user_verwaltung, today):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.post(
                "/api/dish_prices",
                json={
                    "date": _datetime_to_date_string(today),
                    "main_dish_price": 1,
                    "salad_price": 2,
                    "prepayment": -3,
                },
            )

            assert res.status_code == 400
            assert res.json["title"] == "Fehler beim Erstellen"
            assert (
                res.json["description"]
                == "Ungültiger Wert: Vorauszahlung darf nicht negativ sein"
            )

    def describe_put():
        def it_updates_price(client, db, dish_price, user_verwaltung, today):
            db.session.add_all([dish_price, user_verwaltung])
            db.session.commit()
            login(user=user_verwaltung, client=client)

            new_date = today + timedelta(days=5)
            main_dish_price = 1
            salad_price = 2
            prepayment = 3

            res = client.put(
                f"/api/dish_prices/{_datetime_to_date_string(dish_price.date)}",
                json={
                    "date": _datetime_to_date_string(new_date),
                    "main_dish_price": main_dish_price,
                    "salad_price": salad_price,
                    "prepayment": prepayment,
                },
            )

            assert res.status_code == 200
            assert res.json["date"] == _datetime_to_date_string(new_date)
            assert res.json["main_dish_price"] == main_dish_price
            assert res.json["salad_price"] == salad_price
            assert res.json["prepayment"] == prepayment
            assert len(db.session.execute(select(DishPrice)).all()) == 1

        def it_raises_for_non_existing_date(
            client, db, dish_price, user_verwaltung, today
        ):
            db.session.add_all([dish_price, user_verwaltung])
            db.session.commit()
            login(user=user_verwaltung, client=client)

            new_date = today + timedelta(days=5)

            res = client.put(
                f"/api/dish_prices/{_datetime_to_date_string(new_date)}",
                json={
                    "date": _datetime_to_date_string(new_date),
                    "main_dish_price": 1,
                    "salad_price": 2,
                    "prepayment": 3,
                },
            )

            assert res.status_code == 404
            assert res.json["title"] == "Preis existiert nicht"

    def describe_delete():
        def it_deletes_price(client, db, dish_price, user_verwaltung, today):
            dish_price.date = today
            db.session.add_all([dish_price, user_verwaltung])
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.delete(f"/api/dish_prices/{_datetime_to_date_string(today)}")

            assert res.status_code == 204
            assert len(db.session.execute(select(DishPrice)).all()) == 0

        def it_raises_for_non_existing_date(
            client, db, dish_price, user_verwaltung, today
        ):
            db.session.add_all([dish_price, user_verwaltung])
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.delete(
                f"/api/dish_prices/{_datetime_to_date_string(today + timedelta(days=5))}"
            )

            assert res.status_code == 404
            assert res.json["title"] == "Preis existiert nicht"
