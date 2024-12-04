from flask import Blueprint, request, jsonify
from flasgger import swag_from
from marshmallow import ValidationError, Schema, fields
from marshmallow.validate import Length
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err
from src.repositories.groups_repository import GroupsRepository
from src.services.groups_sevice import GroupsService

groups_routes = Blueprint("groups_routes", __name__)


class GroupsPostBody(Schema):
    """
    Schema for the POST /api/groups endpoint
    """

    group_name = fields.Str(required=True, validate=Length(min=1, max=256))
    user_id_group_leader = fields.UUID(required=True)
    location_id = fields.UUID(required=True)


@groups_routes.post("/api/create_group")
@login_required(groups=["verwaltung"])
@swag_from(
    {
        "tags": ["groups"],
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
                            "maxLength": 64,
                        },
                        "user_id_group_leader": {
                            "type": "uuid",
                        },
                        "location_id": {
                            "type": "uuid",
                        },
                    },
                },
            }
        ],
        "responses": {
            200: {
                "description": "Creates a new group",
                "schema": {"$ref": "#/definitions/Group"},
            }
        },
    }
)
def create_group():
    """Create a new group
    Create a new group.
    ---
    """

    try:
        body = GroupsPostBody().load(request.json)
    except ValidationError:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Format der Daten im Request-Body nicht valide",
            )
        )

    try:
        location_id = GroupsRepository.create_group(**body)
    except ValueError:
        abort_with_err(
            ErrMsg(
                status_code=409,
                title="Location bereits vorhanden",
                description="Die Location existiert bereits",
            )
        )

    return jsonify({"id": location_id})


@groups_routes.get("/api/all_groups_with_locations")
@login_required(groups=["verwaltung"])
@swag_from(
    {
        "tags": ["groups"],
        "responses": {
            200: {
                "description": "Returns all groups with locations",
                "schema": {"$ref": "#/definitions/Groups"},
            }
        },
    }
)
def get_all_groups_by_location():
    """Get all groups with locations
    Get all groups with locations.
    ---
    """
    groups = GroupsService.get_all_groups_with_locations()
    return jsonify(groups)
