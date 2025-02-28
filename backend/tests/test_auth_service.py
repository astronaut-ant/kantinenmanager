"""Tests for the AuthService class"""

import base64
from datetime import datetime, timedelta
from math import floor
import uuid

import jwt
import pytest
from argon2 import PasswordHasher

from src import app as project_app
from src.constants import AUTHENTICATION_TOKEN_AUDIENCE
from src.models.refresh_token_session import RefreshTokenSession
from src.models.user import User, UserGroup
from src.repositories.refresh_token_session_repository import (
    RefreshTokenSessionRepository,
)
from src.repositories.users_repository import UsersRepository
from src.services.auth_service import AuthService
from src.utils.exceptions import (
    InvalidCredentialsException,
    NotFoundError,
    UnauthenticatedException,
    UserBlockedError,
)

# * Fixtures bieten eine Möglichkeit, Code zu schreiben, der von mehreren Tests verwendet wird.
# * Die unteren Fixtures erzeugen ein Objekt, das automatisch an die Tests übergeben wird,
# * wenn sie als Argument in der Testfunktion definiert sind.

PASSWORD = "password"
JWT_SECRET = "super_secret"


@pytest.fixture()
def app():
    project_app.config["JWT_SECRET"] = JWT_SECRET
    project_app.config["TESTING"] = True
    yield project_app


@pytest.fixture()
def user():
    user = User(
        first_name="Jane",
        last_name="Doe",
        username="janedoe",
        hashed_password="$argon2id$v=19$m=65536,t=3,p=4$3rfCHeNLgFGKSyeZU0tl5w$rpsECi3FkYbvf2DEyPrDwp5/lPD3RUecZARuaRSVrWQ",  # password: password
        user_group=UserGroup.verwaltung,
    )
    user.id = uuid.uuid4()
    return user


@pytest.fixture()
def session(user):
    return RefreshTokenSession(
        refresh_token="token",
        user_id=user.id,
        expires=datetime.now() + timedelta(days=1),
    )


def describe_login():
    # * Darin werden die Testfälle definiert. Jede Funktion ist ein eigener Testfall.
    # * Tests folgen generell dem Schema: Arrange, Act, Assert, (Cleanup).
    # * Arrange: Vorbereitung der Testumgebung
    # * Act: Ausführung des zu testenden Codes
    # * Assert: Überprüfung des erwarteten Ergebnisses
    # * https://docs.pytest.org/en/stable/explanation/anatomy.html

    def it_throws_error_on_non_exising_username(mocker):
        mocker.patch.object(UsersRepository, "get_user_by_username", return_value=None)

        with pytest.raises(NotFoundError):
            AuthService.login("johndoe", "password")

    def it_throws_error_on_invalid_password(mocker, user):
        mocker.patch.object(UsersRepository, "get_user_by_username", return_value=user)

        with pytest.raises(InvalidCredentialsException):
            AuthService.login(user.username, "wrong_password")

    def it_rehashes_password_if_needed(mocker, user, app):
        def update_user_side_effect(user):
            # Check that UsersRepository.update_user was called with the updated hash
            assert user.hashed_password == "new_hashed_password"

        with app.app_context():
            mocker.patch.object(
                UsersRepository, "get_user_by_username", return_value=user
            )
            mocker.patch.object(
                AuthService, "_AuthService__needs_rehash", return_value=True
            )
            mock_hash_password = mocker.patch.object(
                AuthService, "hash_password", return_value="new_hashed_password"
            )
            mock_update_user = mocker.patch.object(
                UsersRepository, "update_user", side_effect=update_user_side_effect
            )  # side_effets werden ausgeführt, wenn der Mock aufgerufen wird
            mocker.patch.object(
                AuthService, "_AuthService__make_refresh_token", return_value="token"
            )

            AuthService.login(user.username, PASSWORD)

            mock_hash_password.assert_called_once()
            mock_update_user.assert_called_once()

    def it_updates_last_login(app, user, mocker):
        with app.app_context():
            # fmt: off
            mocker.patch.object(UsersRepository, "get_user_by_username", return_value=user)
            mocker.patch.object(AuthService, "_AuthService__needs_rehash", return_value=False)
            mocker.patch.object(AuthService, "_AuthService__make_refresh_token", return_value="token")
            mock_update_user = mocker.patch.object(UsersRepository, "update_user")
            # fmt: on

            AuthService.login(user.username, PASSWORD)

            assert user.last_login is not None
            mock_update_user.assert_called_once()

    def it_throws_error_if_user_blocked(app, user, mocker):
        with app.app_context():
            # fmt: off
            user.blocked = True
            mocker.patch.object(UsersRepository, "get_user_by_username", return_value=user)
            mocker.patch.object(AuthService, "_AuthService__needs_rehash", return_value=False)
            mocker.patch.object(UsersRepository, "update_user")
            # fmt: on

            with pytest.raises(UserBlockedError):
                AuthService.login(user.username, PASSWORD)

    def it_throws_error_if_jwt_secret_not_set(app, user, mocker):
        with app.app_context():
            # fmt: off
            mocker.patch.object(UsersRepository, "get_user_by_username", return_value=user)
            mocker.patch.object(AuthService, "_AuthService__needs_rehash", return_value=False)
            mocker.patch.object(UsersRepository, "update_user")
            app.config["JWT_SECRET"] = None
            # fmt: on

            with pytest.raises(ValueError):
                AuthService.login(user.username, PASSWORD)

    def it_returns_user_for_valid_login(app, user, mocker):
        with app.app_context():
            # fmt: off
            mocker.patch.object(UsersRepository, "get_user_by_username", return_value=user)
            mocker.patch.object(AuthService, "_AuthService__needs_rehash", return_value=False)
            mocker.patch.object(UsersRepository, "update_user")
            mocker.patch.object(AuthService, "_AuthService__make_refresh_token", return_value="token")
            # fmt: on

            user, _, _ = AuthService.login(user.username, PASSWORD)

            assert user == user

    def it_returns_tokens_for_valid_login(app, user, mocker):
        with app.app_context():
            # fmt: off
            mocker.patch.object(UsersRepository, "get_user_by_username", return_value=user)
            mocker.patch.object(AuthService, "_AuthService__needs_rehash", return_value=False)
            mocker.patch.object(UsersRepository, "update_user")
            mocker.patch.object(AuthService, "_AuthService__make_auth_token", return_value="auth_token")
            mocker.patch.object(AuthService, "_AuthService__make_refresh_token", return_value="refresh_token")
            # fmt: on

            _, auth_token, refresh_token = AuthService.login(user.username, PASSWORD)

            assert auth_token == "auth_token"
            assert refresh_token == "refresh_token"


def describe_authenticate():
    def it_raises_error_on_missing_jwt_secret(app, mocker):
        with app.app_context():
            app.config["JWT_SECRET"] = None

            with pytest.raises(ValueError):
                AuthService.authenticate("auth_token", "refresh_token")

    def it_accepts_valid_auth_token(app, user, mocker):
        with app.app_context():
            auth_token = AuthService._AuthService__make_auth_token(user, JWT_SECRET)

            user_info, new_auth_token, new_refresh_token = AuthService.authenticate(
                auth_token, None
            )

            assert str(user_info["id"]) == str(user.id)
            assert user_info["username"] == user.username
            assert user_info["group"].value == user.user_group.value
            assert user_info["first_name"] == user.first_name
            assert user_info["last_name"] == user.last_name
            assert new_auth_token is None
            assert new_refresh_token is None

    def it_throws_error_on_invalid_auth_token_and_no_refresh_token(app):
        with app.app_context():
            with pytest.raises(UnauthenticatedException):
                AuthService.authenticate("invalid_auth_token", None)

    def it_throws_error_on_both_tokens_none(app):
        with app.app_context():
            with pytest.raises(UnauthenticatedException):
                AuthService.authenticate(None, None)

    def it_requests_refresh_token_on_invalid_auth_token(app, mocker):
        with app.app_context():
            mock_get_token = mocker.patch.object(
                RefreshTokenSessionRepository, "get_token", return_value=None
            )

            with pytest.raises(UnauthenticatedException):
                AuthService.authenticate("invalid_auth_token", "invalid_refresh_token")
                mock_get_token.assert_called_once_with("invalid_refresh_token")

    def it_throws_error_on_expired_refresh_token(app, mocker, session):
        with app.app_context():
            session.expires = datetime.now() - timedelta(days=1)
            mocker.patch.object(
                RefreshTokenSessionRepository, "get_token", return_value=session
            )

            try:
                AuthService.authenticate("invalid_auth_token", session.refresh_token)
                assert False  # Should throw an exception
            except UnauthenticatedException as e:
                assert "Refresh token expired" in str(
                    e
                )  # Should throw the right exception

    def it_throws_error_when_refresh_token_has_been_used(app, mocker, session, user):
        with app.app_context():
            session.last_used = datetime.now() - timedelta(days=1)
            mocker.patch.object(
                RefreshTokenSessionRepository, "get_token", return_value=session
            )
            mocker.patch.object(UsersRepository, "get_user_by_id", return_value=user)
            mocker.patch.object(UsersRepository, "update_user")

            try:
                AuthService.authenticate("invalid_auth_token", session.refresh_token)
                assert False  # Should throw an exception
            except UserBlockedError as e:
                assert "Refresh Token wurde bereits verwendet." in str(e)

    def it_blocks_user_when_refresh_token_already_used(app, mocker, session, user):
        with app.app_context():
            session.last_used = datetime.now() - timedelta(days=1)
            mocker.patch.object(
                RefreshTokenSessionRepository, "get_token", return_value=session
            )
            mocker.patch.object(UsersRepository, "get_user_by_id", return_value=user)
            mock_update_user = mocker.patch.object(UsersRepository, "update_user")

            try:
                AuthService.authenticate("invalid_auth_token", session.refresh_token)
                assert False  # Should throw an exception
            except UserBlockedError:
                pass

            assert user.blocked
            mock_update_user.assert_called_once()

    def it_throws_when_user_not_found(app, mocker, session):
        with app.app_context():
            mocker.patch.object(
                RefreshTokenSessionRepository, "get_token", return_value=session
            )
            mocker.patch.object(UsersRepository, "get_user_by_id", return_value=None)

            try:
                AuthService.authenticate("invalid_auth_token", session.refresh_token)
                assert False  # Should throw an exception
            except UnauthenticatedException as e:
                assert "Nutzer nicht gefunden." in str(e)

    def it_throws_when_user_is_blocked(app, mocker, session, user):
        with app.app_context():
            user.blocked = True
            mocker.patch.object(
                RefreshTokenSessionRepository, "get_token", return_value=session
            )
            mocker.patch.object(UsersRepository, "get_user_by_id", return_value=user)

            with pytest.raises(UserBlockedError):
                AuthService.authenticate("invalid_auth_token", session.refresh_token)

    def it_generates_new_tokens_on_success(app, mocker, session, user):
        with app.app_context():
            mocker.patch.object(
                RefreshTokenSessionRepository, "get_token", return_value=session
            )
            mocker.patch.object(UsersRepository, "get_user_by_id", return_value=user)
            mock_make_auth_token = mocker.patch.object(
                AuthService,
                "_AuthService__make_auth_token",
                return_value="new_auth_token",
            )
            mock_make_refresh_token = mocker.patch.object(
                AuthService,
                "_AuthService__make_refresh_token",
                return_value="new_refresh_token",
            )
            mocker.patch.object(RefreshTokenSessionRepository, "update_token")

            user_info, new_auth_token, new_refresh_token = AuthService.authenticate(
                "invalid_auth_token", session.refresh_token
            )

            assert str(user_info["id"]) == str(user.id)
            assert user_info["username"] == user.username
            assert user_info["group"].value == user.user_group.value
            assert user_info["first_name"] == user.first_name
            assert user_info["last_name"] == user.last_name
            assert new_auth_token == "new_auth_token"
            assert new_refresh_token == "new_refresh_token"
            assert session.last_used is not None
            mock_make_auth_token.assert_called_once()
            mock_make_refresh_token.assert_called_once()


def describe_logout():
    def it_deletes_refresh_token(app, mocker, session):
        with app.app_context():
            mocker.patch.object(
                RefreshTokenSessionRepository, "get_token", return_value=session
            )
            mock_delete_user_tokens = mocker.patch.object(
                RefreshTokenSessionRepository, "delete_token"
            )

            AuthService.logout("token")

            mock_delete_user_tokens.assert_called_once_with(session)


def describe_change_password():
    def it_throws_error_on_non_existing_user(app, mocker):
        with app.app_context():
            mocker.patch.object(UsersRepository, "get_user_by_id", return_value=None)

            with pytest.raises(NotFoundError):
                AuthService.change_password(uuid.uuid4(), "password", "new_password")

    def it_throws_error_on_invalid_current_password(app, mocker, user):
        with app.app_context():
            mocker.patch.object(UsersRepository, "get_user_by_id", return_value=user)

            with pytest.raises(InvalidCredentialsException):
                AuthService.change_password(user.id, "wrong_password", "new_password")

    def it_updates_password(app, mocker, user):
        def update_user_side_effect(user):
            assert user.hashed_password == "new_hashed_password"

        with app.app_context():
            mocker.patch.object(UsersRepository, "get_user_by_id", return_value=user)
            mocker.patch.object(
                AuthService, "hash_password", return_value="new_hashed_password"
            )
            mocker.patch.object(
                UsersRepository, "update_user", side_effect=update_user_side_effect
            )

            AuthService.change_password(user.id, PASSWORD, "new_password")

    def it_invalidates_all_refresh_tokens_on_password_change(app, mocker, user):
        with app.app_context():
            mocker.patch.object(UsersRepository, "get_user_by_id", return_value=user)
            mocker.patch.object(UsersRepository, "update_user")
            mock_invalidate_all_refresh_tokens = mocker.patch.object(
                AuthService, "invalidate_all_refresh_tokens"
            )

            AuthService.change_password(user.id, PASSWORD, "new_password")

            mock_invalidate_all_refresh_tokens.assert_called_once_with(user.id)


def describe_invalidate_all_refresh_tokens():
    def it_invalidates_all_tokens(mocker, user):
        mock_delete_user_tokens = mocker.patch.object(
            RefreshTokenSessionRepository, "delete_user_tokens"
        )

        AuthService.invalidate_all_refresh_tokens(user.id)

        mock_delete_user_tokens.assert_called_once_with(user.id)


def describe_generate_password():
    def it_generates_a_password():
        password = AuthService.generate_password()

        assert password
        assert len(password) >= 8


def describe_hash_password():
    def it_hashes_a_password():
        password = "password"
        hashed_password = AuthService.hash_password(password)

        assert hashed_password
        assert password != hashed_password


def describe_check_password():
    def it_checks_matching_password():
        password = "password"
        hashed_password = AuthService.hash_password(password)

        # check_password is a private method, so Python mangles the name to _AuthService__check_password
        assert AuthService._AuthService__check_password(password, hashed_password)

    def it_checks_non_matching_password():
        password = "password"
        hashed_password = AuthService.hash_password(password)

        assert not AuthService._AuthService__check_password(
            "wrong_password", hashed_password
        )

    def it_checks_empty_password():
        password = ""
        hashed_password = AuthService.hash_password(password)

        assert AuthService._AuthService__check_password(password, hashed_password)

    def it_checks_empty_hashed_password():
        password = "password"
        hashed_password = ""

        assert not AuthService._AuthService__check_password(password, hashed_password)


def describe__needs_rehash():
    def it_returns_true_for_old_hash():
        # Rehashing is needed when the hashing parameters change
        ph = PasswordHasher(hash_len=9)  # Different settings than the default
        password = "password"
        hashed_password = ph.hash(password)

        assert AuthService._AuthService__needs_rehash(hashed_password)

    def it_returns_false_for_new_hash():
        password = "password"
        hashed_password = AuthService.hash_password(password)

        assert not AuthService._AuthService__needs_rehash(hashed_password)


def describe_make_auth_token():
    def it_generates_a_token(user, app):
        with app.app_context():
            token = AuthService._AuthService__make_auth_token(user, JWT_SECRET)

            assert token
            assert len(token) > 0
            assert (
                len(token.split(".")) == 3
            )  # JWT token consists of 3 parts separated by a dot

    def it_contains_correct_payload(user, app):
        with app.app_context():
            token = AuthService._AuthService__make_auth_token(user, JWT_SECRET)
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=["HS256"],
                audience=AUTHENTICATION_TOKEN_AUDIENCE,
            )

            assert payload["sub"] == str(user.id)
            assert payload["app-username"] == user.username
            assert payload["app-group"] == user.user_group.value
            assert payload["app-first-name"] == user.first_name
            assert payload["app-last-name"] == user.last_name
            assert payload["aud"] == AUTHENTICATION_TOKEN_AUDIENCE

    def it_sets_correct_expiration(user, app, mocker):
        with app.app_context():
            # Mock datetime.now to return a fixed date
            mocked_datetime = mocker.patch("src.services.auth_service.datetime")
            mocked_datetime.now.return_value = datetime.now()

            # Mock AUTHENTICATION_TOKEN_DURATION to 1 day
            mocker.patch(
                "src.services.auth_service.AUTHENTICATION_TOKEN_DURATION",
                timedelta(days=1),
            )

            token = AuthService._AuthService__make_auth_token(user, JWT_SECRET)
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=["HS256"],
                audience=AUTHENTICATION_TOKEN_AUDIENCE,
            )

            assert payload["exp"] == floor(
                (datetime.now() + timedelta(days=1)).timestamp()
            )


def describe_verify_auth_token():
    def it_verifies_valid_token(user, app):
        with app.app_context():
            token = AuthService._AuthService__make_auth_token(user, JWT_SECRET)

            user_info = AuthService._AuthService__verify_auth_token(token, JWT_SECRET)

            assert user_info["sub"] == str(user.id)
            assert user_info["app-username"] == user.username
            assert user_info["app-group"] == user.user_group.value
            assert user_info["app-first-name"] == user.first_name
            assert user_info["app-last-name"] == user.last_name

    def it_throws_error_on_invalid_token(app):
        with app.app_context():
            with pytest.raises(jwt.PyJWTError):
                AuthService._AuthService__verify_auth_token("invalid_token", JWT_SECRET)

    def it_throws_error_on_expired_token(mocker, user, app):
        mocked_datetime = mocker.patch("src.services.auth_service.datetime")
        mocked_datetime.now.return_value = datetime(2025, 1, 1, 0, 0, 0)
        mocker.patch(
            "src.services.auth_service.AUTHENTICATION_TOKEN_DURATION",
            timedelta(weeks=1),
        )

        with app.app_context():
            token = AuthService._AuthService__make_auth_token(user, JWT_SECRET)

            print("Token:", token)
            print(
                "Payload:", base64.b64decode(token.split(".")[1])
            )  # Decode the payload for debugging

            with pytest.raises(jwt.ExpiredSignatureError):
                AuthService._AuthService__verify_auth_token(token, JWT_SECRET)

    def it_throws_error_on_invalid_audience(mocker, user, app):
        with app.app_context():
            mocker.patch(
                "src.services.auth_service.AUTHENTICATION_TOKEN_AUDIENCE",
                "valid_audience",
            )
            token = AuthService._AuthService__make_auth_token(user, JWT_SECRET)

            mocker.patch(
                "src.services.auth_service.AUTHENTICATION_TOKEN_AUDIENCE",
                "invalid_audience",
            )

            with pytest.raises(jwt.InvalidAudienceError):
                AuthService._AuthService__verify_auth_token(token, JWT_SECRET)

    def it_throws_error_on_wrong_secret(user, app):
        with app.app_context():
            token = AuthService._AuthService__make_auth_token(user, JWT_SECRET)

            with pytest.raises(jwt.InvalidSignatureError):
                AuthService._AuthService__verify_auth_token(token, "invalid_secret")

    def it_throws_error_on_invalid_signature(user, app):
        with app.app_context():
            token = AuthService._AuthService__make_auth_token(user, JWT_SECRET)

            split_token = token.split(".")
            payload = base64.b64decode(split_token[1])
            payload = payload.replace(b"janedoe", b"johnsmith")
            payload = base64.b64encode(payload).decode("utf-8")
            invalid_token = f"{split_token[0]}.{payload}.{split_token[2]}"

            assert token != invalid_token

            with pytest.raises(jwt.InvalidTokenError):
                AuthService._AuthService__verify_auth_token(invalid_token, JWT_SECRET)


def describe_make_refresh_token():
    def it_generates_a_token(mocker, user):
        mocker.patch.object(
            RefreshTokenSessionRepository,
            "get_token",
            return_value=None,
        )
        mock_create_token = mocker.patch.object(
            RefreshTokenSessionRepository, "create_token"
        )

        token = AuthService._AuthService__make_refresh_token(user)

        assert len(token) > 0
        mock_create_token.assert_called_once()

    def it_generates_a_new_token_on_existing_token(mocker, user, session):
        mock_get_token = mocker.patch.object(
            RefreshTokenSessionRepository,
            "get_token",
            side_effect=[session, None],
        )
        mocker.patch.object(RefreshTokenSessionRepository, "create_token")

        token = AuthService._AuthService__make_refresh_token(user)

        assert mock_get_token.call_count == 2
        assert len(token) > 0
