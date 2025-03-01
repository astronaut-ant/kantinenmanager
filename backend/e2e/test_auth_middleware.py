"""End-to-end tests for the auth middleware."""

from datetime import datetime
from flask import g
from sqlalchemy import select
from src.constants import AUTHENTICATION_TOKEN_COOKIE_NAME, REFRESH_TOKEN_COOKIE_NAME
from src.models.refresh_token_session import RefreshTokenSession
from .helper import *  # for fixtures  # noqa: F403
from .helper import PASSWORD, get_refresh_token, get_auth_token, join_headers


def describe_auth_middleware():
    def it_handles_valid_auth_token(app, client, user, db):
        db.session.add(user)
        db.session.commit()

        login_res = client.post(
            "/api/login",
            json={"username": user.username, "password": PASSWORD},
        )

        auth_token = get_auth_token(login_res.headers)
        refresh_token = get_refresh_token(login_res.headers)

        assert login_res.status_code == 200
        assert len(auth_token) > 0
        assert len(refresh_token) > 0

        # Fire a request agains a random route without restrictions
        with app.test_request_context(
            "/api/health",
            method="GET",
            headers={
                "Cookie": f"{AUTHENTICATION_TOKEN_COOKIE_NAME}={auth_token}; {REFRESH_TOKEN_COOKIE_NAME}={refresh_token}"
            },
        ):
            app.preprocess_request()
            assert g.user_authenticated
            assert g.user_id == user.id
            assert g.user_username == user.username
            assert g.user_group.value == user.user_group.value
            assert g.user_first_name == user.first_name
            assert g.user_last_name == user.last_name

    def it_should_not_return_new_tokens_if_auth_token_is_valid(app, client, user, db):
        db.session.add(user)
        db.session.commit()

        login_res = client.post(
            "/api/login",
            json={"username": user.username, "password": PASSWORD},
        )

        assert login_res.status_code == 200

        res = client.get("/api/health")

        headers_str = join_headers(res.headers)
        assert res.status_code == 200
        assert "auth_token" not in headers_str
        assert "refresh_token" not in headers_str

    def it_generates_new_tokens_if_auth_token_is_invalid_but_refresh_token_is_valid(
        app, client, user, db
    ):
        db.session.add(user)
        db.session.commit()

        login_res = client.post(
            "/api/login",
            json={"username": user.username, "password": PASSWORD},
        )

        refresh_token = get_refresh_token(login_res.headers)

        assert login_res.status_code == 200
        assert len(refresh_token) > 0
        assert db.session.query(RefreshTokenSession).count() == 1

        with app.test_request_context(
            "/api/health",
            method="GET",
            headers={
                "Cookie": f"{AUTHENTICATION_TOKEN_COOKIE_NAME}=invalid; {REFRESH_TOKEN_COOKIE_NAME}={refresh_token}"
            },
        ):
            app.preprocess_request()
            assert g.user_authenticated
            assert db.session.query(RefreshTokenSession).count() == 2

            old_refresh_token = db.session.scalars(
                select(RefreshTokenSession).where(
                    RefreshTokenSession.refresh_token == refresh_token
                )
            ).first()
            assert old_refresh_token is not None
            assert old_refresh_token.last_used is not None
            assert old_refresh_token.has_been_used()

    def it_returns_new_tokens_if_auth_token_is_invalid_and_refresh_token_is_valid(
        app, client, user, db
    ):
        db.session.add(user)
        db.session.commit()

        login_res = client.post(
            "/api/login",
            json={"username": user.username, "password": PASSWORD},
        )

        assert login_res.status_code == 200

        client.delete_cookie(AUTHENTICATION_TOKEN_COOKIE_NAME)

        res = client.get(
            "/api/is-logged-in",
        )

        headers_str = join_headers(res.headers)
        print(headers_str)

        assert res.status_code == 200
        assert "auth_token" in headers_str
        assert "refresh_token" in headers_str

    def it_handles_unauthenticated_user(app):
        # Fire a request agains a random route without restrictions
        with app.test_request_context(
            "/api/health",
            method="GET",
        ):
            app.preprocess_request()
            assert not g.user_authenticated
            assert g.user_id is None
            assert g.user_username is None
            assert g.user_group is None
            assert g.user_first_name is None
            assert g.user_last_name is None

    def it_handles_wrong_refresh_token(app, client, db):
        with app.test_request_context(
            "/api/health",
            method="GET",
            headers={
                "Cookie": f"{AUTHENTICATION_TOKEN_COOKIE_NAME}=invalid; {REFRESH_TOKEN_COOKIE_NAME}=invalid"
            },
        ):
            app.preprocess_request()
            assert not g.user_authenticated
            assert g.user_id is None
            assert g.user_username is None
            assert g.user_group is None
            assert g.user_first_name is None
            assert g.user_last_name is None

    def it_handles_expired_refresh_token(app, client, user, db):
        db.session.add(user)
        db.session.commit()

        login_res = client.post(
            "/api/login",
            json={"username": user.username, "password": PASSWORD},
        )

        refresh_token = get_refresh_token(login_res.headers)

        assert login_res.status_code == 200
        assert len(refresh_token) > 0

        db.session.query(RefreshTokenSession).update(
            {RefreshTokenSession.expires: datetime(2020, 1, 1)}
        )
        db.session.commit()

        with app.test_request_context(
            "/api/health",
            method="GET",
            headers={
                "Cookie": f"{AUTHENTICATION_TOKEN_COOKIE_NAME}=invalid; {REFRESH_TOKEN_COOKIE_NAME}={refresh_token}"
            },
        ):
            app.preprocess_request()
            assert not g.user_authenticated
            assert g.user_id is None
            assert g.user_username is None
            assert g.user_group is None
            assert g.user_first_name is None
            assert g.user_last_name is None

    def it_blocks_user_when_refresh_token_has_already_been_used(app, client, user, db):
        db.session.add(user)
        db.session.commit()

        login_res = client.post(
            "/api/login",
            json={"username": user.username, "password": PASSWORD},
        )

        refresh_token = get_refresh_token(login_res.headers)

        assert login_res.status_code == 200
        assert len(refresh_token) > 0

        client.delete_cookie(AUTHENTICATION_TOKEN_COOKIE_NAME)

        # This will use the refresh token for the first time
        res = client.get("/api/is-logged-in")

        assert res.status_code == 200

        client.delete_cookie(AUTHENTICATION_TOKEN_COOKIE_NAME)
        client.set_cookie(REFRESH_TOKEN_COOKIE_NAME, refresh_token)

        # This will use the same refresh token for the second time
        res = client.get("/api/is-logged-in")

        assert res.status_code == 403
        assert res.json["title"] == "Account gesperrt"

    def it_handles_blocked_user(app, client, user, db):
        db.session.add(user)
        db.session.commit()

        login_res = client.post(
            "/api/login",
            json={"username": user.username, "password": PASSWORD},
        )

        assert login_res.status_code == 200

        user.blocked = True
        db.session.commit()

        # User blocked is only checked, when the auth token is invalid
        # and we try to use the refresh token
        client.delete_cookie(AUTHENTICATION_TOKEN_COOKIE_NAME)

        res = client.get("/api/health")

        assert res.status_code == 403
        assert res.json["title"] == "Account gesperrt"

    def it_does_not_return_new_tokens_on_logout(app, client, user, db):
        db.session.add(user)
        db.session.commit()

        login_res = client.post(
            "/api/login",
            json={"username": user.username, "password": PASSWORD},
        )

        assert login_res.status_code == 200

        client.delete_cookie(AUTHENTICATION_TOKEN_COOKIE_NAME)

        res = client.post("/api/logout")

        assert res.status_code == 204

        headers_str = join_headers(res.headers)
        assert "auth_token=; Expires=Thu, 01 Jan 1970 00:00:00 GMT;" in headers_str
        assert "refresh_token=; Expires=Thu, 01 Jan 1970 00:00:00 GMT;" in headers_str
