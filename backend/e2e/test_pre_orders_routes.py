""" ""End-to-End tests for the pre_orders routes."""

import uuid
import datetime
from .helper import *  # for fixtures # noqa: F403
from .helper import login
from src.models.preorder import PreOrder
from src.models.location import Location
from src.models.user import UserGroup, User
from src.models.employee import Employee


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
            db.session.execute(text("PRAGMA foreign_keys = ON"))

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

        def it_returns_userscope_pre_orders(
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
            db.session.execute(text("PRAGMA foreign_keys = ON"))

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

        def it_returns_pre_orders_filter(
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
            db.session.execute(text("PRAGMA foreign_keys = ON"))

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
            db.session.execute(text("PRAGMA foreign_keys = ON"))

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
            db.session.execute(text("PRAGMA foreign_keys = ON"))

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

        def it_returns_pre_order_userscope(
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
            # db.session.execute(text("PRAGMA foreign_keys = ON"))

            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)  # needed for location
            db.session.add(user_gruppenleitung)  # needed for group
            db.session.add(user_kuechenpersonal_alt)
            db.session.commit()  # needed
            db.session.add(location)  # needed for order
            db.session.add(group)  # needed for employees
            db.session.commit()  # needed to import employees
            db.session.add_all(employees)  # needed for pre_orders
            db.session.commit()  # needed to import pre_orders
            db.session.add_all(pre_orders)
            db.session.commit()

            login(user=user_kuechenpersonal_alt, client=client)

            for order in pre_orders:
                res = client.get(f"/api/pre-orders/{order.id}")
                assert res.status_code == 403

        def it_returns_pre_order_not_found(
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
            db.session.execute(text("PRAGMA foreign_keys = ON"))

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

            res = client.get(f"/api/pre-orders/{uuid.uuid4()}")
            assert res.status_code == 404
