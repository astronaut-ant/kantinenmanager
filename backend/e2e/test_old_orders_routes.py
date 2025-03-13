""" ""End-to-End tests for the old_orders routes."""

import uuid
from .helper import *  # for fixtures # noqa: F403
from .helper import login  # noqa: F401
from src.models.oldorder import OldOrder


def describe_old_orders():
    def describe_get_old_orders():
        def it_returns_old_orders(
            client,
            user_verwaltung,
            user_standortleitung,
            user_gruppenleitung,
            location,
            group,
            employees,
            old_orders,
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
            db.session.add_all(old_orders)
            db.session.commit()

            login(user=user_verwaltung, client=client)

            res = client.get("/api/old-orders")

            assert res.status_code == 200
            assert len(res.json) == 5

        def it_returns_filted_old_orders(
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
            old_orders,
            old_orders_alt,
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
            db.session.add(group_alt)
            db.session.add_all(old_orders)
            db.session.commit()
            db.session.add_all(employees_alt)
            db.session.commit()
            db.session.add_all(old_orders_alt)
            db.session.commit()

            login(user=user_verwaltung, client=client)

            res = client.get("/api/old-orders?group-id=" + str(group.id))

            assert res.status_code == 200
            assert len(res.json) == 5
            assert db.session.query(OldOrder).count() == 10

        def it_returns_no_old_orders_not_found(
            client,
            user_verwaltung,
            user_standortleitung,
            user_gruppenleitung,
            location,
            group,
            employees,
            old_orders,
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
            db.session.add_all(old_orders)
            db.session.commit()

            login(user=user_verwaltung, client=client)

            res = client.get(f"/api/old-orders?group-id={uuid.uuid4()}")

            assert res.status_code == 404
            assert db.session.query(OldOrder).count() == 5

        def it_returns_400_on_invalid_input(
            client,
            user_verwaltung,
            user_standortleitung,
            user_gruppenleitung,
            location,
            group,
            employees,
            old_orders,
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
            db.session.add_all(old_orders)
            db.session.commit()

            login(user=user_verwaltung, client=client)

            res = client.get("/api/old-orders?group_id=321")

            assert res.status_code == 400
            assert res.json["title"] == "Validierungsfehler"

        def it_returns_401_403_on_unauthorized(
            client,
            user_standortleitung,
            db,
        ):
            db.session.add(user_standortleitung)
            db.session.commit()

            res = client.get("/api/old-orders")
            assert res.status_code == 401

            login(user=user_standortleitung, client=client)

            res = client.get("/api/old-orders")
            assert res.status_code == 403
