from uuid import UUID
from marshmallow import ValidationError, Schema, fields
from marshmallow.validate import Length
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err
from src.services.locations_service import LocationsService, LocationAlreadyExistsError

from flask import Blueprint, jsonify, request
from flasgger import swag_from

locations_routes = Blueprint("locations_routes", __name__)


class LocationsPostBody(Schema):
    """
    Schema for the POST /api/locations endpoint
    """

    location_name = fields.Str(required=True, validate=Length(min=1, max=256))
    location_leader_id = fields.UUID(required=True)


@locations_routes.post("/api/locations")
@login_required(groups=["verwaltung"])
@swag_from(
    {
        "tags": ["locations"],
        "parameters": [
            {
                "in": "path",
                "name": "location_name",
                "required": True,
                "schema": {"type": "string"},
            },
            {
                "in": "path",
                "name": "location_leader_id",
                "required": True,
                "schema": {"type": "string"},
            },
        ],
        "responses": {
            200: {
                "description": "Returns the ID of the created location",
                "schema": {"$ref": "#/definitions/Locations"},
            },
            400: {"description": "Validation error"},
            409: {"description": "Location already exists"},
        },
    }
)
def create_location():
    """Create a new Location
    Create a new Location with the given name and leader ID.
    ---
    """

    try:
        body = LocationsPostBody().load(request.json)
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
        location_id = LocationsService.create_location(**body)
    except LocationAlreadyExistsError:
        abort_with_err(
            ErrMsg(
                status_code=409,
                title="Location bereits vorhanden",
                description="Die Location existiert bereits",
            )
        )

    return jsonify({"id": location_id})
