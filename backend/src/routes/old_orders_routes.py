from pprint import pprint
from uuid import UUID
from marshmallow import ValidationError, Schema, fields
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err
from flask import Blueprint, jsonify, request, g
from flasgger import swag_from
from src.models.user import UserGroup
from src.models.maindish import MainDish
from src.services.old_orders_service import OrdersFilters, OldOrdersService


old_orders_routes = Blueprint("old_orders_routes", __name__)


class OldOrdersGetQuery(Schema):
    """
    Schema for the GET /api/old-orders endpoint
    Uses ISO 8601-formatted date strings (YYYY-MM-DD)
    """

    person_id = fields.UUID(data_key="person-id", required=False)
    location_id = fields.UUID(data_key="location-id", required=False)
    group_id = fields.UUID(data_key="group-id", required=False)
    date = fields.Date(data_key="date", required=False)
    date_start = fields.Date(data_key="date-start", required=False)
    date_end = fields.Date(data_key="date-end", required=False)


@old_orders_routes.get("/api/pre-orders")
@login_required()  # TODO Permissions
@swag_from(
    {
        "tags": ["old_orders"],
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
                "description": "filter by a group **(Beware: this will only return employees of the group)**",
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
                    "items": {"$ref": "#/definitions/OldOrder"},
                },
            },
            401: {"description": "Unauthorized"},
            403: {"description": "Forbidden"},
        },
    }
)
def get_old_orders():
    """Get all old-orders
    Returns a list of old-orders. You can (optionally) filter by person, location, specific date, date range, and group. Filters can be **combined**.
    ---
    """

    try:
        query_params = OldOrdersGetQuery().load(request.args)
        filters = OrdersFilters(**query_params)
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

    orders = OldOrdersService.get_old_orders(filters)
    return jsonify([order.to_dict() for order in orders]), 200
