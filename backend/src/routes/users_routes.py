from uuid import UUID

from flask import Blueprint, g, jsonify, request
from flasgger import swag_from
from marshmallow import ValidationError

from src.services.locations_service import LocationsService
from src.schemas.users_schemas import (
    GroupLeaderNestedSchema,
    LocationLeaderNestedSchema,
    UserFullSchema,
)
from src.models.user import UserGroup
from src.services.users_service import UsersService
from src.utils.exceptions import (
    NotFoundError,
    AlreadyExistsError,
    ActionNotPossibleError,
)
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err


users_routes = Blueprint("users_routes", __name__)


@users_routes.get("/api/users")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["users"],
        "parameters": [
            {"in": "query", "name": "user_group_filter", "schema": {"type": "string"}},
        ],
        "responses": {
            200: {
                "description": "Returns a list of all users",
                "schema": {"type": "array", "items": UserFullSchema},
            }
        },
    }
)
def get_users():
    """Get all users
    Get a list of all users

    Authentication: required
    Authorization: Verwaltung
    ---
    """
    user_group_filter = request.args.get("user_group_filter")
    users = UsersService.get_users(user_group_filter)

    return UserFullSchema(many=True).dump(users)


@users_routes.get("/api/users/<uuid:user_id>")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["users"],
        "parameters": [
            {
                "in": "path",
                "name": "user_id",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
            }
        ],
        "responses": {
            200: {
                "description": "Returns the user with the given ID",
                "schema": UserFullSchema,
            },
            404: {"description": "User not found"},
        },
    }
)
def get_user_by_id(user_id: UUID):
    """Get a user by ID
    Get a user by ID

    Authentication: required
    Authorization: Verwaltung
    ---
    """

    user = UsersService.get_user_by_id(user_id)
    if user is None:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Nutzer nicht gefunden",
                description="Es wurde kein Nutzer mit dieser ID gefunden",
            )
        )

    return UserFullSchema().dump(user)


@users_routes.get("/api/users/group-leaders")
@login_required(groups=[UserGroup.verwaltung, UserGroup.standortleitung])
@swag_from(
    {
        "tags": ["users"],
        "responses": {
            200: {
                "description": "Returns a list of all group leaders",
                "schema": {
                    "type": "array",
                    "items": GroupLeaderNestedSchema,
                },
            },
            400: {"description": "User not found"},
        },
    }
)
def get_group_leaders():
    """Get all group leaders with their respective groups
    Returns a list of all group leaders with their respective groups
    ---
    """

    try:
        group_leaders = UsersService.get_group_leader(g.user_id)
    except NotFoundError:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Nutzer nicht gefunden",
                description="Sie existieren nicht!",
            )
        )

    return GroupLeaderNestedSchema(many=True).dump(group_leaders)


@users_routes.get("/api/users/location-leaders")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["users"],
        "responses": {
            200: {
                "description": "Returns a list of all location leaders",
                "schema": {
                    "type": "array",
                    "items": LocationLeaderNestedSchema,
                },
            }
        },
    }
)
def get_location_leaders():
    """Get all location leaders with their location
    Returns a list of all location leaders with their location
    ---
    """

    location_leaders = UsersService.get_location_leader()

    return LocationLeaderNestedSchema(many=True).dump(location_leaders)


@users_routes.post("/api/users")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["users"],
        "parameters": [
            {
                "in": "body",
                "name": "body",
                "schema": UserFullSchema,
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
            400: {"description": "Validation error or username already exists"},
        },
    }
)
def create_user():
    """Create a new user
    Create a new user
    ---
    """

    try:
        body = UserFullSchema().load(request.json)
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
        id, initial_password = UsersService.create_user(**body)
    except AlreadyExistsError as e:
        abort_with_err(
            ErrMsg(
                status_code=409,
                title="Nutzername bereits vergeben",
                description=str(e),
            )
        )

    return jsonify({"id": id, "initial_password": initial_password})


@users_routes.put("/api/users/<uuid:user_id>/reset-password")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["users"],
        "parameters": [
            {
                "in": "path",
                "name": "user_id",
                "required": True,
                "schema": {"type": "string"},
            }
        ],
        "responses": {
            200: {
                "description": "Returns the new password of the user",
                "schema": {
                    "type": "object",
                    "properties": {"new_password": {"type": "string"}},
                },
            },
            404: {"description": "User not found"},
        },
    }
)
def reset_password(user_id: UUID):
    """Reset the password of a user
    Reset the password of a user.

    A new random password is generated and returned. All refresh tokens of the user are invalidated.

    Authentication: required
    Authorization: Verwaltung
    ---
    """

    user = UsersService.get_user_by_id(user_id)
    if user is None:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Nutzer nicht gefunden",
                description="Es wurde kein Nutzer mit dieser ID gefunden",
            )
        )

    initial_password = UsersService.reset_password(user)
    return jsonify({"new_password": initial_password})


@users_routes.put("/api/users/<uuid:user_id>")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["users"],
        "parameters": [
            {
                "in": "path",
                "name": "user_id",
                "required": True,
                "schema": {"type": "string"},
            },
            {
                "in": "body",
                "name": "body",
                "schema": UserFullSchema,
            },
        ],
        "responses": {
            200: {
                "description": "Returns the updated user",
                "schema": UserFullSchema,
            },
            400: {"description": "Validation error or username already exists"},
            404: {"description": "User not found"},
        },
    }
)
def update_user(user_id: UUID):
    """Update a user
    Update a user identified by ID
    ---
    """

    try:
        body = UserFullSchema().load(request.json)
    except ValidationError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Format der Daten im Request-Body nicht valide",
                details=err.messages,
            )
        )

    user = UsersService.get_user_by_id(user_id)
    if user is None:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Nutzer nicht gefunden",
                description="Es wurde kein Nutzer mit dieser ID gefunden",
            )
        )

    location = None

    try:
        if (location_id := body.get("location_id")) is not None:
            location = LocationsService.get_location_by_id(location_id)
            if location is None:
                raise NotFoundError()
    except NotFoundError:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Standort nicht gefunden",
                description="Es wurde kein Standort mit dieser ID gefunden",
            )
        )

    try:
        updated_user = UsersService.update_user(
            user,
            first_name=body["first_name"],
            last_name=body["last_name"],
            username=body["username"],
            user_group=body["user_group"],
            location=location,
        )
    except AlreadyExistsError:
        abort_with_err(
            ErrMsg(
                status_code=409,
                title="Nutzer:in-Name bereits vergeben",
                description="Der Nutzer:in-Name ist bereits vergeben",
            )
        )

    return UserFullSchema().dump(updated_user)


@users_routes.put("/api/users/<uuid:user_id>/block")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["users"],
        "parameters": [
            {
                "in": "path",
                "name": "user_id",
                "required": True,
                "schema": {"type": "string"},
            }
        ],
        "responses": {
            200: {
                "description": "User successfully blocked",
                "schema": {
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                },
            },
            404: {"description": "User not found"},
        },
    }
)
def block_user(user_id: UUID):
    """Block a user
    Block a user by ID. The user will not be able to log in anymore,
    although the authentication token will remain valid for a few minutes.

    Authentication: required
    Authorization: Verwaltung
    ---
    """
    user = UsersService.get_user_by_id(user_id)
    if user is None:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Nutzer nicht gefunden",
                description="Es wurde kein Nutzer mit dieser ID gefunden",
            )
        )

    UsersService.block_user(user)
    return jsonify({"message": "Nutzer erfolgreich blockiert"})


@users_routes.put("/api/users/<uuid:user_id>/unblock")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["users"],
        "parameters": [
            {
                "in": "path",
                "name": "user_id",
                "required": True,
                "schema": {"type": "string"},
            }
        ],
        "responses": {
            200: {
                "description": "User successfully unblocked",
                "schema": {
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                },
            },
            404: {"description": "User not found"},
        },
    }
)
def unblock_user(user_id: UUID):
    """Unblock a user
    Unblock a user by ID

    Authentication: required
    Authorization: Verwaltung
    ---
    """
    user = UsersService.get_user_by_id(user_id)
    if user is None:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Nutzer nicht gefunden",
                description="Es wurde kein Nutzer mit dieser ID gefunden",
            )
        )

    UsersService.unblock_user(user)
    return jsonify({"message": "Nutzer erfolgreich freigeschaltet"})


@users_routes.delete("/api/users/<uuid:user_id>")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["users"],
        "parameters": [
            {
                "in": "path",
                "name": "user_id",
                "required": True,
                "schema": {"type": "string"},
            }
        ],
        "responses": {
            200: {
                "description": "User successfully deleted",
                "schema": {
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                },
            },
            404: {"description": "User not found"},
        },
    }
)
def delete_user(user_id: UUID):
    """Delete a user
    Delete a user by ID

    Authentication: required
    Authorization: Verwaltung
    ---
    """
    user = UsersService.get_user_by_id(user_id)
    if user is None:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Nutzer nicht gefunden",
                description="Es wurde kein Nutzer mit dieser ID gefunden",
            )
        )

    try:
        UsersService.delete_user(user)
    except ActionNotPossibleError as e:
        abort_with_err(
            ErrMsg(
                status_code=409,
                title="Nutzer:in kann nicht gelöscht werden",
                description=str(e),
            )
        )
    return jsonify({"message": "Nutzer erfolgreich gelöscht"})
