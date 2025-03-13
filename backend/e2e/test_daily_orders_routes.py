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
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

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

        def it_returns_respective_to_userscope(
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
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.add(user_gruppenleitung)
            db.session.add(user_standortleitung_alt_location)
            db.session.commit()
            db.session.add(location)
            db.session.add(location_alt)
            db.session.add(group)
            db.session.commit()
            db.session.add(user_kuechenpersonal_alt)
            db.session.add_all(employees)
            db.session.commit()
            daily_order.location_id = location_alt.id
            daily_order.person_id = user_standortleitung_alt_location.id
            db.session.add(daily_order)
            db.session.add_all(daily_orders)
            db.session.commit()

            login(user=user_kuechenpersonal_alt, client=client)
            response = client.get("/api/daily-orders")
            assert response.status_code == 200
            assert len(response.json) == 5
            assert db.session.query(DailyOrder).count() == 6

        def it_returns_401_403_on_unauthorized(client, user_gruppenleitung, db):
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
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

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
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

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
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

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

        def it_returns_401_403_on_unauthorized(
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

        def it_returns_not_found_404_when_order_out_of_userscope(
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
            daily_order.person_id = user_standortleitung.id
            db.session.add(daily_order)
            db.session.commit()

            login(user=user_verwaltung, client=client)
            res = client.get("/api/daily-orders/own")

            assert res.status_code == 404

        def it_returns_not_found_404_when_no_order_exists(
            client,
            user_verwaltung,
            db,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys =ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.commit()

            login(user=user_verwaltung, client=client)
            res = client.get("/api/daily-orders/own")

            assert res.status_code == 404

        def it_returns_401_on_unauthorized(client):
            res = client.get("/api/daily-orders/own")
            assert res.status_code == 401

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

        def it_returns_access_denied_403_when_wrong_location(
            client,
            user_verwaltung,
            user_kuechenpersonal_alt,
            user_standortleitung_alt_location,
            user_standortleitung,
            location,
            location_alt,
            daily_order,
            db,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.add(user_standortleitung_alt_location)
            db.session.commit()
            db.session.add(location)
            db.session.add(location_alt)
            db.session.commit()
            db.session.add(user_kuechenpersonal_alt)
            daily_order.person_id = user_standortleitung_alt_location.id
            daily_order.location_id = location_alt.id
            db.session.add(daily_order)
            db.session.commit()

            login(user=user_kuechenpersonal_alt, client=client)
            res = client.get(
                f"/api/daily-orders/person/{user_standortleitung_alt_location.id}"
            )

            assert db.session.query(DailyOrder).count() == 1
            assert res.status_code == 403

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

        def it_returns_401_403_on_unauthorized(
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
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

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

            login(user=user_gruppenleitung, client=client)
            res = client.get(f"/api/daily-orders/{group.id}")

            assert res.status_code == 200
            assert len(res.json) == 5
            assert db.session.query(DailyOrder).count() == 5

        def it_returns_no_daily_orders_out_of_scope(
            client,
            user_verwaltung,
            user_standortleitung,
            user_gruppenleitung,
            user_gruppenleitung_alt,
            location,
            group,
            group_alt,
            employees,
            employees_alt,
            daily_orders,
            daily_orders_alt,
            db,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.add(user_gruppenleitung)
            db.session.commit()
            db.session.add(location)
            db.session.add(group)
            db.session.commit()
            db.session.add(user_gruppenleitung_alt)
            db.session.commit()
            db.session.add(group_alt)
            db.session.commit()
            db.session.add_all(employees)
            db.session.add_all(employees_alt)
            db.session.commit()
            db.session.add_all(daily_orders)
            db.session.add_all(daily_orders_alt)
            db.session.commit()

            login(user=user_gruppenleitung, client=client)
            res = client.get(f"/api/daily-orders/{group.id}")

            assert res.status_code == 200
            assert len(res.json) == 5
            assert db.session.query(DailyOrder).count() == 10

            res = client.get(f"/api/daily-orders/{group_alt.id}")

            assert res.status_code == 403

        def it_returns_no_daily_orders_not_found(
            client,
            user_verwaltung,
            user_standortleitung,
            user_gruppenleitung,
            location,
            group,
            employees,
            db,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.add(user_gruppenleitung)
            db.session.commit()
            db.session.add(location)
            db.session.add(group)
            db.session.commit()
            db.session.add_all(employees)
            db.session.commit()

            login(user=user_gruppenleitung, client=client)
            res = client.get(f"/api/daily-orders/{group.id}")

            assert res.status_code == 200
            assert len(res.json) == 0
            assert db.session.query(DailyOrder).count() == 0

        def it_returns_404_on_group_not_found(
            client,
            user_verwaltung,
            user_gruppenleitung,
            db,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_gruppenleitung)
            db.session.commit()

            login(user=user_gruppenleitung, client=client)
            res = client.get(f"/api/daily-orders/{uuid.uuid4()}")
            assert res.status_code == 404

        def it_returns_401_403_on_unauthorized(
            client,
            user_verwaltung,
            db,
        ):
            db.session.add(user_verwaltung)
            db.session.commit()

            res = client.get(f"/api/daily-orders/{uuid.uuid4()}")
            assert res.status_code == 401

            login(user=user_verwaltung, client=client)
            res = client.get(f"/api/daily-orders/{uuid.uuid4()}")
            assert res.status_code == 403

    def describe_put_daily_order():
        def it_updates_daily_order(
            client,
            user_verwaltung,
            user_standortleitung,
            user_kuechenpersonal_alt,
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

            body = {"handed_out": True}

            login(user=user_kuechenpersonal_alt, client=client)

            assert (
                db.session.query(DailyOrder).first().handed_out == False  # noqa: E712
            )

            orderid = db.session.query(DailyOrder).first().id
            res = client.put(f"/api/daily-orders/{orderid}", json=body)

            assert res.status_code == 200
            assert db.session.query(DailyOrder).first().handed_out == True  # noqa: E712

        def it_dosnt_update_403_when_out_of_userscope(
            client,
            user_verwaltung,
            user_standortleitung,
            user_kuechenpersonal,
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
            db.session.add(user_kuechenpersonal)
            daily_order.person_id = user_verwaltung.id
            db.session.add(daily_order)
            db.session.commit()

            body = {"handed_out": True}

            login(user=user_kuechenpersonal, client=client)

            assert (
                db.session.query(DailyOrder).first().handed_out == False  # noqa: E712
            )

            orderid = db.session.query(DailyOrder).first().id
            res = client.put(f"/api/daily-orders/{orderid}", json=body)

            assert res.status_code == 403
            assert (
                db.session.query(DailyOrder).first().handed_out == False  # noqa: E712
            )

        def it_returns_bad_value_error_400_on_second_update(
            client,
            user_verwaltung,
            user_standortleitung,
            user_kuechenpersonal_alt,
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
            daily_order.handed_out = True
            db.session.add(daily_order)
            db.session.commit()

            body = {"handed_out": True}

            login(user=user_kuechenpersonal_alt, client=client)

            assert db.session.query(DailyOrder).first().handed_out == True  # noqa: E712

            daily_order_id = db.session.query(DailyOrder).first().id
            handed_out = True
            res = client.put(f"/api/daily-orders/{daily_order_id}", json=body)

            assert res.status_code == 400
            assert res.json["title"] == "Eingabefehler"
            assert (
                res.json["details"]
                == f"Ungültiger Wert: Bestellung {daily_order_id} wurde bereits als {handed_out} markiert"
            )
            assert db.session.query(DailyOrder).first().handed_out == True  # noqa: E712

        def it_returns_not_found_404_when_order_not_exists(
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

            body = {"handed_out": True}
            login(user=user_kuechenpersonal_alt, client=client)

            pre_order_id = db.session.query(DailyOrder).first().id

            res = client.put(f"/api/daily-orders/{pre_order_id+1}", json=body)

            assert res.status_code == 404
            assert (
                db.session.query(DailyOrder).first().handed_out == False  # noqa: E712
            )

        def it_returns_401_on_unauthorized(client, user_standortleitung, db):
            db.session.add(user_standortleitung)
            db.session.commit()

            res = client.put("/api/daily-orders/1", json={"handed_out": True})
            assert res.status_code == 401

            login(user=user_standortleitung, client=client)
            res = client.put("/api/daily-orders/1", json={"handed_out": True})
            assert res.status_code == 403
