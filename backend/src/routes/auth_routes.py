"""Routes for authentication and session management."""

from src.services.users_service import UsersService
from src.utils.auth_utils import delete_token_cookies, login_required, set_token_cookies
from src.constants import (
    REFRESH_TOKEN_COOKIE_NAME,
    REFRESH_TOKEN_DURATION,
)
from flask import Blueprint, g, jsonify, make_response, request
from marshmallow.validate import Length
from flasgger import swag_from
from marshmallow import Schema, fields, ValidationError

from src.utils.error import ErrMsg, abort_with_err
from src.services.auth_service import (
    AuthService,
    UserNotFoundException,
    InvalidCredentialsException,
)


auth_routes = Blueprint("auth_routes", __name__)


class LoginBodySchema(Schema):
    """
    Schema to validate POST /api/login request body
    """

    username = fields.Str(required=True, validate=Length(min=1, max=64))
    password = fields.Str(required=True, validate=Length(min=1, max=256))


@auth_routes.post("/api/login")
@swag_from(
    {
        "tags": ["auth"],
        "parameters": [
            {
                "in": "body",
                "name": "body",
                "schema": {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "minLength": 1, "maxLength": 64},
                        "password": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 256,
                        },
                    },
                },
            }
        ],
        "responses": {
            200: {
                "description": "Returns user object on successful login",
                "schema": {"$ref": "#/definitions/User"},  # defined in users_routes.py
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
        body = LoginBodySchema().load(request.json)
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
        user, auth_token, refresh_token = AuthService.login(
            body.get("username"), body.get("password")
        )

    except UserNotFoundException:
        # Both Exceptions return the same error message as it would be a security risk to
        # differentiate between invalid username and invalid password
        abort_with_err(
            ErrMsg(
                status_code=401,
                title="Anmeldung fehlgeschlagen",
                description="Nutzername oder Passwort falsch",
            )
        )
    except InvalidCredentialsException:
        abort_with_err(
            ErrMsg(
                status_code=401,
                title="Anmeldung fehlgeschlagen",
                description="Nutzername oder Passwort falsch",
            )
        )

    resp = make_response(
        user.to_dict_without_pw_hash(),
        200,
    )

    resp.set_cookie(
        "user_group",
        user.user_group.value,
        max_age=round(REFRESH_TOKEN_DURATION.total_seconds()),
    )  # TODO: Set secure=True and samesite="Strict" in production

    set_token_cookies(resp, auth_token, refresh_token)

    return resp


@auth_routes.get("/api/is-logged-in")
@login_required()
@swag_from(
    {
        "tags": ["auth"],
        "responses": {
            200: {
                "description": "Returns user object if user is logged in",
                "schema": {"$ref": "#/definitions/User"},  # defined in users_routes.py
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

    return jsonify(user.to_dict_without_pw_hash())


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
