from uuid import UUID
from marshmallow import ValidationError, Schema, fields
from marshmallow.validate import Length
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err
from flask import Blueprint, jsonify, request, g
from flasgger import swag_from
from src.models.user import UserGroup
from src.models.maindish import MainDish
from src.services.orders_service import OrdersService
from src.utils.exceptions import OrderAlreadyExistsForPersonAndDate


orders_routes = Blueprint("orders_routes", __name__)


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
        "defenitions": {
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
