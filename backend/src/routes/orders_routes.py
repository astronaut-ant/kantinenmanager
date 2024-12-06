from uuid import UUID
from marshmallow import ValidationError, Schema, fields
from marshmallow.validate import Length
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err
from flask import Blueprint, jsonify, request, g
from flasgger import swag_from
from src.models.user import UserGroup
from src.models.maindish import MainDish
from src.services.orders_service import PreOrdersService


orders_routes = Blueprint("orders_routes", __name__)


class OrdersPostBody(Schema):
    """
    Schema for the POST /api/locations endpoint
    """

    person_id = fields.UUID(required=True)
    location_id = fields.UUID(required=True)
    date = fields.DateTime(required=True)
    main_dish = fields.Enum(MainDish, required=False)
    salad_option = fields.Boolean(required=False)


@orders_routes.post("/api/orders")
@login_required(
    groups=[
        UserGroup.verwaltung,
        UserGroup.standortleitung,
        UserGroup.gruppenleitung,
        UserGroup.kuechenpersonal,
    ]
)
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
                    "type": "object",
                    "properties": {
                        "person_id": {"type": "string"},
                        "location_id": {"type": "string"},
                        "date": {"type": "string"},
                        "main_dish": {"type": "string"},
                        "salad_option": {"type": "boolean"},
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

        order_ids = []
        for order in orders:
            order_id = PreOrdersService.create_order(**order)
            order_ids.append(order_id)

        # Return success response with created order IDs
        return jsonify({"ids": order_ids}), 201
