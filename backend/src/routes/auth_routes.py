"""Routes for authentication and session management."""

from flask import Blueprint, jsonify, request
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

    username = fields.Str(required=True, validate=Length(min=1, max=50))
    password = fields.Str(required=True, validate=Length(min=1, max=150))


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
                        "username": {"type": "string", "minLength": 1, "maxLength": 50},
                        "password": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 150,
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
        user = AuthService.login(body["username"], body["password"])
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

    return jsonify(
        {"id": user.id, "username": user.username, "user_group": user.user_group.value}
    )
