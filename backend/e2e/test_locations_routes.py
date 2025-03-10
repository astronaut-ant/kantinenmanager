"""End-to-End tests for the locations routes."""

import uuid
from .helper import *  # for fixtures # noqa: F403
from .helper import login
from src.models.location import Location
from src.models.user import UserGroup, User


def describe_locations():
    def describe_get():
        def it_returns_all_locations_for_verwaltung(
            client, user_verwaltung, location, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get("/api/locations")

            assert res.status_code == 200
            assert len(res.json) == 1
            assert res.json[0]["id"] == str(location.id)

        def it_returns_multiple_locations(
            client, user_verwaltung, location, other_location, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.add(other_location)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get("/api/locations")

            assert res.status_code == 200
            assert len(res.json) == 2

        def it_blocks_unauthenticated_users(client):
            res = client.get("/api/locations")

            assert res.status_code == 401

        def it_blocks_non_verwaltung_users(client, user_standortleitung, db):
            db.session.add(user_standortleitung)
            db.session.commit()
            login(user=user_standortleitung, client=client)

            res = client.get("/api/locations")

            assert res.status_code == 403

    def describe_get_by_id():
        def it_returns_location_by_id(client, user_verwaltung, location, db):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get(f"/api/locations/{location.id}")

            assert res.status_code == 200
            assert res.json["id"] == str(location.id)
            assert res.json["location_name"] == location.location_name

        def it_returns_404_if_location_does_not_exist(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get(f"/api/locations/{uuid.uuid4()}")

            assert res.status_code == 404

        def it_blocks_non_verwaltung_users(client, user_standortleitung, location, db):
            db.session.add(user_standortleitung)
            db.session.add(location)
            db.session.commit()
            login(user=user_standortleitung, client=client)

            res = client.get(f"/api/locations/{location.id}")

            assert res.status_code == 403

    def describe_post():
        def it_creates_location(client, user_verwaltung, user_standortleitung, db):
            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "location_name": "New Location",
                "user_id_location_leader": str(user_standortleitung.id),
            }

            res = client.post("/api/locations", json=body)

            assert res.status_code == 201
            assert "location_id" in res.json

            all_locations = db.session.query(Location).all()
            assert len(all_locations) == 1
            assert all_locations[0].location_name == "New Location"

        def it_returns_400_for_missing_fields(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.post("/api/locations", json={})

            assert res.status_code == 400

        def it_checks_for_taken_location_name(
            client, user_verwaltung, location, user_standortleitung, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.add(user_standortleitung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "location_name": location.location_name,
                "user_id_location_leader": str(user_standortleitung.id),
            }

            res = client.post("/api/locations", json=body)

            assert res.status_code == 409
            assert "Standort" in res.json["title"]

        def it_checks_for_user_already_being_location_leader(
            client, user_verwaltung, location, user_standortleitung, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.add(user_standortleitung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "location_name": "Different Location",
                "user_id_location_leader": str(location.user_id_location_leader),
            }

            res = client.post("/api/locations", json=body)

            assert res.status_code == 409
            assert "als Standortleiter" in res.json["details"]

    def describe_put():
        def it_updates_location(
            client, user_verwaltung, location, user_standortleitung, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.add(user_standortleitung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "location_name": "Updated Location",
                "user_id_location_leader": str(user_standortleitung.id),
            }

            res = client.put(f"/api/locations/{location.id}", json=body)

            assert res.status_code == 200
            assert location.location_name == "Updated Location"
            assert location.user_id_location_leader == user_standortleitung.id

        def it_returns_404_if_location_does_not_exist(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "location_name": "Updated Location",
                "user_id_location_leader": str(uuid.uuid4()),
            }

            res = client.put(f"/api/locations/{uuid.uuid4()}", json=body)

            assert res.status_code == 404

        def it_checks_for_taken_location_name(
            client, user_verwaltung, location, other_location, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.add(other_location)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "location_name": other_location.location_name,
                "user_id_location_leader": str(location.user_id_location_leader),
            }

            res = client.put(f"/api/locations/{location.id}", json=body)

            assert res.status_code == 409

    def describe_delete():
        def it_deletes_location(client, user_verwaltung, location, db):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.delete(f"/api/locations/{location.id}")

            assert res.status_code == 200
            assert "erfolgreich gelöscht" in res.json["message"]

            remaining_locations = db.session.query(Location).all()
            assert len(remaining_locations) == 0

        def it_returns_404_if_location_does_not_exist(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.delete(f"/api/locations/{uuid.uuid4()}")

            assert res.status_code == 404

        def it_returns_400_if_location_has_dependencies(
            client, user_verwaltung, location, group, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.add(group)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.delete(f"/api/locations/{location.id}")

            assert res.status_code == 400
            assert "Gruppen" in res.json["description"]
