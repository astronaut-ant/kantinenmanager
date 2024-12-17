from uuid import UUID
from marshmallow import ValidationError
from src.schemas.locations_schemas import LocationFullNestedSchema, LocationFullSchema
from src.schemas.users_schemas import UserFullSchema
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err
from src.models.user import UserGroup
from flask import Blueprint, jsonify, request
from flasgger import swag_from
from src.services.locations_service import LocationsService
from src.utils.exceptions import (
    LocationAlreadyExistsError,
    LeaderDoesNotExist,
    NotFoundError,
)


locations_routes = Blueprint("locations_routes", __name__)


@locations_routes.get("/api/locations")
@login_required(groups=[UserGroup.verwaltung])
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

    location = LocationsService.get_location_by_id(location_id)
    if location is None:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Standort nicht gefunden",
                description="Es wurde kein Standort mit dieser ID gefunden",
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
    except ValidationError:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Ungültige Anfrage",
                description="Die Anfrage ist ungültig",
            )
        )

    try:
        location_id = LocationsService.create_location(**body)
    except LocationAlreadyExistsError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Standort konnte nicht erstellt werden",
                description="Der Standort konnte nicht erstellt werden",
                detail=str(err),
            )
        )
    except LeaderDoesNotExist as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Standort konnte nicht erstellt werden",
                description="Der Standort konnte nicht erstellt werden",
                detail=str(err),
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
                details=err.messages,
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
                title=f"Standort nicht gefunden",
                description=f"Der Standort mit ID {body['id']} konnte nicht gefunden werden.",
                details=err,
            )
        )
    except LocationAlreadyExistsError:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Standort konnte nicht aktualisiert werden",
                description=f"Der Standort mit ID {body['id']} konnte nicht aktualisiert werden",
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

    location = LocationsService.get_location_by_id(location_id)
    if location is None:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Standort nicht gefunden",
                description="Es wurde kein Standort mit dieser ID gefunden",
            )
        )

    groups_of_location = LocationsService.get_groups_of_location(location_id)
    if groups_of_location:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Standort konnte nicht gelöscht werden",
                description="Der Standort konnte nicht gelöscht werden, weil er noch Gruppen enthält",
            )
        )

    try:
        LocationsService.delete_location(location)
    except Exception:
        abort_with_err(
            ErrMsg(
                status_code=500,
                title="Standort konnte nicht gelöscht werden",
                description="Der Standort konnte nicht gelöscht werden",
            )
        )
    return jsonify({"message": "Standort erfolgreich gelöscht"})
