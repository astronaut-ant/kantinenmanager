"""End-to-End tests for the groups routes."""

import uuid
from .helper import *  # for fixtures # noqa: F403
from .helper import login
from src.models.group import Group
from src.models.location import Location
from src.models.user import UserGroup, User
from src.models.employee import Employee


def describe_groups():
    def describe_post():
        def it_creates_group(
            client, user_verwaltung, user_gruppenleitung, location, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(user_gruppenleitung)
            db.session.add(location)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "group_name": "New Group",
                "group_number": 101,
                "user_id_group_leader": str(user_gruppenleitung.id),
                "location_id": str(location.id),
            }

            res = client.post("/api/groups", json=body)

            assert res.status_code == 201
            assert "id" in res.json

            all_groups = db.session.query(Group).all()
            assert len(all_groups) == 1
            assert all_groups[0].group_name == "New Group"
            assert all_groups[0].group_number == 101

        def it_returns_400_for_missing_fields(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.post("/api/groups", json={})

            assert res.status_code == 400

        def it_checks_for_taken_group_number(
            client, user_verwaltung, group, user_gruppenleitung, location, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(group)
            db.session.add(user_gruppenleitung)
            db.session.add(location)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "group_name": "Different Group",
                "group_number": group.group_number,
                "user_id_group_leader": str(user_gruppenleitung.id),
                "location_id": str(location.id),
            }

            res = client.post("/api/groups", json=body)

            assert res.status_code == 409
            assert "Gruppe" in res.json["title"]

        def it_checks_for_existing_location(
            client, user_verwaltung, user_gruppenleitung, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(user_gruppenleitung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "group_name": "New Group",
                "group_number": 101,
                "user_id_group_leader": str(user_gruppenleitung.id),
                "location_id": str(uuid.uuid4()),
            }

            res = client.post("/api/groups", json=body)

            assert res.status_code == 404
            assert "Standort" in res.json["title"]

        def it_blocks_unauthenticated_users(client):
            res = client.post("/api/groups", json={"group_name": "Test"})

            assert res.status_code == 401

        def it_blocks_non_authorized_users(client, user_gruppenleitung, db):
            db.session.add(user_gruppenleitung)
            db.session.commit()
            login(user=user_gruppenleitung, client=client)

            res = client.post("/api/groups", json={"group_name": "Test"})

            assert res.status_code == 403

    def describe_put():
        def it_updates_group(
            client, user_verwaltung, group, user_gruppenleitung, location, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(group)
            db.session.add(user_gruppenleitung)
            db.session.add(location)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "group_name": "Updated Group",
                "group_number": group.group_number,
                "user_id_group_leader": str(group.user_id_group_leader),
                "location_id": str(location.id),
            }

            res = client.put(f"/api/groups/{group.id}", json=body)

            assert res.status_code == 200
            db.session.refresh(group)
            assert group.group_name == "Updated Group"

        def it_returns_404_if_group_does_not_exist(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "group_name": "Updated Group",
                "group_number": 101,
                "user_id_group_leader": str(uuid.uuid4()),
                "location_id": str(uuid.uuid4()),
            }

            res = client.put(f"/api/groups/{uuid.uuid4()}", json=body)

            assert res.status_code == 404

        def it_blocks_non_authorized_users(client, user_gruppenleitung, group, db):
            db.session.add(user_gruppenleitung)
            db.session.add(group)
            db.session.commit()
            login(user=user_gruppenleitung, client=client)

            body = {
                "group_name": "Updated Group",
                "group_number": group.group_number,
                "user_id_group_leader": str(group.user_id_group_leader),
                "location_id": str(group.location_id),
            }

            res = client.put(f"/api/groups/{group.id}", json=body)

            assert res.status_code == 403

    def describe_delete():
        def it_deletes_group(client, user_verwaltung, group, db):
            db.session.add(user_verwaltung)
            db.session.add(group)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.delete(f"/api/groups/{group.id}")

            assert res.status_code == 200
            assert "erfolgreich gelöscht" in res.json["message"]

            remaining_groups = db.session.query(Group).all()
            assert len(remaining_groups) == 0

        def it_returns_404_if_group_does_not_exist(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.delete(f"/api/groups/{uuid.uuid4()}")

            assert res.status_code == 404

        def it_blocks_non_authorized_users(client, user_gruppenleitung, group, db):
            db.session.add(user_gruppenleitung)
            db.session.add(group)
            db.session.commit()
            login(user=user_gruppenleitung, client=client)

            res = client.delete(f"/api/groups/{group.id}")

            assert res.status_code == 403

    def describe_get_by_id():
        def it_returns_group_by_id(client, user_verwaltung, group, db):
            db.session.add(user_verwaltung)
            db.session.add(group)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get(f"/api/groups/{group.id}")

            assert res.status_code == 200
            assert res.json["id"] == str(group.id)
            assert res.json["group_name"] == group.group_name
            assert res.json["group_number"] == group.group_number

        def it_returns_404_if_group_does_not_exist(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get(f"/api/groups/{uuid.uuid4()}")

            assert res.status_code == 404

        def it_blocks_non_authorized_users(client, user_gruppenleitung, group, db):
            db.session.add(user_gruppenleitung)
            db.session.add(group)
            db.session.commit()
            login(user=user_gruppenleitung, client=client)

            res = client.get(f"/api/groups/{group.id}")

            assert res.status_code == 403

    def describe_get_all_groups():
        def it_returns_all_groups_for_verwaltung(client, user_verwaltung, group, db):
            db.session.add(user_verwaltung)
            db.session.add(group)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get("/api/groups")

            assert res.status_code == 200
            assert len(res.json) == 1
            assert res.json[0]["id"] == str(group.id)

        def it_returns_multiple_groups(client, user_verwaltung, group, other_group, db):
            db.session.add(user_verwaltung)
            db.session.add(group)
            db.session.add(other_group)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get("/api/groups")

            assert res.status_code == 200
            assert len(res.json) == 2

        def it_returns_only_relevant_groups_for_gruppenleitung(
            client, group, user_gruppenleitung, db
        ):
            # For group leader, should only get their own groups
            user_gruppenleitung.id = group.user_id_group_leader
            db.session.add(user_gruppenleitung)
            db.session.add(group)
            db.session.commit()
            login(user=user_gruppenleitung, client=client)

            res = client.get("/api/groups")

            assert res.status_code == 200
            assert len(res.json) == 1
            assert res.json[0]["id"] == str(group.id)

        def it_blocks_unauthenticated_users(client):
            res = client.get("/api/groups")

            assert res.status_code == 401

    def describe_get_with_locations():
        def it_returns_groups_with_locations_for_verwaltung(
            client, user_verwaltung, group, location, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.add(group)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get("/api/groups/with-locations")

            assert res.status_code == 200
            assert location.location_name in res.json
            assert group.group_name in res.json[location.location_name]

        def it_returns_only_relevant_groups_for_standortleitung(
            client, user_standortleitung, location, group, db
        ):
            # Make the standortleitung the leader of the location
            location.user_id_location_leader = user_standortleitung.id
            db.session.add(user_standortleitung)
            db.session.add(location)
            db.session.add(group)
            db.session.commit()
            login(user=user_standortleitung, client=client)

            res = client.get("/api/groups/with-locations")

            assert res.status_code == 200
            assert location.location_name in res.json
            assert group.group_name in res.json[location.location_name]

        def it_blocks_unauthenticated_users(client):
            res = client.get("/api/groups/with-locations")

            assert res.status_code == 401

    def describe_get_with_employees():
        def it_returns_groups_with_employees(
            client, user_verwaltung, group, employees, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(group)
            for employee in employees:
                db.session.add(employee)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get("/api/groups/with-employees")

            assert res.status_code == 200
            assert len(res.json) >= 1
            group_found = False
            for g in res.json:
                if g["id"] == str(group.id):
                    group_found = True
                    assert "employees" in g
                    assert len(g["employees"]) == 5
            assert group_found

        def it_blocks_non_authorized_users(client, user_gruppenleitung, db):
            db.session.add(user_gruppenleitung)
            db.session.commit()
            login(user=user_gruppenleitung, client=client)

            res = client.get("/api/groups/with-employees")

            assert res.status_code == 403

    def describe_remove_replacement():
        def it_removes_replacement_from_group(client, user_standortleitung, group, db):
            replacement_id = uuid.uuid4()
            group.user_id_replacement = replacement_id

            db.session.add(user_standortleitung)
            db.session.add(group)
            db.session.commit()
            login(user=user_standortleitung, client=client)

            res = client.delete(f"/api/groups/remove-replacement/{group.id}")

            assert res.status_code == 200

        def it_returns_404_if_group_does_not_exist(client, user_standortleitung, db):
            db.session.add(user_standortleitung)
            db.session.commit()
            login(user=user_standortleitung, client=client)

            res = client.delete(f"/api/groups/remove-replacement/{uuid.uuid4()}")

            assert res.status_code == 404
            assert "Gruppe nicht gefunden" in res.json["title"]

    def describe_create_qr():
        def it_returns_pdf_with_qr_codes(client, user_verwaltung, group, employees, db):
            db.session.add(user_verwaltung)
            db.session.add(group)
            for employee in employees:
                db.session.add(employee)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get(f"/api/groups/create-qr/{group.id}")

            # This should return a PDF file
            assert res.status_code == 200
            assert res.headers["Content-Type"] == "application/pdf"

        def it_returns_404_if_group_has_no_employees(
            client, user_verwaltung, group, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(group)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get(f"/api/groups/create-qr/{group.id}")

            assert res.status_code == 404

        def it_blocks_non_authorized_users(client, user_gruppenleitung, group, db):
            db.session.add(user_gruppenleitung)
            db.session.add(group)
            db.session.commit()
            login(user=user_gruppenleitung, client=client)

            res = client.get(f"/api/groups/create-qr/{group.id}")

            assert res.status_code == 403
