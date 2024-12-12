from uuid import UUID
from marshmallow import ValidationError, Schema, fields
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err
from flask import Blueprint, jsonify, request, g
from flasgger import swag_from
from src.models.user import UserGroup
from src.services.daily_orders_service import DailyOrdersService, WrongLocationError

daily_orders_routes = Blueprint("daily_orders_routes", __name__)


class OrdersGetQuery(Schema):
    """
    Schema for the GET /api/pre-orders endpoint

    Uses ISO 8601-formatted date strings (YYYY-MM-DD)
    """

    person_id = fields.UUID(data_key="person-id", required=False)
    location_id = fields.UUID(data_key="location-id", required=False)
    group_id = fields.UUID(data_key="group-id", required=False)
    date = fields.Date(data_key="date", required=False)
    date_start = fields.Date(data_key="date-start", required=False)
    date_end = fields.Date(data_key="date-end", required=False)


@daily_orders_routes.get("/api/daily-orders")
@login_required()  # TODO Permissions
@swag_from(
    {
        "tags": ["daily_orders"],
    }
)
def get_daily_orders():
    """
    Get daily orders
    """
    abort_with_err(
        ErrMsg(
            status_code=501,
            title="Not implemented",
            description="This endpoint is not implemented yet.",
        )
    )


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
