"""End-to-End tests for the users routes."""

import uuid
from .helper import *  # for fixtures # noqa: F403
from .helper import login
from src.models.user import UserGroup, User


def describe_users():
    def describe_get():
        def it_returns_all_users_for_verwaltung(client, user_verwaltung, users, db):
            db.session.add(user_verwaltung)
            db.session.add_all(users)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get("/api/users")

            assert res.status_code == 200
            assert len(res.json) == 1 + len(users)

        def it_returns_filtered_users(
            client, user_verwaltung, user_standortleitung, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get("/api/users?user_group_filter=standortleitung")

            assert res.status_code == 200
            assert len(res.json) == 1
            assert res.json[0]["id"] == str(user_standortleitung.id)

        def it_blocks_unauthenticated_users(client):
            res = client.get("/api/users")

            assert res.status_code == 401

        def it_blocks_non_verwaltung_users(client, user_standortleitung, db):
            db.session.add(user_standortleitung)
            db.session.commit()
            login(user=user_standortleitung, client=client)

            res = client.get("/api/users")

            assert res.status_code == 403

        def it_does_not_send_hidden_users(
            client, user_verwaltung, user_standortleitung, db
        ):
            db.session.add(user_verwaltung)
            user_standortleitung.hidden = True
            db.session.add(user_standortleitung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get("/api/users")

            assert res.status_code == 200
            assert len(res.json) == 1

    def describe_get_by_id():
        def it_returns_user_by_id(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get(f"/api/users/{user_verwaltung.id}")

            assert res.status_code == 200
            assert res.json["id"] == str(user_verwaltung.id)

        def it_returns_404_if_user_does_not_exist(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get(f"/api/users/{uuid.uuid4()}")

            assert res.status_code == 404

        def it_does_not_return_hidden_user(
            client, user_verwaltung, user_standortleitung, db
        ):
            db.session.add(user_verwaltung)
            user_standortleitung.hidden = True
            db.session.add(user_standortleitung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get(f"/api/users/{user_standortleitung.id}")

            assert res.status_code == 404

    def describe_post():
        def it_returns_400_for_missing_fields(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.post("/api/users", json={})

            assert res.status_code == 400

        def it_creates_user(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "first_name": "Max",
                "last_name": "Mustermann",
                "username": "max.mustermann",
                "user_group": "standortleitung",
            }

            res = client.post("/api/users", json=body)

            assert res.status_code == 201

            all_users = db.session.query(User).all()

            assert len(all_users) == 2

        def it_checks_for_taken_user_name(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "first_name": "Max",
                "last_name": "Mustermann",
                "username": user_verwaltung.username,
                "user_group": "standortleitung",
            }

            res = client.post("/api/users", json=body)

            assert res.status_code == 409
            assert res.json["title"] == "Nutzername bereits vergeben"

        def it_checks_hidden_user_names(
            client, user_verwaltung, user_standortleitung, db
        ):
            db.session.add(user_verwaltung)
            user_standortleitung.hidden = True
            db.session.add(user_standortleitung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "first_name": "Max",
                "last_name": "Mustermann",
                "username": user_standortleitung.username,
                "user_group": "standortleitung",
            }

            res = client.post("/api/users", json=body)

            assert res.status_code == 409
            assert res.json["title"] == "Nutzername bereits vergeben"

        def it_returns_random_password_and_id(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "first_name": "Max",
                "last_name": "Mustermann",
                "username": "max.mustermann",
                "user_group": "standortleitung",
            }

            res = client.post("/api/users", json=body)

            assert res.status_code == 201
            assert "initial_password" in res.json
            assert "id" in res.json

        def it_takes_location_for_user(client, user_verwaltung, db, location):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "first_name": "Max",
                "last_name": "Mustermann",
                "username": "max.mustermann",
                "user_group": "standortleitung",
                "location_id": location.id,
            }

            res = client.post("/api/users", json=body)

            assert res.status_code == 201

            user = db.session.query(User).filter_by(username="max.mustermann").first()
            assert user.location_id == location.id

        def it_checks_if_location_exists(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "first_name": "Max",
                "last_name": "Mustermann",
                "username": "max.mustermann",
                "user_group": "standortleitung",
                "location_id": uuid.uuid4(),
            }

            res = client.post("/api/users", json=body)

            assert res.status_code == 404
            assert res.json["title"] == "Standort nicht gefunden"

    def describe_put_reset_password():
        def it_returns_404_for_unknown_user(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.put(f"/api/users/{uuid.uuid4()}/reset-password")

            assert res.status_code == 404

        def it_resets_password(client, user_verwaltung, user_standortleitung, db):
            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            initial_hash = user_standortleitung.hashed_password
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.put(f"/api/users/{user_standortleitung.id}/reset-password")

            assert res.status_code == 200
            assert "new_password" in res.json
            assert user_standortleitung.hashed_password != initial_hash

        def it_only_allows_verwaltung_to_reset_password(
            client, user_standortleitung, user_kuechenpersonal, user_gruppenleitung, db
        ):
            for user in [
                user_kuechenpersonal,
                user_gruppenleitung,
                user_standortleitung,
            ]:
                db.session.add(user)
                db.session.commit()
                login(user=user, client=client)

                res = client.put(f"/api/users/{user.id}/reset-password")

                assert res.status_code == 403

    def describe_put():
        def it_returns_404_for_unknown_user(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "first_name": "Harry",
                "last_name": "Potter",
                "username": "harry.potter",
                "user_group": "gruppenleitung",
            }

            res = client.put(f"/api/users/{uuid.uuid4()}", json=body)

            assert res.status_code == 404

        def it_updates_user(client, user_verwaltung, user_standortleitung, db):
            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "first_name": "Harry",
                "last_name": "Potter",
                "username": "harry.potter",
                "user_group": "gruppenleitung",
            }

            res = client.put(f"/api/users/{user_standortleitung.id}", json=body)

            assert res.status_code == 200
            assert user_standortleitung.first_name == "Harry"
            assert user_standortleitung.last_name == "Potter"
            assert user_standortleitung.username == "harry.potter"
            assert user_standortleitung.user_group == UserGroup.gruppenleitung

        def it_permits_not_updating_the_username(
            client, user_verwaltung, user_standortleitung, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "username": user_standortleitung.username,
                "first_name": "Harry",
                "last_name": "Potter",
                "user_group": "gruppenleitung",
            }

            res = client.put(f"/api/users/{user_standortleitung.id}", json=body)

            assert res.status_code == 200
            assert user_standortleitung.first_name == "Harry"
            assert user_standortleitung.last_name == "Potter"
            assert user_standortleitung.username == user_standortleitung.username
            assert user_standortleitung.user_group == UserGroup.gruppenleitung

        def it_checks_for_taken_user_name(
            client, user_verwaltung, user_standortleitung, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "first_name": "Harry",
                "last_name": "Potter",
                "username": user_verwaltung.username,
                "user_group": "gruppenleitung",
            }

            res = client.put(f"/api/users/{user_standortleitung.id}", json=body)

            assert res.status_code == 409
            assert res.json["title"] == "Nutzer:in-Name bereits vergeben"

        def it_takes_location(
            client, user_verwaltung, user_standortleitung, db, location
        ):
            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.add(location)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            assert user_standortleitung.location_id is None

            body = {
                "first_name": "Harry",
                "last_name": "Potter",
                "username": "harry.potter",
                "user_group": "gruppenleitung",
                "location_id": location.id,
            }

            res = client.put(f"/api/users/{user_standortleitung.id}", json=body)

            assert res.status_code == 200
            assert user_standortleitung.location_id == location.id

        def it_checks_if_location_exists(
            client, user_verwaltung, user_standortleitung, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            assert user_standortleitung.location_id is None

            body = {
                "first_name": "Harry",
                "last_name": "Potter",
                "username": "harry.potter",
                "user_group": "gruppenleitung",
                "location_id": uuid.uuid4(),
            }

            res = client.put(f"/api/users/{user_standortleitung.id}", json=body)

            assert res.status_code == 404
            assert res.json["title"] == "Standort nicht gefunden"

    def describe_delete():
        def it_returns_404_for_unknown_user(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.delete(f"/api/users/{uuid.uuid4()}")

            assert res.status_code == 404

        def it_deletes_user(client, user_verwaltung, user_standortleitung, db):
            db.session.add(user_verwaltung)
            db.session.add(user_standortleitung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            user_id = user_standortleitung.id

            res = client.delete(f"/api/users/{user_id}")

            assert res.status_code == 200
            assert user_standortleitung.hidden


def describe_group_leaders():
    def describe_get():
        def it_returns_all_group_leaders_for_verwaltung(
            client, user_verwaltung, users, db
        ):
            db.session.add(user_verwaltung)
            for user in users:
                user.user_group = UserGroup.gruppenleitung
            db.session.add_all(users)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get("/api/users/group-leaders")

            assert res.status_code == 200
            assert len(res.json) == len(users)

        def it_returns_users_from_location_for_standortleitung(
            client, user_standortleitung, db, users
        ):
            user_standortleitung.location_id = uuid.uuid4()
            db.session.add(user_standortleitung)
            for idx, user in enumerate(users):
                user.user_group = UserGroup.gruppenleitung
                if idx <= 2:
                    user.location_id = user_standortleitung.location
                else:
                    user.location_id = uuid.uuid4()  # different location
            db.session.add_all(users)
            db.session.commit()
            login(user=user_standortleitung, client=client)

            res = client.get("/api/users/group-leaders")

            assert res.status_code == 200
            assert len(res.json) == 3  # because only 3 users are in the same location

        def it_returns_users_without_location_for_standortleitung(
            client, user_standortleitung, db, users
        ):
            user_standortleitung.location_id = uuid.uuid4()
            db.session.add(user_standortleitung)
            for idx, user in enumerate(users):
                user.user_group = UserGroup.gruppenleitung
                if idx <= 2:
                    user.location_id = None
                else:
                    user.location_id = uuid.uuid4()
            db.session.add_all(users)
            db.session.commit()
            login(user=user_standortleitung, client=client)

            res = client.get("/api/users/group-leaders")

            assert res.status_code == 200
            assert len(res.json) == 3  # because only 3 users have no location

    def describe_location_leaders():
        def describe_get():
            def it_returns_all_location_leaders_for_verwaltung(
                client, user_verwaltung, users, db
            ):
                db.session.add(user_verwaltung)
                # insert 3 location leaders and other users
                for idx, user in enumerate(users):
                    user.user_group = (
                        UserGroup.standortleitung if idx <= 2 else UserGroup.verwaltung
                    )
                db.session.add_all(users)
                db.session.commit()
                login(user=user_verwaltung, client=client)

                res = client.get("/api/users/location-leaders")

                assert res.status_code == 200
                assert len(res.json) == 3  # because only 3 users are location leaders

            def it_blocks_non_verwaltung_users(client, user_standortleitung, db):
                db.session.add(user_standortleitung)
                db.session.commit()
                login(user=user_standortleitung, client=client)

                res = client.get("/api/users/location-leaders")

                assert res.status_code == 403


def describe_block_user():
    def it_blocks_user(client, user_verwaltung, user_standortleitung, db):
        db.session.add(user_verwaltung)
        db.session.add(user_standortleitung)
        db.session.commit()
        login(user=user_verwaltung, client=client)

        assert not user_standortleitung.blocked

        res = client.put(f"/api/users/{user_standortleitung.id}/block")

        assert res.status_code == 200
        assert user_standortleitung.blocked

    def it_denies_non_verwaltung(
        client,
        user_standortleitung,
        user_gruppenleitung,
        user_kuechenpersonal,
        user_verwaltung,
        db,
    ):
        for user in [user_standortleitung, user_gruppenleitung, user_kuechenpersonal]:
            db.session.add(user)
            db.session.commit()
            login(user=user, client=client)

            res = client.put(f"/api/users/{user_verwaltung.id}/block")

            assert res.status_code == 403


def describe_unblock_user():
    def it_unblocks_user(client, user_verwaltung, user_standortleitung, db):
        db.session.add(user_verwaltung)
        user_standortleitung.blocked = True
        db.session.add(user_standortleitung)
        db.session.commit()
        login(user=user_verwaltung, client=client)

        assert user_standortleitung.blocked

        res = client.put(f"/api/users/{user_standortleitung.id}/unblock")

        assert res.status_code == 200
        assert not user_standortleitung.blocked

    def it_denies_non_verwaltung(
        client,
        user_standortleitung,
        user_gruppenleitung,
        user_kuechenpersonal,
        user_verwaltung,
        db,
    ):
        db.session.add(user_standortleitung)
        db.session.add(user_gruppenleitung)
        db.session.add(user_kuechenpersonal)
        db.session.commit()

        for user in [
            user_standortleitung,
            user_gruppenleitung,
            user_kuechenpersonal,
        ]:
            db.session.add(user)
            db.session.commit()
            login(user=user, client=client)

            res = client.put(f"/api/users/{user_verwaltung.id}/unblock")

            assert res.status_code == 403
