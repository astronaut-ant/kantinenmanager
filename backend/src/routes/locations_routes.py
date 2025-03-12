from uuid import UUID
from marshmallow import ValidationError
from src.schemas.locations_schemas import LocationFullNestedSchema, LocationFullSchema
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err
from src.models.user import UserGroup
from flask import Blueprint, jsonify, request, current_app as app
from flasgger import swag_from
from src.services.locations_service import LocationsService
from src.utils.exceptions import (
    AlreadyExistsError,
    BadValueError,
    IntegrityError,
    NotFoundError,
)


locations_routes = Blueprint("locations_routes", __name__)


@locations_routes.get("/api/locations")
# Must not be restricted, because of User Food order! (Frontend)
@login_required()
@swag_from(
    {
        "tags": ["locations"],
        "responses": {
            200: {
                "description": "Returns a list of all locations",
                "schema": {
                    "type": "array",
                    "items": LocationFullNestedSchema,
                },
            }
        },
    }
)
def get_locations():
    """Get all locations"""

    locations = LocationsService.get_locations(prejoin_location_leader=True)

    return LocationFullNestedSchema(many=True).dump(locations)


@locations_routes.get("/api/locations/<uuid:location_id>")
# Must not be restricted, because of User Food order! (Frontend)
@login_required()
@swag_from(
    {
        "tags": ["locations"],
        "parameters": [
            {
                "in": "path",
                "name": "location_id",
                "required": True,
                "schema": {"type": "string"},
            }
        ],
        "responses": {
            200: {
                "description": "Returns the location with the given ID",
                "schema": LocationFullNestedSchema,
            },
            404: {"description": "Location not found"},
        },
    }
)
def get_location_by_id(location_id: UUID):
    """Get a location by ID"""

    try:
        location = LocationsService.get_location_by_id(location_id)
    except NotFoundError as err:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Standort nicht gefunden",
                description="Es wurde kein Standort mit dieser ID gefunden",
                details=str(err),
            )
        )

    return LocationFullNestedSchema().dump(location)


@locations_routes.post("/api/locations")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["locations"],
        "parameters": [{"in": "body", "name": "body", "schema": LocationFullSchema}],
        "responses": {
            201: {
                "description": "Location sucessfully created, returns ID of the new location",
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
            400: {
                "description": "Validation error or location_name already exists or group leader does not exist"
            },
        },
    }
)
def create_location():
    """Create a new location"""
    try:
        body = LocationFullSchema().load(request.json)
    except ValidationError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Ungültige Anfrage",
                description="Die Anfrage ist ungültig",
                details=str(err),
            )
        )

    try:
        location_id = LocationsService.create_location(**body)
    except AlreadyExistsError as err:
        abort_with_err(
            ErrMsg(
                status_code=409,
                title="Standort konnte nicht erstellt werden",
                description="Der Standort konnte nicht erstellt werden",
                details=str(err),
            )
        )
    except NotFoundError as err:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Standort konnte nicht erstellt werden",
                description="Der Standort konnte nicht erstellt werden",
                details=str(err),
            )
        )
    return jsonify({"location_id": location_id}), 201


@locations_routes.put("/api/locations/<uuid:location_id>")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["locations"],
        "parameters": [
            {
                "in": "path",
                "name": "location_id",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
            },
            {"in": "body", "name": "body", "schema": LocationFullSchema},
        ],
        "responses": {
            200: {
                "description": "Returns the updated location",
                "schema": LocationFullNestedSchema,
            },
            400: {
                "description": "Validation error or you tried to change the location name to an already existing one"
            },
            404: {"description": "Location not found"},
        },
    }
)
def update_location(location_id: UUID):
    """Update a location"""

    try:
        body = LocationFullSchema().load(request.json)
    except ValidationError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Ungültige Anfrage",
                description="Die Anfrage ist ungültig",
                details=str(err),
            )
        )

    try:
        updated_location = LocationsService.update_location(
            location_id=location_id,
            user_id_location_leader=body["user_id_location_leader"],
            location_name=body["location_name"],
        )
    except NotFoundError as err:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Standort nicht gefunden",
                description=f"Der Standort mit ID {location_id} konnte nicht gefunden werden.",
                details=str(err),
            )
        )
    except AlreadyExistsError as err:
        abort_with_err(
            ErrMsg(
                status_code=409,
                title="Standort konnte nicht aktualisiert werden",
                description=f"Der Standort mit ID {location_id} konnte nicht aktualisiert werden",
                details=str(err),
            )
        )
    except BadValueError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Standort konnte nicht aktualisiert werden",
                description=str(err),
            )
        )

    return LocationFullNestedSchema().dump(updated_location)


@locations_routes.delete("/api/locations/<uuid:location_id>")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["locations"],
        "parameters": [
            {
                "in": "path",
                "name": "location_id",
                "required": True,
                "schema": {"type": "string"},
            },
        ],
        "responses": {
            200: {
                "description": "Location successfully deleted",
                "schema": {
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                },
            },
            404: {"description": "Location not found"},
        },
    }
)
def delete_location(location_id: UUID):
    """Delete a location"""

    try:
        location = LocationsService.get_location_by_id(location_id)
        LocationsService.delete_location(location)
    except NotFoundError as err:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Standort nicht gefunden",
                description="Es wurde kein Standort mit dieser ID gefunden",
                details=str(err),
            )
        )
    except IntegrityError as e:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Standort konnte nicht gelöscht werden",
                description=str(e),
            )
        )

    return jsonify({"message": "Standort erfolgreich gelöscht"})
