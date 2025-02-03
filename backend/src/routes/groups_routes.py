from uuid import UUID
from flask import Blueprint, g, request, jsonify
from flasgger import swag_from
from marshmallow import ValidationError
from src.models.user import UserGroup
from src.schemas.group_schemas import (
    GroupFullNestedSchema,
    GroupFullSchema,
    GroupFullWithEmployeesNestedSchema,
)
from src.services.groups_service import GroupsService
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err
from src.utils.exceptions import AlreadyExistsError, NotFoundError, BadValueError

groups_routes = Blueprint("groups_routes", __name__)


@groups_routes.post("/api/groups")
@login_required(groups=[UserGroup.verwaltung, UserGroup.standortleitung])
@swag_from(
    {
        "tags": ["groups"],
        "parameters": [
            {
                "in": "body",
                "name": "body",
                "schema": GroupFullSchema,
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
        body = GroupFullSchema().load(request.json)
        group_id = GroupsService.create_group(**body)

    except ValidationError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Ungültige Daten wurden übergeben.",
                details=err.messages,
            )
        )
    except AlreadyExistsError as err:
        abort_with_err(
            ErrMsg(
                status_code=409,
                title="Gruppe existiert bereits",
                description="Eine Gruppe mit diesem Namen existiert bereits.",
                details=str(err),
            )
        )
    except NotFoundError as err:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Gruppenleitung oder Standort existiert nicht",
                description="Gruppenleitung oder Standort existiert nicht.",
                details=str(err),
            )
        )
    except BadValueError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Ungültige Anfrage",
                description="Ungültige Anfrage.",
                details=str(err),
            )
        )

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
                "schema": GroupFullSchema,
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
        body = GroupFullSchema().load(request.json)
    except ValidationError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Ungültige Daten wurden übergeben.",
                details=err.messages,
            )
        )

    try:
        GroupsService.update_group(group_id, **body)
    except BadValueError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Ungültige Anfrage",
                description="Ungültige Anfrage.",
                details=str(err),
            )
        )
    except NotFoundError as err:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Gruppe nicht gefunden",
                description=f"Die Gruppe mit der angegebenen ID {group_id} existiert nicht.",
                details=str(err),
            )
        )
    except AlreadyExistsError as err:
        abort_with_err(
            ErrMsg(
                status_code=409,
                title="Gruppe existiert bereits",
                description="Eine Gruppe mit diesem Namen existiert bereits.",
                details=str(err),
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
    except NotFoundError:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Gruppe nicht gefunden",
                description=f"Die Gruppe mit der angegebenen ID {group_id} existiert nicht.",
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

    groups_with_locations = GroupsService.get_all_groups_with_locations(
        g.user_id, g.user_group
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
                "schema": GroupFullNestedSchema,
            },
            404: {"description": "Group not found."},
        },
    }
)
def get_group_by_id(group_id: UUID):
    """Get a group by ID."""

    try:
        group = GroupsService.get_group_by_id(group_id)
    except NotFoundError:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Gruppe nicht gefunden",
                description="Die Gruppe mit der angegebenen ID existiert nicht.",
            )
        )

    return GroupFullNestedSchema().dump(group)


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
                    "items": GroupFullNestedSchema,
                },
            }
        },
    }
)
def get_groups():
    """Get all groups for respective user."""

    groups = GroupsService.get_groups(g.user_id, g.user_group)

    return GroupFullNestedSchema(many=True).dump(groups)


@groups_routes.get("/api/groups/with-employees")
@login_required(groups=[UserGroup.verwaltung, UserGroup.standortleitung])
@swag_from(
    {
        "tags": ["groups"],
        "responses": {
            200: {
                "description": "Returns all groups with employees",
                "schema": {
                    "type": "array",
                    "items": GroupFullWithEmployeesNestedSchema,
                },
            },
            400: {"description": "Invalid request."},
        },
    }
)
def get_groups_with_employees():
    """Get all groups with their employees
    Retrieves all groups along with their employees.
    ---
    """

    groups = GroupsService.get_groups(g.user_id, g.user_group)

    return GroupFullWithEmployeesNestedSchema(many=True).dump(groups)


@groups_routes.delete("/api/groups/remove-replacement/<uuid:group_id>")
@login_required(groups=[UserGroup.standortleitung], disabled=True)
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
            200: {"description": "Updated group", "schema": GroupFullNestedSchema},
            400: {"description": "Invalid request."},
            404: {"description": "Group not found."},
        },
    }
)
def remove_group_replacement(group_id: UUID):
    """Remove a Group Replacement."""

    try:
        group = GroupsService.get_group_by_id(group_id)
    except NotFoundError:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Gruppe nicht gefunden",
                description="Die Gruppe mit der angegebenen ID existiert nicht.",
            )
        )

    if group.user_id_replacement is None:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Gruppe hat keine Vertretung",
                description=f"Die Gruppe {group.group_name} hat keine Vertretung.",
            )
        )

    try:
        group = GroupsService.update_group(
            group_id=group_id,
            group_name=group.group_name,
            group_number=group.group_number,
            user_id_group_leader=group.user_id_group_leader,
            location_id=group.location_id,
            user_id_replacement=None,
        )
    except BadValueError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Ungültige Anfrage",
                description="Ungültige Anfrage.",
                details=str(err),
            )
        )
    except NotFoundError as err:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Gruppe nicht gefunden",
                description=f"Die Gruppe existiert nicht.",
                details=str(err),
            )
        )
    except AlreadyExistsError as err:
        abort_with_err(
            ErrMsg(
                status_code=409,
                title="Gruppe existiert bereits",
                description=f"Eine Gruppe mit Nummer {group.group_number} existiert bereits.",
                details=str(err),
            )
        )

    return GroupFullNestedSchema().dump(group)


@groups_routes.get("/api/groups/create-qr/<uuid:group_id>")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["groups"],
        "parameters": [
            {
                "in": "path",
                "name": "group_id",
                "required": True,
                "schema": {"type": "string"},
            }
        ],
        "responses": {
            200: {
                "description": "Successfully created QR code as a PDF for each person in the group",
                "content": {
                    "application/pdf": {
                        "schema": {"type": "string", "format": "binary"}
                    }
                },
            },
            404: {
                "description": "QR codes could not be created for the group",
            },
        },
    }
)
def create_batch_qr_code(person_id: UUID):
    """Create QR codes for each employee in a group

    Authentication: required
    Authorization: Verwaltung
    ---
    """
    try:
        return GroupsService.create_batch_qr_code(person_id)
    except NotFoundError:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Person existiert nicht",
                description="Es existiert keine Person zu der ID in der Datenbank",
            )
        )
