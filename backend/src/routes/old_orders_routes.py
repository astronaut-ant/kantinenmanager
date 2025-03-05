from marshmallow import ValidationError, Schema, fields
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err
from flask import Blueprint, jsonify, request
from flasgger import swag_from
from src.services.old_orders_service import OrdersFilters, OldOrdersService
from src.models.user import UserGroup
from src.schemas.old_orders_schemas import OldOrderFilterSchema, OldOrderFullSchema


old_orders_routes = Blueprint("old_orders_routes", __name__)


# TODO: Test route
@old_orders_routes.get("/api/old-orders")
@login_required(groups=[UserGroup.verwaltung], disabled=True)
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
                    "items": OldOrderFullSchema,
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
        query_params = OldOrderFilterSchema().load(request.args)
        filters = OrdersFilters(**query_params)
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
    print(orders)
    return OldOrderFullSchema(many=True).dump(orders)
