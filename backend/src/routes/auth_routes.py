"""Routes for authentication and session management."""

from src.constants import (
    AUTHENTICATION_TOKEN_DURATION,
    AUTHENTICATION_TOKEN_COOKIE_NAME,
    REFRESH_TOKEN_DURATION,
    REFRESH_TOKEN_COOKIE_NAME,
)
from flask import Blueprint, make_response, request
from marshmallow.validate import Length
from flasgger import swag_from
from marshmallow import Schema, fields, ValidationError

from src.utils.error import ErrMsg, abort_with_err
from src.services.auth_service import (
    AuthService,
    UserNotFoundException,
    InvalidCredentialsException,
)

# CONSTANTS

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
        "tags": ["users"],
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
        {
            "id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "user_group": user.user_group.value,
            "created": user.created.timestamp(),
            "last_login": user.last_login.timestamp() if user.last_login else 0,
        },
        200,
    )

    resp.set_cookie(
        "user_group",
        user.user_group.value,
        max_age=round(REFRESH_TOKEN_DURATION.total_seconds()),
    )  # TODO: Set secure=True and samesite="Strict" in production

    resp.set_cookie(
        AUTHENTICATION_TOKEN_COOKIE_NAME,
        auth_token,
        max_age=round(AUTHENTICATION_TOKEN_DURATION.total_seconds()),
        httponly=True,
        # secure=True,  # TODO: Enable in production
        # samesite="Strict",  # TODO: Enable in production
    )

    resp.set_cookie(
        REFRESH_TOKEN_COOKIE_NAME,
        refresh_token,
        max_age=round(REFRESH_TOKEN_DURATION.total_seconds()),
        httponly=True,
        # secure=True,  # TODO: Enable in production
        # samesite="Strict",  # TODO: Enable in production
    )

    return resp
