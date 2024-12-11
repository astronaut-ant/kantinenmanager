from uuid import UUID
from flask import Blueprint, g, request, jsonify
from flasgger import swag_from
from marshmallow import ValidationError, Schema, fields
from marshmallow.validate import Length
from src.models.user import UserGroup
from src.utils.exceptions import GroupDoesNotExistError
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err
from src.services.groups_service import GroupsService
from src.services.users_service import UsersService

groups_routes = Blueprint("groups_routes", __name__)


class GroupCreateSchema(Schema):
    """
    Schema for POST and PUT api/groups endpoints.
    """

    group_name = fields.Str(required=True, validate=Length(min=1, max=256))
    user_id_group_leader = fields.UUID(required=True)
    location_id = fields.UUID(required=True)
    user_id_replacement = fields.UUID(required=False)


@groups_routes.post("/api/groups")
@login_required(groups=[UserGroup.verwaltung, UserGroup.standortleitung])
@swag_from(
    {
        "tags": ["groups"],
        "definitions": {
            "Group": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "example": "123e4567-e89b-12d3-a456-426614174000",
                    },
                    "group_name": {"type": "string"},
                    "group_leader": {
                        "type": "object",
                        "$ref": "#/definitions/UserReduced",
                    },
                    "group_leader_replacement": {
                        "type": "object",
                        "nullable": True,
                        "$ref": "#/definitions/UserReduced",
                    },
                    "location": {"type": "object", "$ref": "#/definitions/Location"},
                },
            },
            "GroupReduced": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "example": "123e4567-e89b-12d3-a456-426614174000",
                    },
                    "group_name": {"type": "string"},
                    "user_id_group_leader": {"type": "string"},
                    "user_id_replacement": {"type": "string"},
                    "location_id": {"type": "string"},
                },
            },
        },
        "parameters": [
            {
                "in": "body",
                "name": "body",
                "schema": {
                    "type": "object",
                    "properties": {
                        "group_name": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 256,
                        },
                        "user_id_group_leader": {
                            "type": "string",
                            "example": "123e4567-e89b-12d3-a456-426614174000",
                        },
                        "location_id": {
                            "type": "string",
                            "example": "123e4567-e89b-12d3-a456-426614174000",
                        },
                        "user_id_replacement": {
                            "type": "string",
                            "example": "123e4567-e89b-12d3-a456-426614174000",
                        },
                    },
                },
            }
        ],
        "responses": {
            201: {
                "description": "Group successfully created.",
                "schema": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "example": "123e4567-e89b-12d3-a456-426614174000",
                        }
                    },
                },
            },
            400: {"description": "Validation error."},
        },
    }
)
def create_group():
    """Create a new group."""
    try:
        body = GroupCreateSchema().load(request.json)
    except ValidationError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Ungültige Daten wurden übergeben.",
            )
        )
    except ValueError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Ungültige Anfrage",
                description="Ungültige Anfrage.",
                details=str(err),
            )
        )

    group_id = GroupsService.create_group(**body)
    return jsonify({"id": group_id}), 201


@groups_routes.put("/api/groups/<uuid:group_id>")
@login_required(groups=[UserGroup.verwaltung, UserGroup.standortleitung])
@swag_from(
    {
        "tags": ["groups"],
        "parameters": [
            {
                "in": "path",
                "name": "group_id",
                "required": True,
                "schema": {"type": "string"},
            },
            {
                "in": "body",
                "name": "body",
                "schema": {
                    "type": "object",
                    "properties": {
                        "group_name": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 256,
                        },
                        "user_id_group_leader": {"type": "string"},
                        "location_id": {"type": "string"},
                        "user_id_replacement": {"type": "string"},
                    },
                },
            },
        ],
        "responses": {
            200: {
                "description": "Group successfully updated.",
                "schema": {
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                },
            },
            404: {"description": "Group not found."},
        },
    }
)
def update_group(group_id: UUID):
    """Update a group."""
    try:
        body = GroupCreateSchema().load(request.json)
        changes = GroupsService.update_group(group_id, **body)
    except ValidationError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Ungültige Daten wurden übergeben.",
                details=err.messages,
            )
        )
    except ValueError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Ungültige Anfrage",
                description="Ungültige Anfrage.",
                details=str(err),
            )
        )
    except GroupDoesNotExistError:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Gruppe nicht gefunden",
                description="Die Gruppe mit der angegebenen ID existiert nicht.",
            )
        )
    if not changes:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Keine Änderungen",
                description="Es wurden keine Änderungen an der Gruppe vorgenommen.",
            )
        )
    return jsonify({"message": "Gruppe erfolgreich aktualisiert."})


@groups_routes.delete("/api/groups/<uuid:group_id>")
@login_required(groups=[UserGroup.verwaltung, UserGroup.standortleitung])
@swag_from(
    {
        "tags": ["groups"],
        "parameters": [
            {
                "in": "path",
                "name": "group_id",
                "required": True,
                "schema": {"type": "string"},
            },
        ],
        "responses": {
            200: {
                "description": "Group successfully deleted.",
                "schema": {
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                },
            },
            404: {"description": "Group not found."},
        },
    }
)
def delete_group(group_id: UUID):
    """Delete a group."""
    try:
        GroupsService.delete_group(group_id)
    except GroupDoesNotExistError:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Gruppe nicht gefunden",
                description="Die Gruppe mit der angegebenen ID existiert nicht.",
            )
        )
    return jsonify({"message": "Gruppe erfolgreich gelöscht."})


@groups_routes.get("/api/groups/with-locations")
@login_required(
    groups=[UserGroup.verwaltung, UserGroup.standortleitung, UserGroup.gruppenleitung]
)
@swag_from(
    {
        "tags": ["groups"],
        "responses": {
            200: {
                "description": "Returns all groups with locations",
                "schema": {
                    "type": "object",
                    "additionalProperties": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            }
        },
    }
)
def get_all_groups_with_locations():
    """Get all groups and their associated locations."""
    user_id = g.user_id
    user_group = g.user_group
    groups_with_locations = GroupsService.get_all_groups_with_locations(
        user_id, user_group
    )
    return jsonify(groups_with_locations)


@groups_routes.get("/api/groups/<uuid:group_id>")
@login_required(groups=[UserGroup.verwaltung, UserGroup.standortleitung])
@swag_from(
    {
        "tags": ["groups"],
        "parameters": [
            {
                "in": "path",
                "name": "group_id",
                "required": True,
                "schema": {"type": "string"},
            },
        ],
        "responses": {
            200: {
                "description": "Group details retrieved successfully.",
                "schema": {"$ref": "#/definitions/Group"},
            },
            404: {"description": "Group not found."},
        },
    }
)
def get_group_by_id(group_id: UUID):
    """Get a group by ID."""
    try:
        group = GroupsService.get_group_by_id(group_id)
    except GroupDoesNotExistError:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Gruppe nicht gefunden",
                description="Die Gruppe mit der angegebenen ID existiert nicht.",
            )
        )
    return jsonify(group.to_dict())


@groups_routes.get("/api/groups")
@login_required(
    groups=[UserGroup.verwaltung, UserGroup.standortleitung, UserGroup.gruppenleitung]
)
@swag_from(
    {
        "tags": ["groups"],
        "responses": {
            200: {
                "description": "Returns all groups",
                "schema": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Group"},
                },
            }
        },
    }
)
def get_groups():
    """Get all groups for respective user."""
    user_id = g.user_id
    user_group = g.user_group
    try:
        groups = GroupsService.get_groups(user_id, user_group)
    except ValueError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Ungültige Anfrage",
                description="Ungültige Anfrage.",
                details=str(err),
            )
        )
    groups_to_dict = [group.to_dict() for group in groups]
    return jsonify(groups_to_dict)


@groups_routes.delete("/api/groups/remove-replacement/<uuid:group_id>")
@login_required(groups=[UserGroup.standortleitung])
@swag_from(
    {
        "tags": ["groups"],
        "parameters": [
            {
                "in": "path",
                "name": "group_id",
                "required": True,
                "schema": {"type": "string"},
            },
        ],
        "responses": {
            200: {"description": "Group Replacement successfully removed."},
            404: {"description": "Group not found."},
            404: {"description": "Group Replacement not found."},
        },
    }
)
def remove_group_replacement(group_id: UUID):
    """Remove a Group Replacement."""
    try:
        group_replacement = GroupsService.remove_group_replacement(group_id)
    except GroupDoesNotExistError:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Gruppe nicht gefunden",
                description="Die Gruppe mit der angegebenen ID existiert nicht.",
            )
        )
    if group_replacement is None:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Gruppen Vertretung nicht gefunden",
                description="Die Gruppenvertretung wurde nicht gefunden.",
            )
        )
    user = UsersService.get_user_by_id(group_replacement)
    return jsonify(
        {
            "message": f"Group Replacement: '{user.first_name}', ' {user.last_name}' successfully removed."
        }
    )
