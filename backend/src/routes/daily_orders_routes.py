from uuid import UUID
from marshmallow import ValidationError, Schema, fields
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err
from flask import Blueprint, jsonify, request, g
from flasgger import swag_from
from src.models.user import UserGroup
from src.services.daily_orders_service import DailyOrdersService, WrongLocationError

daily_orders_routes = Blueprint("daily_orders_routes", __name__)


# TODO: Test all routes
@daily_orders_routes.get("/api/daily-orders")
@login_required(
    groups=[UserGroup.verwaltung, UserGroup.standortleitung, UserGroup.kuechenpersonal]
)
@swag_from(
    {
        "tags": ["daily_orders"],
        "responses": {
            200: {
                "description": "Returns daily orders filtered by user scope",
                "schema": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/DailyOrder"},
                },
            },
            404: {"description": "Bad request"},
        },
    }
)
def get_daily_orders():
    """
    Get all daily orders filtered by location of the user
    """
    try:
        all_daily_orders = DailyOrdersService.get_daily_orders_filtered_by_user_scope(
            g.user_id
        )
    except ValueError as err:  # TODO Specific exceptions
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Fehler",
                description="Ein Fehler ist aufgetreten.",
                details=str(err),
            )
        )
    daily_orders_dicts = [order.to_dict() for order in all_daily_orders]
    return jsonify(daily_orders_dicts), 200


@daily_orders_routes.get("/api/daily-orders/counted")
@login_required(
    groups=[UserGroup.verwaltung, UserGroup.kuechenpersonal]
)  # TODO: pick allowed usergroups
@swag_from(
    {
        "tags": ["daily_orders"],
        "responses": {
            200: {
                "description": "Returns count of Orders per Location",
                "schema": {
                    "type": "object",
                    "properties": {
                        "location_name": {"type": "string"},
                        "rot": {"type": "integer"},
                        "blau": {"type": "integer"},
                        "salad_option": {"type": "integer"},
                    },
                },
            },
            404: {"description": "Bad request"},
        },
    }
)
def get_daily_orders_count():
    """
    Count the number of daily orders (rot, blau, salad_option) for each location
    """
    try:
        orders_counted_by_location = DailyOrdersService.get_all_daily_orders_count()
    except ValueError:  # TODO Specific exceptions
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Fehler",
                description="Ein Fehler ist aufgetreten.",
                details="Ein Fehler ist aufgetreten.",
            )
        )
    return jsonify(orders_counted_by_location), 200


# QR-Code scannen
@daily_orders_routes.get("/api/daily-orders/<uuid:person_id>")
@login_required(groups=[UserGroup.kuechenpersonal])
@swag_from(
    {
        "tags": ["daily_orders"],
        "definitions": {
            "DailyOrder": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "person_id": {"type": "string"},
                    "location_id": {"type": "string"},
                    "main_dish": {"type": "string"},
                    "salad_option": {"type": "boolean"},
                    "handed_out": {"type": "boolean"},
                },
            }
        },
        "parameters": [
            {
                "in": "path",
                "name": "person_id",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
            },
        ],
        "responses": {
            200: {
                "description": "Returns a daily order",
                "oneOf": [
                    {"$ref": "#/definitions/DailyOrder"},
                    {"type": "object", "properties": {"message": {"type": "string"}}},
                ],
            },
        },
    }
)
def get_daily_order(person_id: UUID):
    """
    Get daily order for a person (kitchen staff)
    """
    try:
        daily_order = DailyOrdersService.get_daily_order(person_id, g.user_id)
        if daily_order is None:
            return jsonify({"message": "Keine Bestellung gefunden."}), 200
        return jsonify(daily_order.to_dict()), 200
    except WrongLocationError as err:
        abort_with_err(
            ErrMsg(
                status_code=401,
                title="Falscher Standort",
                description=f"Die Person {person_id} gehört nicht zum Standort dieses Küchenpersonals.",
                details=str(err),
            )
        )
    except ValueError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Fehler",
                description="Ein Fehler ist aufgetreten.",
                details=str(err),
            )
        )


@daily_orders_routes.put("/api/daily-orders/<int:daily_order_id>")
@login_required(groups=[UserGroup.kuechenpersonal])
@swag_from(
    {
        "tags": ["daily_orders"],
        "parameters": [
            {
                "in": "path",
                "name": "daily_order_id",
                "required": True,
                "schema": {"type": "integer"},
            },
            {
                "in": "query",
                "name": "handed_out",
                "description": "Set to true if the order has been handed out",
                "type": "boolean",
                "required": True,
            },
        ],
        "responses": {
            200: {
                "description": "Daily order updated",
                "schema": {
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                },
            },
            400: {"description": "Bad request"},
            404: {"description": "Not found"},
        },
    }
)
def update_daily_order(daily_order_id: int):
    """
    Update an existing daily order for a person (kitchen staff)
    """
    try:
        handed_out = request.args.get("handed_out")
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
        DailyOrdersService.update_daily_order(daily_order_id, handed_out, g.user_id)
    except WrongLocationError as err:
        abort_with_err(
            ErrMsg(
                status_code=401,
                title="Falscher Standort",
                description=f"Nutzer:in {g.user_id} hat keinen Zugriff auf diese Bestellung.",
                details=str(err),
            )
        )
    return jsonify({"message": "Bestellung erfolgreich angepasst."}), 200
