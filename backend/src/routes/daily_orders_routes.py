from uuid import UUID

from flask import Blueprint, jsonify, request, g
from flasgger import swag_from
from marshmallow import ValidationError

from src.utils.exceptions import NotFoundError
from src.models.user import UserGroup
from src.schemas.daily_orders_schema import DailyOrderFullSchema, CountOrdersSchema
from src.services.daily_orders_service import DailyOrdersService, WrongLocationError
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err

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
                    "items": DailyOrderFullSchema,
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
                    "type": "array",
                    "items": CountOrdersSchema,
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
@daily_orders_routes.get("/api/daily-orders/person/<uuid:person_id>")
@login_required(groups=[UserGroup.kuechenpersonal])
@swag_from(
    {
        "tags": ["daily_orders"],
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
                "schema": DailyOrderFullSchema,
            },
            404: {"description": "Not found"},
        },
    }
)
def get_daily_order(person_id: UUID):
    """
    Get daily order for a person (kitchen staff)
    """
    try:
        daily_order = DailyOrdersService.get_daily_order(person_id, g.user_id)
    except NotFoundError as err:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Nicht gefunden",
                description=f"Bestellung für Person {person_id} nicht gefunden.",
                details=str(err),
            )
        )
    except WrongLocationError as err:
        abort_with_err(
            ErrMsg(
                status_code=403,
                title="Nicht autorisiert",
                description="Sie haben keinen Zugriff auf diese Bestellung.",
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

    return daily_order, 200


@daily_orders_routes.put("/api/daily-orders/<int:daily_order_id>")
@login_required(groups=[UserGroup.kuechenpersonal], disabled=True)
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
                "in": "body",
                "name": "body",
                "type": "object",
                "properties": {
                    "handed_out": {
                        "type": "boolean",
                        "required": True,
                        "description": "Set to true if the order has been handed out",
                    }
                },
            },
        ],
        "responses": {
            200: {
                "description": "Updated daily order",
                "schema": DailyOrderFullSchema,
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
        order = DailyOrderFullSchema(only=("handed_out",)).load(request.json)
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
        order = DailyOrdersService.update_daily_order(
            daily_order_id, order["handed_out"], g.user_id
        )
    except NotFoundError as err:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Nicht gefunden",
                description=f"Bestellung '{daily_order_id}' nicht gefunden.",
                details=str(err),
            )
        )
    except WrongLocationError as err:
        abort_with_err(
            ErrMsg(
                status_code=403,
                title="Nicht autorisiert",
                description="Sie haben keinen Zugriff auf diese Bestellung.",
                details=str(err),
            )
        )

    return order, 200
