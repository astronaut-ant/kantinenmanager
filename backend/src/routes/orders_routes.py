from pprint import pprint
from marshmallow import ValidationError, Schema, fields
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err
from flask import Blueprint, jsonify, request, g
from flasgger import swag_from
from src.models.user import UserGroup
from src.models.maindish import MainDish
from src.services.orders_service import OrdersService
from src.utils.exceptions import OrderAlreadyExistsForPersonAndDate


orders_routes = Blueprint("orders_routes", __name__)


class OrdersGetQuery(Schema):
    """
    Schema for the GET /api/orders endpoint

    Uses ISO 8601-formatted date strings (YYYY-MM-DD)
    """

    person_id = fields.UUID(data_key="person-id", required=False)
    location_id = fields.UUID(data_key="location-id", required=False)
    group_id = fields.UUID(data_key="group-id", required=False)
    date = fields.Date(data_key="date", required=False)
    date_start = fields.Date(data_key="date-start", required=False)
    date_end = fields.Date(data_key="date-end", required=False)


@orders_routes.get("/api/orders")
@login_required()
@swag_from(
    {
        "tags": ["orders"],
        "parameters": [
            {
                "in": "query",
                "name": "person-id",
                "description": "filter by a person",
                "type": "string",
                "format": "uuid",
                "required": False,
                "example": "123e4567-e89b-12d3-a456-426614174000",
            },
            {
                "in": "query",
                "name": "location-id",
                "description": "filter by a location",
                "type": "string",
                "format": "uuid",
                "required": False,
                "example": "123e4567-e89b-12d3-a456-426614174000",
            },
            {
                "in": "query",
                "name": "group-id",
                "description": "filter by a group",
                "type": "string",
                "format": "uuid",
                "required": False,
                "example": "123e4567-e89b-12d3-a456-426614174000",
            },
            {
                "in": "query",
                "name": "date",
                "description": "filter by a specific date (YYYY-MM-DD)",
                "type": "string",
                "format": "date",
                "required": False,
                "example": "2024-12-08",
            },
            {
                "in": "query",
                "name": "date-start",
                "description": "filter for orders on or after date-start (YYYY-MM-DD)",
                "type": "string",
                "format": "date",
                "required": False,
                "example": "2024-12-08",
            },
            {
                "in": "query",
                "name": "date-end",
                "description": "filter for orders on or before date-end (YYYY-MM-DD)",
                "type": "string",
                "format": "date",
                "required": False,
                "example": "2024-12-08",
            },
        ],
        "responses": {
            200: {
                "description": "Returns a list of orders",
                "schema": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Order"},
                },
            },
            401: {"description": "Unauthorized"},
            403: {"description": "Forbidden"},
        },
    }
)
def get_orders():
    """Get orders
    Returns a list of orders. You can (optionally) filter by person, location, specific date, date range, and group. Filters can be **combined**.
    ---
    """

    try:
        filters = OrdersGetQuery().load(request.args)
        pprint(filters)

    except ValidationError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Format der Daten in der Query nicht valide",
                details=err.messages,
            )
        )

    return []


class OrdersPostBody(Schema):
    """
    Schema for the POST /api/locations endpoint
    """

    person_id = fields.UUID(required=True)
    location_id = fields.UUID(required=True)
    date = fields.Date(required=True)  # ISO 8601-formatted date string
    main_dish = fields.Enum(MainDish, required=False)
    salad_option = fields.Boolean(required=False)


@orders_routes.post("/api/orders")
@login_required(groups=[UserGroup.gruppenleitung])
@swag_from(
    {
        "tags": ["orders"],
        "definitions": {
            "Order": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "person_id": {"type": "string"},
                    "location_id": {"type": "string"},
                    "date": {"type": "string"},
                    "main_dish": {"type": "string"},
                    "salad_option": {"type": "boolean"},
                },
            }
        },
        "parameters": [
            {
                "in": "body",
                "name": "body",
                "schema": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "person_id": {
                                "type": "string",
                                "format": "uuid",
                            },
                            "location_id": {
                                "type": "string",
                                "format": "uuid",
                            },
                            "date": {
                                "type": "string",
                                "format": "date",
                            },
                            "main_dish": {"type": "string"},
                            "salad_option": {"type": "boolean"},
                        },
                        "required": [
                            "person_id",
                            "location_id",
                            "date",
                        ],
                    },
                },
            },
        ],
        "responses": {
            201: {
                "description": "Order created",
                "schema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                    },
                },
            },
            400: {"description": "Bad request"},
            401: {"description": "Unauthorized"},
            403: {"description": "Forbidden"},
            404: {"description": "Not found"},
        },
    }
)
def create_orders():
    """
    Create a new order
    """
    try:
        orders_data = request.json
        orders = []
        for order_data in orders_data:
            order = OrdersPostBody().load(order_data)
            orders.append(order)
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
            order_ids = OrdersService.create_bulk_orders(
                orders, g.user_group, g.user_id
            )
        except OrderAlreadyExistsForPersonAndDate as err:
            abort_with_err(
                ErrMsg(
                    status_code=400,
                    title="Bestellung existiert bereits",
                    description="Eine Bestellung für eine der Person und existiert bereits für diesen Tag",
                    details=str(err),
                )
            )
        return jsonify({"ids": order_ids}), 201
