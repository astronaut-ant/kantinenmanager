"""Tests for the AuthService class"""

import base64
from datetime import datetime, timedelta
import uuid
import pytest
import jwt
from src import app as project_app
from src.models.refresh_token_session import RefreshTokenSession
from src.models.user import User, UserGroup
from src.services.auth_service import (
    AuthService,
    InvalidCredentialsException,
    UnauthenticatedException,
    UserNotFoundException,
)

# * Fixtures bieten eine Möglichkeit, Code zu schreiben, der von mehreren Tests verwendet wird.
# * Die unteren Fixtures erzeugen ein Objekt, das automatisch an die Tests übergeben wird,
# * wenn sie als Argument in der Testfunktion definiert sind.


@pytest.fixture()
def app():
    project_app.config["JWT_SECRET"] = "super_secret"
    project_app.config["TESTING"] = True
    yield project_app


@pytest.fixture()
def user():
    user = User(
        first_name="Jane",
        last_name="Doe",
        username="janedoe",
        hashed_password="hashed_password",
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


# * Mit Unterstrich beginnen Hilfsfunktionen, die nicht als Testfälle ausgeführt werden.


def _helper_mock_users_repo_with_attrs(mocker, attrs):
    # Hier wird ein Mock, also ein "Platzhalter" für das UsersRepository erstellt.
    # Wir wollen uns nur auf den Service konzentrieren und nicht auf die Datenbank.
    # Außerdem vermeiden wir, dass die Tests von der Datenbank abhängig sind.

    mockRepo = mocker.Mock()
    mockRepo.configure_mock(**attrs)
    mocker.patch(
        "src.services.auth_service.UsersRepository",
        mockRepo,
    )  # patch ersetzt das UsersRepository im AuthService durch den Mock.
    return mockRepo


def _helper_mock_refresh_token_session_repo_with_attrs(mocker, attrs):
    mockRepo = mocker.Mock()
    mockRepo.configure_mock(**attrs)
    mocker.patch(
        "src.services.auth_service.RefreshTokenSessionRepository",
        mockRepo,
    )
    return mockRepo


# * Mit describe() können wir die Tests in Gruppen einteilen und so die Ausgabe strukturieren.
# * Hier wird ein describe-Block für jede Methode in AuthService erstellt.


def describe_generate_password():
    # * Darin werden die Testfälle definiert. Jede Funktion ist ein eigener Testfall.
    # * Tests folgen generell dem Schema: Arrange, Act, Assert, (Cleanup).
    # * Arrange: Vorbereitung der Testumgebung
    # * Act: Ausführung des zu testenden Codes
    # * Assert: Überprüfung des erwarteten Ergebnisses
    # * https://docs.pytest.org/en/stable/explanation/anatomy.html
    def it_generates_a_password():
        password = AuthService.generate_password()
        assert password  # * assert prüft, ob der Ausdruck wahr ist, wenn nicht wird ein Fehler geworfen und der Test schlägt fehl.
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


def describe_make_auth_token():
    def it_generates_a_token(user, app):
        # * Hier brauchen wir Zugriff auf die Flask-App, um auf die Konfiguration zuzugreifen.
        # * Dafür bietet Flask die app_context()-Methode, die den Kontext der App in einem Block zur Verfügung stellt.
        # * https://flask.palletsprojects.com/en/stable/testing/
        with app.app_context():
            token = AuthService._AuthService__make_auth_token(
                user, app.config["JWT_SECRET"]
            )
            assert token
            assert len(token) > 0
            assert (
                len(token.split(".")) == 3
            )  # JWT token consists of 3 parts separated by a dot


def describe_verify_auth_token():
    def it_verifies_valid_token(user, app):
        with app.app_context():
            token = AuthService._AuthService__make_auth_token(
                user, app.config["JWT_SECRET"]
            )
            payload = AuthService._AuthService__verify_auth_token(
                token, app.config["JWT_SECRET"]
            )
            assert payload
            assert uuid.UUID(payload["sub"]) == user.id

    def it_throws_error_on_invalid_token(app):
        with app.app_context():
            with pytest.raises(jwt.PyJWTError):
                AuthService._AuthService__verify_auth_token(
                    "invalid_token", app.config["JWT_SECRET"]
                )

    def it_throws_error_on_expired_token(mocker, user, app):
        # Mock datetime.now to return a fixed date
        mocked_datetime = mocker.patch("src.services.auth_service.datetime")
        mocked_datetime.now.return_value = datetime(2021, 1, 1, 0, 0, 0)

        # Mock AUTHENTICATION_TOKEN_DURATION to 1 day
        mocker.patch(
            "src.services.auth_service.AUTHENTICATION_TOKEN_DURATION",
            timedelta(weeks=1),
        )

        with app.app_context():
            token = AuthService._AuthService__make_auth_token(
                user, app.config["JWT_SECRET"]
            )

            print("Token:", token)
            print(
                "Payload:", base64.b64decode(token.split(".")[1])
            )  # Decode the payload for debugging

            with pytest.raises(jwt.ExpiredSignatureError):
                AuthService._AuthService__verify_auth_token(
                    token, app.config["JWT_SECRET"]
                )

    def it_throws_error_on_invalid_audience(mocker, user, app):
        with app.app_context():
            mocker.patch(
                "src.services.auth_service.AUTHENTICATION_TOKEN_AUDIENCE",
                "valid_audience",
            )
            token = AuthService._AuthService__make_auth_token(
                user, app.config["JWT_SECRET"]
            )

            mocker.patch(
                "src.services.auth_service.AUTHENTICATION_TOKEN_AUDIENCE",
                "invalid_audience",
            )

            with pytest.raises(jwt.InvalidAudienceError):
                AuthService._AuthService__verify_auth_token(
                    token, app.config["JWT_SECRET"]
                )

    def it_throws_error_on_wrong_secret(user, app):
        with app.app_context():
            token = AuthService._AuthService__make_auth_token(
                user, app.config["JWT_SECRET"]
            )

            with pytest.raises(jwt.InvalidSignatureError):
                AuthService._AuthService__verify_auth_token(token, "invalid_secret")

    def it_throws_error_on_invalid_signature(user, app):
        with app.app_context():
            token = AuthService._AuthService__make_auth_token(
                user, app.config["JWT_SECRET"]
            )

            split_token = token.split(".")
            payload = base64.b64decode(split_token[1])
            payload = payload.replace(b"janedoe", b"johnsmith")
            payload = base64.b64encode(payload).decode("utf-8")
            invalid_token = f"{split_token[0]}.{payload}.{split_token[2]}"

            assert token != invalid_token

            with pytest.raises(jwt.InvalidTokenError):
                AuthService._AuthService__verify_auth_token(
                    invalid_token, app.config["JWT_SECRET"]
                )


def describe_make_refresh_token():
    def it_generates_a_token(mocker, user):
        mockRepo = mocker.Mock()
        attrs = {"get_token.return_value": None, "create_token.return_value": None}
        mockRepo.configure_mock(**attrs)
        mocker.patch(
            "src.services.auth_service.RefreshTokenSessionRepository",
            mockRepo,
        )

        token = AuthService._AuthService__make_refresh_token(user)

        assert len(token) > 0
        mockRepo.create_token.assert_called_once()


def describe_verify_refresh_token():

    def it_verifies_valid_refresh_token(mocker, session):
        mockRepo = _helper_mock_refresh_token_session_repo_with_attrs(
            mocker, {"get_token.return_value": session}
        )

        verified_session = AuthService._AuthService__verify_refresh_token(
            session.refresh_token
        )

        assert verified_session == session
        mockRepo.get_token.assert_called_once_with(session.refresh_token)

    def it_throws_error_on_invalid_refresh_token(mocker):
        token = "invalid_token"

        _helper_mock_refresh_token_session_repo_with_attrs(
            mocker, {"get_token.return_value": None}
        )

        with pytest.raises(UnauthenticatedException):
            AuthService._AuthService__verify_refresh_token(token)

    def it_throws_error_on_expired_refresh_token(mocker, session):
        session.expires = datetime.now() - timedelta(days=1)

        _helper_mock_refresh_token_session_repo_with_attrs(
            mocker, {"get_token.return_value": session}
        )

        with pytest.raises(UnauthenticatedException):
            AuthService._AuthService__verify_refresh_token(session.refresh_token)

    def it_throws_error_when_already_used(mocker, session):
        session.last_used = datetime.now()

        _helper_mock_refresh_token_session_repo_with_attrs(
            mocker, {"get_token.return_value": session}
        )

        with pytest.raises(UnauthenticatedException):
            AuthService._AuthService__verify_refresh_token(session.refresh_token)


def describe_login():

    def it_throws_error_on_non_exising_username(mocker):
        attrs = {"get_user_by_username.return_value": None}
        _helper_mock_users_repo_with_attrs(mocker, attrs)

        with pytest.raises(UserNotFoundException):
            AuthService.login("johndoe", "password")

    def it_throws_error_on_invalid_password(mocker, user):
        attrs = {"get_user_by_username.return_value": user}
        _helper_mock_users_repo_with_attrs(mocker, attrs)

        with pytest.raises(InvalidCredentialsException):
            AuthService.login(user.username, "wrong_password")

    def it_returns_tokens_on_valid_credentials(mocker, user, app):
        password = "password123"
        hashed_password = AuthService.hash_password(password)
        user.hashed_password = hashed_password

        attrs = {"get_user_by_username.return_value": user}
        _helper_mock_users_repo_with_attrs(mocker, attrs)

        with app.app_context():
            user, auth_token, refresh_token = AuthService.login(user.username, password)

        assert user == user
        assert len(auth_token) > 0
        assert len(refresh_token) > 0


def describe_authenticate():
    def it_accepts_valid_auth_token(mocker, user, app):
        with app.app_context():
            # Generate a valid auth token
            auth_token = AuthService._AuthService__make_auth_token(
                user, app.config["JWT_SECRET"]
            )

            user_info, new_auth_token, new_refresh_token = AuthService.authenticate(
                auth_token=auth_token, refresh_token=None
            )

            assert user_info["id"] == user.id
            assert new_auth_token is None
            assert new_refresh_token is None

    def it_throws_error_on_invalid_auth_and_no_refresh_token(mocker, app):
        with app.app_context():
            with pytest.raises(UnauthenticatedException):
                AuthService.authenticate(auth_token="invalid", refresh_token=None)

    def it_throws_error_on_invalid_auth_and_invalid_refresh_token(mocker, app):
        with app.app_context():
            _helper_mock_refresh_token_session_repo_with_attrs(
                mocker, {"get_token.return_value": None}
            )
            with pytest.raises(UnauthenticatedException):
                AuthService.authenticate(auth_token="invalid", refresh_token="invalid")

    def it_generates_new_tokens_on_valid_refresh_token(mocker, app, session, user):
        with app.app_context():
            refresh_token = session.refresh_token

            # Mock the RefreshTokenSessionRepository to return the session
            mockSessionRepo = _helper_mock_refresh_token_session_repo_with_attrs(
                mocker,
                {
                    "get_token": lambda token: (
                        session if token == session.refresh_token else None
                    ),
                    "create_token.return_value": None,
                    "update_token.return_value": None,
                },
            )
            _helper_mock_users_repo_with_attrs(
                mocker, {"get_user_by_id.return_value": user}
            )

            # Authenticate with the valid refresh token
            user_info, new_auth_token, new_refresh_token = AuthService.authenticate(
                auth_token="invalid", refresh_token=refresh_token
            )

            assert user_info["id"] == user.id
            assert len(new_auth_token) > 0
            assert len(new_refresh_token) > 0
            mockSessionRepo.create_token.assert_called_once()

    # TODO: Add test for blocked user
