"""End-to-End tests for the auth routes."""

from sqlalchemy import select
from src.models.refresh_token_session import RefreshTokenSession
from src.models.user import User
from .helper import *  # for fixtures  # noqa: F403
from .helper import PASSWORD, join_headers


def describe_login():
    def describe_post():
        def it_returns_400_on_invalid_input(client):
            res = client.post("/api/login", json={})

            assert res.status_code == 400

        def it_returns_401_on_invalid_credentials(client, user, db):
            db.session.add(user)
            db.session.commit()

            res = client.post(
                "/api/login",
                json={"username": user.username, "password": "wrong_password"},
            )

            assert res.status_code == 401

        def it_returns_401_on_nonexistent_user(client, db):
            res = client.post(
                "/api/login",
                json={"username": "nonexistent_user", "password": PASSWORD},
            )

            assert res.status_code == 401

        def it_returns_401_on_hidden_user(client, user, db):
            user.hidden = True
            db.session.add(user)
            db.session.commit()

            res = client.post(
                "/api/login", json={"username": user.username, "password": PASSWORD}
            )

            assert res.status_code == 401

        def it_removes_token_cookies_on_invalid_credentials(client, user, db):
            db.session.add(user)
            db.session.commit()

            res = client.post(
                "/api/login",
                json={"username": user.username, "password": "wrong_password"},
            )

            headers_str = join_headers(res.headers)
            print(headers_str)

            assert res.status_code == 401
            assert res.headers.get("Set-Cookie")
            assert "auth_token=; Expires=Thu, 01 Jan 1970 00:00:00 GMT;" in headers_str
            assert (
                "refresh_token=; Expires=Thu, 01 Jan 1970 00:00:00 GMT;" in headers_str
            )

        def it_returns_403_on_blocked_user(client, user, db):
            user.blocked = True
            db.session.add(user)
            db.session.commit()

            res = client.post(
                "/api/login", json={"username": user.username, "password": PASSWORD}
            )

            assert res.json["title"] == "Account gesperrt"
            assert res.status_code == 403

        def it_returns_user_object_on_successful_login(user, client, db):
            db.session.add(user)
            db.session.commit()

            assert len(db.session.scalars(select(User)).all()) == 1

            res = client.post(
                "/api/login", json={"username": user.username, "password": PASSWORD}
            )

            assert res.status_code == 200
            assert res.json["id"] == str(user.id)
            assert res.json["username"] == user.username
            assert res.json["first_name"] == user.first_name
            assert res.json["last_name"] == user.last_name
            assert not res.json["blocked"]

        def it_sets_token_cookies_on_successful_login(user, client, db):
            db.session.add(user)
            db.session.commit()

            res = client.post(
                "/api/login", json={"username": user.username, "password": PASSWORD}
            )

            headers_str = join_headers(res.headers)
            print(headers_str)

            assert res.status_code == 200
            assert res.headers.get("Set-Cookie")
            assert "auth_token" in headers_str
            assert "refresh_token" in headers_str

        def it_saves_refresh_token_in_db(user, client, db):
            db.session.add(user)
            db.session.commit()

            # Ensure no refresh tokens are in the database
            assert len(db.session.scalars(select(RefreshTokenSession)).all()) == 0

            res = client.post(
                "/api/login", json={"username": user.username, "password": PASSWORD}
            )

            headers_str = join_headers(res.headers)
            print(headers_str)
            refresh_token = headers_str.split("refresh_token=")[1].split(";")[0]

            assert res.status_code == 200

            assert len(db.session.scalars(select(RefreshTokenSession)).all()) == 1
            assert (
                db.session.scalars(select(RefreshTokenSession)).first().refresh_token
                == refresh_token
            )


def describe_is_logged_in():
    def describe_get():
        def it_returns_401_on_unauthenticated_user(client):
            res = client.get("/api/is-logged-in")

            assert res.status_code == 401

        def it_returns_user_object_on_authenticated_user(user, client, db):
            db.session.add(user)
            db.session.commit()

            res = client.post(
                "/api/login", json={"username": user.username, "password": PASSWORD}
            )

            res = client.get("/api/is-logged-in")

            assert res.status_code == 200
            assert res.json["id"] == str(user.id)
            assert res.json["username"] == user.username
            assert res.json["first_name"] == user.first_name
            assert res.json["last_name"] == user.last_name
            assert not res.json["blocked"]


def describe_logout():
    def describe_post():
        def it_returns_401_on_unauthenticated_user(client):
            res = client.post("/api/logout")

            assert res.status_code == 204

        def it_removes_token_cookies_on_logout(user, client, db):
            db.session.add(user)
            db.session.commit()

            client.post(
                "/api/login", json={"username": user.username, "password": PASSWORD}
            )

            res = client.post("/api/logout")

            headers_str = join_headers(res.headers)
            print(headers_str)

            assert res.status_code == 204
            assert res.headers.get("Set-Cookie")
            assert "auth_token=; Expires=Thu, 01 Jan 1970 00:00:00 GMT;" in headers_str
            assert (
                "refresh_token=; Expires=Thu, 01 Jan 1970 00:00:00 GMT;" in headers_str
            )

        def it_removes_refresh_token_from_db(user, client, db):
            db.session.add(user)
            db.session.commit()

            client.post(
                "/api/login", json={"username": user.username, "password": PASSWORD}
            )

            assert len(db.session.scalars(select(RefreshTokenSession)).all()) == 1

            res = client.post("/api/logout")

            assert res.status_code == 204
            assert len(db.session.scalars(select(RefreshTokenSession)).all()) == 0


def describe_change_password():
    def describe_post():
        def it_returns_401_on_unauthenticated_user(client):
            res = client.post("/api/account/change-password")

            assert res.status_code == 401

        def it_returns_400_on_invalid_input(user, client, db):
            db.session.add(user)
            db.session.commit()

            client.post(
                "/api/login", json={"username": user.username, "password": PASSWORD}
            )

            res = client.post("/api/account/change-password", json={})

            assert res.status_code == 400

        def it_returns_400_on_invalid_credentials(user, client, db):
            db.session.add(user)
            db.session.commit()

            client.post(
                "/api/login", json={"username": user.username, "password": PASSWORD}
            )

            res = client.post(
                "/api/account/change-password",
                json={
                    "old_password": "wrong_password",
                    "new_password": PASSWORD,
                },
            )

            assert res.status_code == 401
            assert res.json["title"] == "Passwort ändern fehlgeschlagen"

        def it_returns_204_on_successful_change(user, client, db):
            db.session.add(user)
            db.session.commit()

            client.post(
                "/api/login", json={"username": user.username, "password": PASSWORD}
            )

            res = client.post(
                "/api/account/change-password",
                json={
                    "old_password": PASSWORD,
                    "new_password": "new_password",
                },
            )

            assert res.status_code == 204

        def it_changes_password_hash(user, client, db):
            db.session.add(user)
            db.session.commit()

            initial_password = user.hashed_password

            assert (
                db.session.scalars(select(User)).first().hashed_password
                == initial_password
            )

            client.post(
                "/api/login", json={"username": user.username, "password": PASSWORD}
            )

            res = client.post(
                "/api/account/change-password",
                json={
                    "old_password": PASSWORD,
                    "new_password": "super_compliCated_new_password",
                },
            )

            assert res.status_code == 204
            assert (
                db.session.scalars(select(User)).first().hashed_password
                != initial_password
            )

        def it_deletes_refresh_tokens(user, client, db):
            db.session.add(user)
            db.session.commit()

            client.post(
                "/api/login", json={"username": user.username, "password": PASSWORD}
            )
            client.post(
                "/api/login", json={"username": user.username, "password": PASSWORD}
            )
            client.post(
                "/api/login", json={"username": user.username, "password": PASSWORD}
            )

            assert len(db.session.scalars(select(RefreshTokenSession)).all()) == 3

            res = client.post(
                "/api/account/change-password",
                json={
                    "old_password": PASSWORD,
                    "new_password": "super_compliCated_new_password",
                },
            )

            assert res.status_code == 204
            assert len(db.session.scalars(select(RefreshTokenSession)).all()) == 0

        def it_removes_token_cookies_on_successful_change(user, client, db):
            db.session.add(user)
            db.session.commit()

            client.post(
                "/api/login", json={"username": user.username, "password": PASSWORD}
            )

            res = client.post(
                "/api/account/change-password",
                json={
                    "old_password": PASSWORD,
                    "new_password": "super_compliCated_new_password",
                },
            )

            headers_str = join_headers(res.headers)
            print(headers_str)

            assert res.status_code == 204
            assert res.headers.get("Set-Cookie")
            assert "auth_token=; Expires=Thu, 01 Jan 1970 00:00:00 GMT;" in headers_str
            assert (
                "refresh_token=; Expires=Thu, 01 Jan 1970 00:00:00 GMT;" in headers_str
            )
