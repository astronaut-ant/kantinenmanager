""" ""End-to-End tests for the daily_orders routes."""

import uuid
import datetime
from .helper import *  # for fixtures # noqa: F403
from .helper import login  # noqa: F401
from src.models.dailyorder import DailyOrder


def describe_daily_orders():
    def describe_get_daily_orders_userscope():
        def it_returns_daily_orders(
            client,
            user_verwaltung,
            user_standortleitung,
            user_gruppenleitung,
            location,
            group,
            employees,
            daily_orders,
            db,
        ):
            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.add(user_gruppenleitung)
            db.session.commit()
            db.session.add(location)
            db.session.add(group)
            db.session.commit()
            db.session.add_all(employees)
            db.session.commit()
            db.session.add_all(daily_orders)
            db.session.commit()

            login(user=user_verwaltung, client=client)
            response = client.get("/api/daily-orders")
            assert response.status_code == 200
            assert len(response.json) == 5
            assert db.session.query(DailyOrder).count() == 5

        def it_returns_no_daily_orders_out_of_scope(
            client,
            user_verwaltung,
            user_standortleitung,
            user_gruppenleitung,
            user_kuechenpersonal_alt,
            user_standortleitung_alt_location,
            location,
            location_alt,
            group,
            employees,
            daily_order,
            daily_orders,
            db,
        ):
            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.add(user_gruppenleitung)
            db.session.add(user_kuechenpersonal_alt)
            db.session.add(user_standortleitung_alt_location)
            db.session.commit()
            db.session.add(location)
            db.session.add(location_alt)
            db.session.add(group)
            db.session.commit()
            db.session.add_all(employees)
            db.session.commit()
            daily_order.location_id = location_alt.id
            db.session.add(daily_order)
            db.session.add_all(daily_orders)
            db.session.commit()

            login(user=user_kuechenpersonal_alt, client=client)
            response = client.get("/api/daily-orders")
            assert response.status_code == 200
            assert len(response.json) == 5
            assert db.session.query(DailyOrder).count() == 6

        def unauthorized(client, user_gruppenleitung, db):
            db.session.add(user_gruppenleitung)
            db.session.commit()

            res = client.get("/api/daily-orders")
            assert res.status_code == 401

            login(user=user_gruppenleitung, client=client)
            res = client.get("/api/daily-orders")
            assert res.status_code == 403

    def describe_get_daily_orders_counted():
        def it_returns_daily_orders_counted(
            client,
            user_verwaltung,
            user_standortleitung,
            user_gruppenleitung,
            user_kuechenpersonal,
            location,
            group,
            employees,
            daily_orders,
            db,
        ):
            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.add(user_gruppenleitung)
            db.session.add(user_kuechenpersonal)
            db.session.commit()
            db.session.add(location)
            db.session.add(group)
            db.session.commit()
            db.session.add_all(employees)
            db.session.commit()
            db.session.add_all(daily_orders)
            db.session.commit()

            login(user=user_verwaltung, client=client)
            response = client.get("/api/daily-orders/counted")
            assert response.status_code == 200
            assert len(response.json) == 1
            assert response.json[0]["location_id"] == str(location.id)
            assert response.json[0]["rot"] == 5
            assert response.json[0]["blau"] == 0
            assert response.json[0]["salad_option"] == 5

        def it_returns_single_location_kuechenpersonal(
            client,
            user_verwaltung,
            user_kuechenpersonal_alt,
            user_gruppenleitung,
            user_gruppenleitung_alt,
            user_gruppenleitung_alt_location,
            user_standortleitung,
            user_standortleitung_alt_location,
            location_alt,
            location,
            group,
            group_alt,
            group_alt_location,
            employees,
            employees_alt,
            employees_alt_location,
            daily_orders,
            daily_orders_alt,
            daily_orders_alt_location,
            db,
        ):
            db.session.add(user_verwaltung)
            db.session.add(user_gruppenleitung)
            db.session.add(user_standortleitung)
            db.session.add(user_standortleitung_alt_location)
            db.session.commit()
            db.session.add(location)
            db.session.add(location_alt)
            db.session.add(group)
            db.session.commit()
            db.session.add(user_gruppenleitung_alt)
            db.session.add(user_gruppenleitung_alt_location)
            db.session.add(user_kuechenpersonal_alt)
            db.session.commit()
            db.session.add(group_alt)
            db.session.add(group_alt_location)
            db.session.commit()
            db.session.add_all(employees)
            db.session.add_all(employees_alt)
            db.session.add_all(employees_alt_location)
            db.session.commit()
            db.session.add_all(daily_orders)
            db.session.add_all(daily_orders_alt)
            db.session.add_all(daily_orders_alt_location)
            db.session.commit()

            login(user=user_kuechenpersonal_alt, client=client)

            res = client.get("/api/daily-orders/counted")
            assert res.status_code == 200
            assert len(res.json) == 1
            assert res.json[0]["location_id"] == str(location.id)
            assert res.json[0]["rot"] == 5
            assert res.json[0]["blau"] == 5
            assert res.json[0]["salad_option"] == 10

        def it_returns_all_locations_verwaltung(
            client,
            user_verwaltung,
            user_kuechenpersonal_alt,
            user_gruppenleitung,
            user_gruppenleitung_alt,
            user_gruppenleitung_alt_location,
            user_standortleitung,
            user_standortleitung_alt_location,
            location_alt,
            location,
            group,
            group_alt,
            group_alt_location,
            employees,
            employees_alt,
            employees_alt_location,
            daily_orders,
            daily_orders_alt,
            daily_orders_alt_location,
            db,
        ):
            db.session.add(user_verwaltung)
            db.session.add(user_gruppenleitung)
            db.session.add(user_standortleitung)
            db.session.add(user_standortleitung_alt_location)
            db.session.commit()
            db.session.add(location)
            db.session.add(location_alt)
            db.session.add(group)
            db.session.commit()
            db.session.add(user_gruppenleitung_alt)
            db.session.add(user_gruppenleitung_alt_location)
            db.session.add(user_kuechenpersonal_alt)
            db.session.commit()
            db.session.add(group_alt)
            db.session.add(group_alt_location)
            db.session.commit()
            db.session.add_all(employees)
            db.session.add_all(employees_alt)
            db.session.add_all(employees_alt_location)
            db.session.commit()
            db.session.add_all(daily_orders)
            db.session.add_all(daily_orders_alt)
            db.session.add_all(daily_orders_alt_location)
            db.session.commit()

            login(user=user_verwaltung, client=client)

            res = client.get("/api/daily-orders/counted")
            assert res.status_code == 200
            assert len(res.json) == 2
            assert res.json[0]["location_id"] == str(location.id)
            assert res.json[0]["rot"] == 5
            assert res.json[0]["blau"] == 5
            assert res.json[0]["salad_option"] == 10
            assert res.json[1]["location_id"] == str(location_alt.id)
            assert res.json[1]["rot"] == 5
            assert res.json[1]["blau"] == 0
            assert res.json[1]["salad_option"] == 5

        def unauthorized(
            client,
            user_gruppenleitung,
            db,
        ):
            db.session.add(user_gruppenleitung)
            db.session.commit()

            res = client.get("/api/daily-orders/counted")
            assert res.status_code == 401

            login(user=user_gruppenleitung, client=client)
            res = client.get("/api/daily-orders/counted")
            assert res.status_code == 403

    # TODO FIX THIS
    def describe_get_daily_order_own():
        def it_returns_daily_order(
            client,
            user_verwaltung,
            user_standortleitung,
            location,
            daily_order,
            db,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys =ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.commit()
            db.session.add(location)
            db.session.commit()
            daily_order.person_id = user_verwaltung.id
            db.session.add(daily_order)
            db.session.commit()

            login(user=user_verwaltung, client=client)
            res = client.get("/api/daily-orders/own")

            assert db.session.query(DailyOrder).count() == 1
            assert db.session.query(DailyOrder).first().person_id == user_verwaltung.id

            assert res.status_code == 200
            assert res.json["id"] == str(db.session.query(DailyOrder).first().id)

        def it_returns_no_daily_order_out_of_userscope():
            pass

        def it_returns_not_found(
            client,
            user_verwaltung,
            user_standortleitung,
            daily_order,
            db,
        ):
            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            daily_order.user_id = user_standortleitung.id
            db.session.add(daily_order)
            db.session.commit()

            login(user=user_verwaltung, client=client)
            res = client.get("/api/daily-orders/own")

            assert db.session.query(DailyOrder).count() == 1
            assert res.status_code == 404

        def unauthorized(client):
            res = client.get("/api/daily-orders/own")
            assert res.status_code == 401

    # TODO FIX THIS
    def describe_get_daily_order_person():
        def it_returns_daily_order(
            client,
            user_verwaltung,
            user_kuechenpersonal_alt,
            user_standortleitung,
            location,
            daily_order,
            db,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.commit()
            db.session.add(location)
            db.session.commit()
            db.session.add(user_kuechenpersonal_alt)
            daily_order.person_id = user_verwaltung.id
            db.session.add(daily_order)
            db.session.commit()

            login(user=user_kuechenpersonal_alt, client=client)
            res = client.get(f"/api/daily-orders/person/{user_verwaltung.id}")

            assert db.session.query(DailyOrder).count() == 1
            assert db.session.query(DailyOrder).first().person_id == user_verwaltung.id

            assert res.status_code == 200
            assert (
                res.json["person_id"]
                == str(db.session.query(DailyOrder).first().person_id)
                == str(user_verwaltung.id)
            )

        def it_returns_no_daily_order_out_of_scope():
            pass

        def it_returns_no_daily_order_not_found(
            client,
            user_verwaltung,
            user_kuechenpersonal,
            user_standortleitung,
            location,
            daily_order,
            db,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_kuechenpersonal)
            db.session.add(user_standortleitung)
            db.session.commit()
            db.session.add(location)
            db.session.commit()
            daily_order.person_id = user_verwaltung.id
            db.session.add(daily_order)
            db.session.commit()

            login(user=user_kuechenpersonal, client=client)
            res = client.get(f"/api/daily-orders/person/{uuid.uuid4()}")

            assert db.session.query(DailyOrder).count() == 1
            assert db.session.query(DailyOrder).first().person_id == user_verwaltung.id

            assert res.status_code == 404

        def unauthorized(
            client,
            user_verwaltung,
            db,
        ):
            db.session.add(user_verwaltung)
            db.session.commit()

            res = client.get(f"/api/daily-orders/person/{user_verwaltung.id}")
            assert res.status_code == 401

            login(user=user_verwaltung, client=client)
            res = client.get(f"/api/daily-orders/person/{user_verwaltung.id}")
            assert res.status_code == 403

    def describe_get_daily_orders_group():
        def it_returns_daily_orders():
            pass

        def it_returns_no_daily_orders_out_of_scope():
            pass

        def it_returns_no_daily_orders_not_found():
            pass

        def unauthorized():
            pass

    def describe_put_daily_order():
        def it_updates_daily_order():
            pass

        def it_dosnt_update_out_of_userscope():
            pass

        def it_returns_bad_value_error_on_update():
            pass

        def unauthorized():
            pass
