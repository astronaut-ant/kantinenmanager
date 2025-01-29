"""Routes for authentication and session management."""

from flask import Blueprint, g, make_response, request, current_app as app
from flasgger import swag_from
from marshmallow import ValidationError
from prometheus_client import Counter

from src.utils.exceptions import UserBlockedError
from src.metrics import metrics
from src.schemas.users_schemas import UserFullSchema
from src.constants import REFRESH_TOKEN_COOKIE_NAME, REFRESH_TOKEN_DURATION
from src.schemas.auth_schemas import AuthLoginSchema, AuthPasswordChangeSchema
from src.services.auth_service import AuthService
from src.utils.exceptions import InvalidCredentialsException, NotFoundError
from src.services.users_service import UsersService
from src.utils.auth_utils import delete_token_cookies, login_required, set_token_cookies
from src.utils.error import ErrMsg, abort_with_err


auth_routes = Blueprint("auth_routes", __name__)

successful_login_counter = Counter(
    "flask_successful_login_counter", "Total number of successful logins"
)
failed_login_counter = Counter(
    "flask_failed_login_counter", "Total number of failed logins"
)
blocked_login_counter = Counter(
    "flask_blocked_login_counter", "Total number of logins for blocked users"
)


@auth_routes.post("/api/login")
@metrics.counter("flask_login_requests_total", "Total number of login requests")
@metrics.summary("flask_login_request_latency_seconds", "Request latency for login")
@swag_from(
    {
        "tags": ["auth"],
        "parameters": [
            {
                "in": "body",
                "name": "body",
                "schema": AuthLoginSchema,
            }
        ],
        "responses": {
            200: {
                "description": "Returns user object on successful login",
                "schema": UserFullSchema,  # defined in users_routes.py
            },
            400: {"description": "Validation error"},
            401: {"description": "Unauthorized"},
        },
    }
)
def login():
    """Login
    Login with given username and password

    When the login is successful, the response will contain the user object and set the
    following cookies:

    - user_group: The user's group as plain text
    - auth_token: The authentication token as plain text (HTTP only)
    - refresh_token: The refresh token as plain text (HTTP only)
    ---
    """

    try:
        body = AuthLoginSchema().load(request.json)
    except ValidationError as err:
        resp = make_response()
        delete_token_cookies(resp)

        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Format der Daten im Request-Body nicht valide",
                details=err.messages,
            ),
            resp=resp,
        )

    try:
        user, auth_token, refresh_token = AuthService.login(
            body.get("username"), body.get("password")
        )

    except (NotFoundError, InvalidCredentialsException):
        # Both Exceptions return the same error message as it would be a security risk to
        # differentiate between invalid username and invalid password
        failed_login_counter.inc()

        resp = make_response()
        delete_token_cookies(resp)

        abort_with_err(
            ErrMsg(
                status_code=401,
                title="Anmeldung fehlgeschlagen",
                description="Nutzername oder Passwort falsch",
            ),
            resp=resp,
        )
    except UserBlockedError:
        failed_login_counter.inc()
        blocked_login_counter.inc()

        resp = make_response()
        delete_token_cookies(resp)

        abort_with_err(
            ErrMsg(
                status_code=423,
                title="Account gesperrt",
                description="Ihr Account wurde gesperrt. Bitte kontaktieren Sie einen Administrator.",
            ),
            resp=resp,
        )

    resp = make_response(
        UserFullSchema().dump(user),
        200,
    )

    # TODO: detete
    resp.set_cookie(
        "user_group",
        user.user_group.value,
        max_age=round(REFRESH_TOKEN_DURATION.total_seconds()),
    )  # TODO: Set secure=True and samesite="Strict" in production

    set_token_cookies(resp, auth_token, refresh_token)

    successful_login_counter.inc()

    return resp


@auth_routes.get("/api/is-logged-in")
@login_required()
@swag_from(
    {
        "tags": ["auth"],
        "responses": {
            200: {
                "description": "Returns user object if user is logged in",
                "schema": UserFullSchema,  # defined in users_routes.py
            },
            401: {"description": "Unauthorized"},
        },
    }
)
def is_logged_in():
    """Check if user is logged in
    Returns user object if user is logged in, otherwise 401.
    ---
    """

    user = UsersService.get_user_by_id(g.user_id)

    return UserFullSchema().dump(user)


@auth_routes.post("/api/logout")  # POST, because browsers may prefetch GET requests
@swag_from(
    {
        "tags": ["auth"],
        "responses": {
            204: {"description": "Logout successful (No Content)"},
        },
    }
)
def logout():
    """Logout
    Logs out the user by deleting the cookies and invalidating the refresh token.
    ---
    """

    refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    AuthService.logout(refresh_token)

    resp = make_response("", 204)

    delete_token_cookies(resp)

    return resp


@auth_routes.post("/api/account/change-password")
@login_required()
@swag_from(
    {
        "tags": ["auth"],
        "parameters": [
            {
                "in": "body",
                "name": "body",
                "schema": AuthPasswordChangeSchema,
            }
        ],
        "responses": {
            204: {"description": "Password changed successfully"},
            400: {"description": "Validation error"},
            401: {"description": "Unauthorized"},
        },
    }
)
def change_password():
    """Change password
    Change the password of the currently logged in user.
    ---
    """

    try:
        body = AuthPasswordChangeSchema().load(request.json)
    except ValidationError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Format der Daten im Request-Body nicht valide",
                details=err.messages,
            )
        )

    try:
        AuthService.change_password(
            g.user_id, body.get("old_password"), body.get("new_password")
        )
    except NotFoundError:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Passwort ändern fehlgeschlagen",
                description="Nutzer nicht gefunden",
            )
        )
    except InvalidCredentialsException:
        abort_with_err(
            ErrMsg(
                status_code=401,
                title="Passwort ändern fehlgeschlagen",
                description="Altes Passwort falsch",
            )
        )

    return "", 204
