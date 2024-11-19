from marshmallow import ValidationError
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err
from src.models.user import UserGroup
from src.services.users_service import UsersService
from flask import Blueprint, jsonify, request
from marshmallow.validate import Length
from marshmallow import Schema, fields
from flasgger import swag_from

# Routes sind die Verbindung zur Außenwelt und verantwortlich für die Verarbeitung von HTTP-Requests.
# Eine Route bekommt einen Request vom Nutzer (Frontend), extrahiert die enthaltenen Daten, gibt
# sie an den Service weiter und dann das entsprechende Ergebnis in einem Response Objekt zurück.
#
# Hier verwenden wir hauptsächlich Flask:
# https://flask.palletsprojects.com/en/stable/
#
# Flasgger dient der Dokumentation unserer API, ähnlich wie JavaDoc
# Unsere API Dokumentation: http://localhost:4200/apidocs/.
# Flasgger Doku: https://github.com/flasgger/flasgger

# Blueprints kommen aus Flask: https://flask.palletsprojects.com/en/stable/blueprints/
# Damit können wir unsere Anwendung "modularisieren".
users_routes = Blueprint("users_routes", __name__)


# Bei jedem GET Request (siehe HTTP) auf /api/users wird die get_users Funktion aufgerufen
@users_routes.get("/api/users")
@login_required(disabled=True)
@swag_from(
    {
        "tags": ["users"],
        "definitions": {
            "User": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "example": "123e4567-e89b-12d3-a456-426614174000",
                    },
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "username": {"type": "string"},
                    "user_group": {"type": "string"},
                    "created": {"type": "number"},
                    "last_login": {"type": "number"},
                },
            }
        },
        "responses": {
            200: {
                "description": "Returns a list of all users",
                "schema": {"type": "array", "items": {"$ref": "#/definitions/User"}},
            }
        },
    }
)
def get_users():
    """Get all users
    Get a list of all users
    ---
    """
    # Der docstring --^ ist wie wir Flasgger über die Parameter und Rückgabewerte
    # dieses Endpunkts informieren. Die Informationen werden extrahiert und
    # graphisch auf http://localhost:4200/apidocs/ angezeigt.
    # Achtung: Im Kommentar wird YAML verwendet, was **2** Leerzeichen als Einrückung verwendet.

    users = UsersService.get_users()

    # Diese wird in eine Liste an Dicts umgewandelt, aber ohne das Passwort
    users_dict = [
        {
            "id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "user_group": user.user_group.value,
            "created": user.created.timestamp(),
            "last_login": user.last_login.timestamp() if user.last_login else 0,
        }
        for user in users
    ]

    # Die dicts brauchen wir, denn daraus können wir JSON erzeugen.
    # Mit jsonify wird automatisch ein Response Object erstellt.
    return jsonify(users_dict)


# Das folgende kommt aus Marshmallow. https://marshmallow.readthedocs.io/en/stable/#
# Mit Marshmallow kann man Objekte serialisieren, deserialisieren und validieren, was eine Menge if Statements ersparen sollte.
# Das Schema gibt an, wie die Daten aussehen sollen, zusammen mit gewissen Einschränkungen.
class UsersPostBody(Schema):
    """
    Schema for the POST /users endpoint
    """

    first_name = fields.Str(required=True, validate=Length(min=1, max=64))
    last_name = fields.Str(required=True, validate=Length(min=1, max=64))
    username = fields.Str(required=True, validate=Length(min=1, max=64))
    password = fields.Str(required=True, validate=Length(min=8, max=256))
    user_group = fields.Enum(UserGroup, required=True)


@users_routes.post("/api/users")
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
                        "first_name": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 64,
                        },
                        "last_name": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 64,
                        },
                        "username": {"type": "string", "minLength": 1, "maxLength": 64},
                        "password": {
                            "type": "string",
                            "minLength": 8,
                            "maxLength": 256,
                        },
                        "user_group": {
                            "type": "string",
                            "enum": [
                                "verwaltung",
                                "standortleitung",
                                "gruppenleitung",
                                "kuechenpersonal",
                            ],
                        },
                    },
                },
            }
        ],
        "responses": {
            200: {
                "description": "Returns the ID and initial password of the new user",
                "schema": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "example": "123e4567-e89b-12d3-a456-426614174000",
                        },
                        "initial_password": {"type": "string"},
                    },
                },
            },
            400: {"description": "Validation error"},
        },
    }
)
def create_user():
    """Create a new user
    Create a new user
    ---
    """

    try:
        body = UsersPostBody().load(request.json)
    except ValidationError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Format der Daten im Request-Body nicht valide",
                details=err.messages,
            )
        )

    (id, initial_password) = UsersService.create_user(
        body.get("first_name"),
        body.get("last_name"),
        body.get("username"),
        body.get("password"),
        body.get("user_group"),
    )

    return jsonify({"id": id, "initial_password": initial_password})
