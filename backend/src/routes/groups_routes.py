from flask import Blueprint, request, jsonify
from flasgger import swag_from
from src.utils.auth_utils import login_required
from src.services.groups_sevice import GroupsService

groups_routes = Blueprint("groups_routes", __name__)


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
