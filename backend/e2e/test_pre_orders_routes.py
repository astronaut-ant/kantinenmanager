""" ""End-to-End tests for the pre_orders routes."""

import uuid
from datetime import date, datetime, time
import datetime
from .helper import *  # for fixtures # noqa: F403
from .helper import login
from src.models.preorder import PreOrder


def describe_pre_orders():
    def describe_get():
        def it_returns_pre_orders(
            client,
            location,
            group,
            employees,
            user_verwaltung,
            user_standortleitung,
            user_gruppenleitung,
            pre_orders,
            pre_order,
            db,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)  # needed for location
            db.session.add(user_gruppenleitung)  # needed for group
            db.session.commit()  # needed
            db.session.add(location)  # needed for order
            db.session.add(group)  # needed for employees
            db.session.commit()
            db.session.add_all(employees)
            db.session.commit()
            db.session.add_all(pre_orders)
            pre_order.person_id = user_standortleitung.id
            db.session.add(pre_order)
            db.session.commit()

            login(user=user_verwaltung, client=client)

            res = client.get("/api/pre-orders")

            assert res.status_code == 200
            assert len(res.json) == 6

        def it_pre_orders_respective_to_userscope(
            client,
            location,
            group,
            employees,
            user_verwaltung,
            user_standortleitung,
            user_gruppenleitung,
            pre_orders,
            pre_order,
            db,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)  # needed for location
            db.session.add(user_gruppenleitung)  # needed for group
            db.session.commit()  # needed
            db.session.add(location)  # needed for order
            db.session.add(group)  # needed for employees
            db.session.commit()
            db.session.add_all(employees)
            db.session.commit()
            db.session.add_all(pre_orders)
            pre_order.person_id = user_standortleitung.id
            db.session.add(pre_order)
            db.session.commit()

            login(user=user_gruppenleitung, client=client)

            res = client.get("/api/pre-orders")

            assert res.status_code == 200
            assert (
                len(res.json) == 5
            )  # only 5 because user_standortleitung is not returned
            assert db.session.query(PreOrder).count() == 6

        def it_returns_filtered_pre_orders(
            client,
            location,
            group,
            employees,
            user_verwaltung,
            user_standortleitung,
            user_gruppenleitung,
            pre_orders,
            pre_order,
            db,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)  # needed for location
            db.session.add(user_gruppenleitung)  # needed for group
            db.session.commit()  # needed
            db.session.add(location)  # needed for order
            db.session.add(group)  # needed for employees
            db.session.commit()
            db.session.add_all(employees)
            db.session.commit()
            db.session.add_all(pre_orders)
            pre_order.person_id = user_standortleitung.id
            db.session.add(pre_order)
            db.session.commit()

            login(user=user_verwaltung, client=client)

            res = client.get(f"/api/pre-orders?group-id={group.id}")

            assert res.status_code == 200
            assert len(res.json) == 5
            assert db.session.query(PreOrder).count() == 6

        def it_returns_nothing_pre_orders_filter(
            client,
            location,
            group,
            employees,
            user_verwaltung,
            user_standortleitung,
            user_gruppenleitung,
            pre_orders,
            db,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)  # needed for location
            db.session.add(user_gruppenleitung)  # needed for group
            db.session.commit()  # needed
            db.session.add(location)  # needed for order
            db.session.add(group)  # needed for employees
            db.session.commit()
            db.session.add_all(employees)
            db.session.commit()
            db.session.add_all(pre_orders)
            db.session.commit()

            login(user=user_verwaltung, client=client)

            res = client.get(f"/api/pre-orders?group-id={uuid.uuid4()}")
            assert res.status_code == 200
            assert len(res.json) == 0
            assert db.session.query(PreOrder).count() != 0

        def it_returns_401_on_not_authorized(client):
            res = client.get("/api/pre-orders")
            assert res.status_code == 401

    def describe_get_int():
        def it_returns_pre_order(
            client,
            location,
            group,
            employees,
            user_verwaltung,
            user_standortleitung,
            user_gruppenleitung,
            pre_orders,
            db,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)  # needed for location
            db.session.add(user_gruppenleitung)  # needed for group
            db.session.commit()  # needed
            db.session.add(location)  # needed for order
            db.session.add(group)  # needed for employees
            db.session.commit()  # needed to import employees
            db.session.add_all(employees)  # needed for pre_orders
            db.session.commit()  # needed to import pre_orders
            db.session.add_all(pre_orders)
            db.session.commit()

            login(user=user_verwaltung, client=client)
            for order in pre_orders:
                res = client.get(f"/api/pre-orders/{order.id}")
                assert res.status_code == 200
                assert len(res.json) == 8
                assert res.json["id"] == str(order.id)

        def it_returns_403_for_order_out_of_userscope(
            client,
            location,
            group,
            employees,
            user_verwaltung,
            user_standortleitung,
            user_gruppenleitung,
            user_kuechenpersonal_alt,
            pre_orders,
            db,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)  # needed for location
            db.session.add(user_gruppenleitung)  # needed for group
            db.session.commit()  # needed
            db.session.add(location)  # needed for order
            db.session.add(group)  # needed for employees
            db.session.commit()  # needed to import employees
            db.session.add(user_kuechenpersonal_alt)
            db.session.add_all(employees)  # needed for pre_orders
            db.session.commit()  # needed to import pre_orders
            db.session.add_all(pre_orders)
            db.session.commit()

            login(user=user_kuechenpersonal_alt, client=client)

            for order in pre_orders:
                res = client.get(f"/api/pre-orders/{order.id}")
                assert res.status_code == 403

        def it_returns_404_if_not_found(
            client,
            location,
            group,
            employees,
            user_verwaltung,
            user_standortleitung,
            user_gruppenleitung,
            pre_orders,
            db,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)  # needed for location
            db.session.add(user_gruppenleitung)  # needed for group
            db.session.commit()  # needed
            db.session.add(location)  # needed for order
            db.session.add(group)  # needed for employees
            db.session.commit()  # needed to import employees
            db.session.add_all(employees)  # needed for pre_orders
            db.session.commit()  # needed to import pre_orders
            db.session.add_all(pre_orders)
            db.session.commit()

            login(user=user_verwaltung, client=client)

            res = client.get("/api/pre-orders/5000")
            assert res.status_code == 404

        def it_returns_401_and_403_on_not_authorized(client, user_standortleitung, db):
            res = client.get("/api/pre-orders/1")
            assert res.status_code == 401

            db.session.add(user_standortleitung)
            db.session.commit()

            login(user=user_standortleitung, client=client)

            resp = client.get("/api/pre-orders/1")
            assert resp.status_code == 403

    def describe_get_groupleader():
        def it_returns_pre_orders(
            client,
            location,
            group,
            employees,
            user_verwaltung,
            user_standortleitung,
            user_gruppenleitung,
            pre_orders,
            pre_order,
            db,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)  # needed for location
            db.session.add(user_gruppenleitung)  # needed for group
            db.session.commit()  # needed
            db.session.add(location)  # needed for order
            db.session.add(group)  # needed for employees
            db.session.commit()  # needed to import employees
            db.session.add_all(employees)  # needed for pre_orders
            db.session.commit()  # needed to import pre_orders
            db.session.add_all(pre_orders)
            pre_order.person_id = user_gruppenleitung.id
            db.session.add(pre_order)
            db.session.commit()

            login(user=user_gruppenleitung, client=client)
            res = client.get(
                f"/api/pre-orders/by-group-leader/{user_gruppenleitung.id}"
            )
            assert res.status_code == 200
            assert len(res.json) == 5
            assert db.session.query(PreOrder).count() == 6

        def it_returns_404_when_not_found(
            client, user_gruppenleitung, user_standortleitung, location, pre_order, db
        ):
            db.session.add(user_gruppenleitung)
            db.session.add(user_standortleitung)
            db.session.commit()
            db.session.add(location)
            db.session.commit()
            pre_order.person_id = user_gruppenleitung.id
            db.session.add(pre_order)
            db.session.commit()
            login(user=user_gruppenleitung, client=client)

            res = client.get(f"/api/pre-orders/by-group-leader/{uuid.uuid4()}")
            assert res.status_code == 404
            assert db.session.query(PreOrder).count() == 1

        def returns_correct_pre_orders_subsitute_group_leader(
            client,
            location,
            group,
            group_alt,
            employees,
            employees_alt,
            user_verwaltung,
            user_standortleitung,
            user_gruppenleitung,
            user_gruppenleitung_alt,
            pre_orders,
            pre_orders_alt,
            pre_order,
            db,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.add(user_gruppenleitung)
            db.session.commit()
            db.session.add(location)
            db.session.commit()
            db.session.add(user_gruppenleitung_alt)
            db.session.add(group)
            group_alt.user_id_replacement = user_gruppenleitung.id
            db.session.add(group_alt)
            db.session.commit()
            db.session.add_all(employees)
            db.session.add_all(employees_alt)
            db.session.commit()
            db.session.add_all(pre_orders)
            db.session.add_all(pre_orders_alt)
            pre_order.person_id = user_gruppenleitung.id
            db.session.add(pre_order)
            db.session.commit()

            login(user=user_gruppenleitung, client=client)
            res = client.get(
                f"/api/pre-orders/by-group-leader/{user_gruppenleitung.id}"
            )
            assert res.status_code == 200
            main_dish_count = sum(
                1
                for group in res.json["groups"]
                for order in group["orders"]
                if "main_dish" in order
            )
            assert main_dish_count == 10
            assert db.session.query(PreOrder).count() == 11

            group_alt.user_id_replacement = None
            db.session.commit()

            res = client.get(
                f"/api/pre-orders/by-group-leader/{user_gruppenleitung.id}"
            )
            assert res.status_code == 200
            main_dish_count = sum(
                1
                for group in res.json["groups"]
                for order in group["orders"]
                if "main_dish" in order
            )
            assert main_dish_count == 5
            assert db.session.query(PreOrder).count() == 11

        def it_returns_401_403_on_not_authorized(
            client, user_verwaltung, user_gruppenleitung, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(user_gruppenleitung)
            db.session.commit()

            res = client.get(f"/api/pre-orders/by-group-leader/{uuid.uuid4()}")
            assert res.status_code == 401

            login(user=user_verwaltung, client=client)
            res = client.get(
                f"/api/pre-orders/by-group-leader/{user_gruppenleitung.id}"
            )
            assert res.status_code == 403

    def describe_post_employees():
        def it_creates_pre_orders(
            client,
            location,
            group,
            employees,
            user_verwaltung,
            user_standortleitung,
            user_gruppenleitung,
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

            inte = 0
            employeesi = {}
            for employee in employees:
                employeesi[inte] = employee.id
                inte += 1

            forward = datetime.date.today().weekday()
            if forward > 2 and forward < 5:
                forward = 4
            else:
                forward = 2

            body = [
                {
                    "date": (
                        datetime.date.today() + datetime.timedelta(days=forward)
                    ).isoformat(),
                    "location_id": location.id,
                    "main_dish": "rot",
                    "nothing": False,
                    "person_id": employeesi[i],
                    "salad_option": True,
                }
                for i in range(3)
            ]

            res = client.post("/api/pre-orders", json=body)
            assert res.status_code == 201
            assert db.session.query(PreOrder).count() == 3

        def it_does_not_create_based_on_userscope_409(
            client,
            location,
            group,
            employees,
            user_verwaltung,
            user_standortleitung,
            user_gruppenleitung,
            user_gruppenleitung_alt,
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
            db.session.add_all(employees)
            db.session.commit()

            login(user=user_gruppenleitung_alt, client=client)

            inte = 0
            employeesi = {}
            for employee in employees:
                employeesi[inte] = employee.id
                inte += 1

            forward = datetime.date.today().weekday()
            if forward > 2 and forward < 5:
                forward = 4
            else:
                forward = 2

            body = [
                {
                    "date": (
                        datetime.date.today() + datetime.timedelta(days=forward)
                    ).isoformat(),
                    "location_id": location.id,
                    "main_dish": "rot",
                    "nothing": False,
                    "person_id": employeesi[i],
                    "salad_option": True,
                }
                for i in range(3)
            ]

            res = client.post("/api/pre-orders", json=body)
            assert res.status_code == 409
            assert db.session.query(PreOrder).count() == 0

        def does_not_create_two_for_same_day(
            client,
            location,
            group,
            employees,
            user_verwaltung,
            user_standortleitung,
            user_gruppenleitung,
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

            inte = 0
            employeesi = {}
            for employee in employees:
                employeesi[inte] = employee.id
                inte += 1

            forward = datetime.date.today().weekday()
            if forward > 2 and forward < 5:
                forward = 4
            else:
                forward = 2

            body = [
                {
                    "date": (
                        datetime.date.today() + datetime.timedelta(days=forward)
                    ).isoformat(),
                    "location_id": location.id,
                    "main_dish": "rot",
                    "nothing": False,
                    "person_id": employeesi[0],
                    "salad_option": True,
                }
                for i in range(2)
            ]

            res = client.post("/api/pre-orders", json=body)
            assert res.status_code == 201
            assert db.session.query(PreOrder).count() == 1

        def correctly_adjusts_pre_orders(
            client,
            location,
            group,
            employees,
            user_verwaltung,
            user_standortleitung,
            user_gruppenleitung,
            pre_orders,
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

            forward = datetime.date.today().weekday()
            if forward > 2 and forward < 5:
                forward = 4
            else:
                forward = 2

            body = [
                {
                    "date": (
                        datetime.date.today() + datetime.timedelta(days=forward)
                    ).isoformat(),
                    "location_id": preorder.location_id,
                    "main_dish": "blau",  # noqa: F405
                    "nothing": False,
                    "person_id": preorder.person_id,
                    "salad_option": True,
                }
                for preorder in pre_orders
            ]

            client.post("/api/pre-orders", json=body)

            assert (
                db.session.query(PreOrder)
                .filter(PreOrder.nothing == False)  # noqa: E712
                .count()
                == 5
            )

            body = [
                {
                    "date": (
                        datetime.date.today() + datetime.timedelta(days=forward)
                    ).isoformat(),
                    "location_id": preorder.location_id,
                    "main_dish": None,  # noqa: F405
                    "nothing": True,
                    "person_id": preorder.person_id,
                    "salad_option": False,
                }
                for preorder in pre_orders
            ]

            res = client.post("/api/pre-orders", json=body)
            assert res.status_code == 201

            assert db.session.query(PreOrder).count() == 5
            assert (
                db.session.query(PreOrder)
                .filter(PreOrder.nothing == True)  # noqa: E712
                .count()
                == 5
            )
            assert (
                db.session.query(PreOrder)
                .filter(PreOrder.nothing == False)  # noqa: E712
                .count()
                == 0
            )

        def it_returns_401_403_on_not_authorized(client, user_standortleitung, db):
            db.session.add(user_standortleitung)
            db.session.commit()

            res = client.post("/api/pre-orders")
            assert res.status_code == 401

            login(user=user_standortleitung, client=client)
            res = client.post("/api/pre-orders")
            assert res.status_code == 403

    def describe_post_user():
        def it_creates_pre_order(
            client,
            location,
            user_verwaltung,
            user_standortleitung,
            db,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.commit()
            db.session.add(location)

            login(user=user_verwaltung, client=client)

            forward = datetime.date.today().weekday()
            if forward > 2 and forward < 5:
                forward = 4
            else:
                forward = 2

            body = {
                "date": (
                    datetime.date.today() + datetime.timedelta(days=forward)
                ).isoformat(),
                "location_id": location.id,
                "main_dish": "rot",
                "nothing": False,
                "person_id": user_verwaltung.id,
                "salad_option": True,
            }

            res = client.post("/api/pre-orders/users", json=body)

            assert res.status_code == 201
            assert db.session.query(PreOrder).count() == 1

        def it_does_not_create_based_on_userscope(
            client,
            location,
            user_verwaltung,
            user_standortleitung,
            db,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.commit()
            db.session.add(location)

            login(user=user_verwaltung, client=client)

            forward = datetime.date.today().weekday()
            if forward > 2 and forward < 5:
                forward = 4
            else:
                forward = 2

            body = {
                "date": (
                    datetime.date.today() + datetime.timedelta(days=forward)
                ).isoformat(),
                "location_id": location.id,
                "main_dish": "rot",
                "nothing": False,
                "person_id": user_standortleitung.id,
                "salad_option": True,
            }

            res = client.post("/api/pre-orders/users", json=body)

            assert res.status_code == 403
            assert db.session.query(PreOrder).count() == 0

        def does_not_create_two_for_same_day(
            client,
            location,
            user_verwaltung,
            user_standortleitung,
            db,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.commit()
            db.session.add(location)
            db.session.commit()

            login(user=user_verwaltung, client=client)

            forward = datetime.date.today().weekday()
            if forward > 2 and forward < 5:
                forward = 4
            else:
                forward = 2

            body = {
                "date": (
                    datetime.date.today() + datetime.timedelta(days=forward)
                ).isoformat(),
                "location_id": location.id,
                "main_dish": "rot",
                "nothing": False,
                "person_id": user_verwaltung.id,
                "salad_option": True,
            }

            res = client.post("/api/pre-orders/users", json=body)

            assert res.status_code == 201
            assert db.session.query(PreOrder).count() == 1

            body = {
                "date": (
                    datetime.date.today() + datetime.timedelta(days=forward)
                ).isoformat(),
                "location_id": location.id,
                "main_dish": "rot",
                "nothing": False,
                "person_id": user_verwaltung.id,
                "salad_option": True,
            }

            res = client.post("/api/pre-orders/users", json=body)

            assert res.status_code == 409
            assert db.session.query(PreOrder).count() == 1

        def does_not_create_on_weekend(
            client,
            location,
            user_verwaltung,
            user_standortleitung,
            db,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.commit()
            db.session.add(location)
            db.session.commit()

            login(user=user_verwaltung, client=client)

            forward = datetime.date.today().weekday()
            forward = 6 - forward
            if forward == 0:
                forward = 7

            body = {
                "date": (
                    datetime.date.today() + datetime.timedelta(days=forward)
                ).isoformat(),
                "location_id": location.id,
                "main_dish": "rot",
                "nothing": False,
                "person_id": user_verwaltung.id,
                "salad_option": True,
            }

            res = client.post("/api/pre-orders/users", json=body)

            assert res.status_code == 400
            assert db.session.query(PreOrder).count() == 0

        def does_not_create_14_days_in_advance(
            client,
            location,
            user_verwaltung,
            user_standortleitung,
            db,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.commit()
            db.session.add(location)
            db.session.commit()

            login(user=user_verwaltung, client=client)

            forward = datetime.date.today().weekday()
            if forward > 2 and forward < 5:
                forward = 18
            else:
                forward = 16

            body = {
                "date": (
                    datetime.date.today() + datetime.timedelta(days=forward)
                ).isoformat(),
                "location_id": location.id,
                "main_dish": "rot",
                "nothing": False,
                "person_id": user_verwaltung.id,
                "salad_option": True,
            }

            res = client.post("/api/pre-orders/users", json=body)

            assert res.status_code == 400
            assert db.session.query(PreOrder).count() == 0

        def returns_401_on_not_authorized(client):
            res = client.post("/api/pre-orders/users")
            assert res.status_code == 401

    def describe_put_user():
        def it_updates_pre_order(
            client,
            location,
            user_verwaltung,
            user_standortleitung,
            db,
            pre_order,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.commit()
            db.session.add(location)
            pre_order.id = 1
            pre_order.person_id = user_verwaltung.id
            db.session.add(pre_order)
            db.session.commit()

            login(user=user_verwaltung, client=client)

            forward = datetime.date.today().weekday()
            if forward > 2 and forward < 5:
                forward = 4
            else:
                forward = 2

            assert db.session.query(PreOrder).first().nothing == False  # noqa: E712

            body = {
                "date": (
                    datetime.date.today() + datetime.timedelta(days=forward)
                ).isoformat(),
                "location_id": location.id,
                "main_dish": None,
                "nothing": True,
                "person_id": user_verwaltung.id,
                "salad_option": False,
            }

            preorderid = db.session.query(PreOrder).first().id

            res = client.put(f"/api/pre-orders/{preorderid}", json=body)

            assert res.status_code == 200
            assert db.session.query(PreOrder).count() == 1
            assert db.session.query(PreOrder).first().nothing == True  # noqa: E712

        def it_does_not_update_based_on_userscope_403(
            client,
            location,
            user_verwaltung,
            user_standortleitung,
            db,
            pre_order,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.commit()
            db.session.add(location)
            pre_order.id = 1
            pre_order.person_id = user_standortleitung.id
            db.session.add(pre_order)
            db.session.commit()

            login(user=user_verwaltung, client=client)

            forward = datetime.date.today().weekday()
            if forward > 2 and forward < 5:
                forward = 4
            else:
                forward = 2

            assert db.session.query(PreOrder).first().nothing == False  # noqa: E712

            body = {
                "date": (
                    datetime.date.today() + datetime.timedelta(days=forward)
                ).isoformat(),
                "location_id": location.id,
                "main_dish": None,
                "nothing": True,
                "person_id": user_verwaltung.id,
                "salad_option": False,
            }

            preorderid = db.session.query(PreOrder).first().id

            res = client.put(f"/api/pre-orders/{preorderid}", json=body)

            assert res.status_code == 403
            assert db.session.query(PreOrder).count() == 1
            assert db.session.query(PreOrder).first().nothing == False  # noqa: E712

        def does_not_update_if_not_found_404(
            client,
            location,
            user_verwaltung,
            user_standortleitung,
            db,
            pre_order,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.commit()
            db.session.add(location)
            pre_order.id = 1
            pre_order.person_id = user_verwaltung.id
            db.session.add(pre_order)
            db.session.commit()

            login(user=user_verwaltung, client=client)

            forward = datetime.date.today().weekday()
            if forward > 2 and forward < 5:
                forward = 4
            else:
                forward = 2

            assert db.session.query(PreOrder).first().nothing == False  # noqa: E712

            body = {
                "date": (
                    datetime.date.today() + datetime.timedelta(days=forward)
                ).isoformat(),
                "location_id": location.id,
                "main_dish": None,
                "nothing": True,
                "person_id": user_verwaltung.id,
                "salad_option": False,
            }

            preorderid = db.session.query(PreOrder).first().id

            res = client.put(f"/api/pre-orders/{preorderid+1}", json=body)

            assert res.status_code == 404
            assert db.session.query(PreOrder).count() == 1
            assert db.session.query(PreOrder).first().nothing == False  # noqa: E712

        def does_not_update_two_for_same_day_409(
            client,
            location,
            user_verwaltung,
            user_standortleitung,
            db,
            pre_order,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            forward = datetime.date.today().weekday()
            if forward > 1 and forward < 5:
                forward = 5
            else:
                forward = 2

            preoderone = PreOrder(
                date=datetime.date.today() + datetime.timedelta(days=forward),
                location_id=location.id,
                main_dish="rot",
                nothing=False,
                person_id=user_verwaltung.id,
                salad_option=True,
            )

            preordertwo = PreOrder(
                date=datetime.date.today() + datetime.timedelta(days=forward + 1),
                location_id=location.id,
                main_dish="rot",
                nothing=True,
                person_id=user_verwaltung.id,
                salad_option=True,
            )

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.commit()
            db.session.add(location)
            db.session.commit()
            db.session.add(preoderone)
            db.session.add(preordertwo)
            db.session.commit()

            login(user=user_verwaltung, client=client)

            dateToCheck = datetime.datetime.combine(
                datetime.date.today() + datetime.timedelta(days=forward + 1), time(0, 0)
            )

            assert (
                db.session.query(PreOrder).filter(PreOrder.date == dateToCheck).count()
                == 1
            )  # noqa: E712

            body = {
                "date": (
                    datetime.date.today() + datetime.timedelta(days=forward + 1)
                ).isoformat(),
                "location_id": location.id,
                "main_dish": "rot",
                "nothing": False,
                "person_id": user_verwaltung.id,
                "salad_option": True,
            }

            preorderid = db.session.query(PreOrder).first().id

            res = client.put(f"/api/pre-orders/{preorderid}", json=body)

            assert res.status_code == 409
            assert db.session.query(PreOrder).count() == 2
            assert (
                db.session.query(PreOrder).filter(PreOrder.date == dateToCheck).count()
                == 1
            )  # noqa: E712

        def does_not_update_on_weekend_400(
            client,
            location,
            user_verwaltung,
            user_standortleitung,
            db,
            pre_order,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.commit()
            db.session.add(location)
            pre_order.id = 1
            pre_order.person_id = user_verwaltung.id
            db.session.add(pre_order)
            db.session.commit()

            login(user=user_verwaltung, client=client)

            forward = datetime.date.today().weekday()
            forward = 6 - forward
            if forward == 0:
                forward = 7

            datum = db.session.query(PreOrder).first().date

            body = {
                "date": (
                    datetime.date.today() + datetime.timedelta(days=forward)
                ).isoformat(),
                "location_id": location.id,
                "main_dish": None,
                "nothing": True,
                "person_id": user_verwaltung.id,
                "salad_option": False,
            }

            preorderid = db.session.query(PreOrder).first().id

            res = client.put(f"/api/pre-orders/{preorderid}", json=body)

            assert res.status_code == 400
            assert db.session.query(PreOrder).count() == 1
            assert db.session.query(PreOrder).first().date == datum  # noqa: E712

        def does_not_update_14_days_in_advance_400(
            client,
            location,
            user_verwaltung,
            user_standortleitung,
            db,
            pre_order,
        ):
            # enforce foreign key constraints just for this test
            db.session.execute(text("PRAGMA foreign_keys = ON"))  # noqa: F405

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.commit()
            db.session.add(location)
            pre_order.id = 1
            pre_order.person_id = user_verwaltung.id
            db.session.add(pre_order)
            db.session.commit()

            login(user=user_verwaltung, client=client)

            forward = datetime.date.today().weekday()
            forward = datetime.date.today().weekday()
            if forward > 1 and forward < 5:
                forward = 19
            else:
                forward = 21

            datum = db.session.query(PreOrder).first().date

            body = {
                "date": (
                    datetime.date.today() + datetime.timedelta(days=forward)
                ).isoformat(),
                "location_id": location.id,
                "main_dish": None,
                "nothing": True,
                "person_id": user_verwaltung.id,
                "salad_option": False,
            }

            preorderid = db.session.query(PreOrder).first().id

            res = client.put(f"/api/pre-orders/{preorderid}", json=body)

            assert res.status_code == 400
            assert db.session.query(PreOrder).count() == 1
            assert db.session.query(PreOrder).first().date == datum  # noqa: E712

        def returns_401_on_not_authorized(client):
            res = client.put("/api/pre-orders/1")
            assert res.status_code == 401

    def describe_delete_user():
        def it_deletes_pre_order(
            client,
            location,
            user_verwaltung,
            user_standortleitung,
            db,
            pre_order,
        ):
            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.commit()
            db.session.add(location)
            pre_order.id = 1
            pre_order.person_id = user_verwaltung.id
            db.session.add(pre_order)
            db.session.commit()

            login(user=user_verwaltung, client=client)

            preorderid = int(db.session.query(PreOrder).first().id)

            assert db.session.query(PreOrder).count() == 1

            res = client.delete(f"/api/pre-orders/{preorderid}")
            assert res.status_code == 204
            assert db.session.query(PreOrder).count() == 0

        def it_does_not_delete_based_on_userscope_403(
            client,
            location,
            user_verwaltung,
            user_standortleitung,
            db,
            pre_order,
        ):
            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.commit()
            db.session.add(location)
            pre_order.id = 1
            pre_order.person_id = user_standortleitung.id
            db.session.add(pre_order)
            db.session.commit()

            login(user=user_verwaltung, client=client)

            preorderid = int(db.session.query(PreOrder).first().id)

            assert db.session.query(PreOrder).count() == 1

            res = client.delete(f"/api/pre-orders/{preorderid}")
            assert res.status_code == 403
            assert db.session.query(PreOrder).count() == 1

        def returns_404_on_not_found(
            client,
            location,
            user_verwaltung,
            user_standortleitung,
            db,
            pre_order,
        ):
            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.commit()
            db.session.add(location)
            pre_order.id = 1
            pre_order.person_id = user_verwaltung.id
            db.session.add(pre_order)
            db.session.commit()

            login(user=user_verwaltung, client=client)

            preorderid = int(db.session.query(PreOrder).first().id)

            assert db.session.query(PreOrder).count() == 1

            res = client.delete(f"/api/pre-orders/{preorderid+1}")
            assert res.status_code == 404
            assert db.session.query(PreOrder).count() == 1

        def returns_401_on_not_authorized(client):
            res = client.delete("/api/pre-orders/1")
            assert res.status_code == 401
