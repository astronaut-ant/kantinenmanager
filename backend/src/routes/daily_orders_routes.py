from uuid import UUID

from flask import Blueprint, jsonify, request, g
from flasgger import swag_from
from marshmallow import ValidationError

from src.utils.exceptions import NotFoundError, AccessDeniedError, BadValueError
from src.models.user import UserGroup
from src.schemas.daily_orders_schema import (
    DailyOrderFullSchema,
    DailyOrderHandedOutSchema,
)
from src.schemas.reports_schemas import CountOrdersSchema
from src.services.daily_orders_service import DailyOrdersService
from src.services.reports_service import ReportsService
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err

daily_orders_routes = Blueprint("daily_orders_routes", __name__)


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
        },
    }
)
def get_daily_orders():
    """
    Get all daily orders filtered by location of the user
    """

    daily_orders = DailyOrdersService.get_daily_orders_filtered_by_user_scope(g.user_id)

    return DailyOrderFullSchema(many=True).dump(daily_orders)


@daily_orders_routes.get("/api/daily-orders/counted")
@login_required(groups=[UserGroup.kuechenpersonal])
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
            403: {"description": "Access denied"},
            500: {"description": "Server Error"},
        },
    }
)
def get_daily_orders_counted():
    """
    Count the number of daily orders (rot, blau, salad_option) for each location
    """

    try:
        orders_counted_by_location = ReportsService.get_daily_orders_count(
            g.user_group, g.user_id
        )
    except AccessDeniedError as err:
        abort_with_err(
            ErrMsg(
                status_code=403,
                title="Nicht autorisiert",
                description=f"Nutzer:in mit ID {g.user_id} auf eine Bestellung.",
                details=str(err),
            )
        )
    except NotFoundError as err:
        # Handled as Server Error because logic would not allow this to happen.
        abort_with_err(
            ErrMsg(
                status_code=500,
                title="Server Error",
                description="Zuordnung Fehlgeschlagen.",
                details="Für die Zuordnung einer Bestellung zu einem Standort, wurde kein Standort gefunden",
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
            403: {"description": "Access denied"},
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
                description="Bestellung oder Person wurde nicht gefunden.",
                details=str(err),
            )
        )
    except AccessDeniedError as err:
        abort_with_err(
            ErrMsg(
                status_code=403,
                title="Nicht autorisiert",
                description="Sie haben keinen Zugriff auf diese Bestellung.",
                details=str(err),
            )
        )

    return DailyOrderFullSchema().dump(daily_order)


@daily_orders_routes.get("/api/daily-orders/<uuid:group_id>")
@login_required(groups=[UserGroup.gruppenleitung])
@swag_from(
    {
        "tags": ["daily_orders"],
        "parameters": [
            {
                "in": "path",
                "name": "group_id",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
            },
        ],
        "responses": {
            200: {
                "description": "Returns daily orders for a group",
                "schema": {"type": "array", "items": DailyOrderFullSchema},
            },
            404: {"description": "Not found"},
            403: {"description": "Access denied"},
        },
    }
)
def get_daily_orders_for_group(group_id: UUID):
    """
    Get daily orders for a group (group leader)
    """

    try:
        daily_orders = DailyOrdersService.get_daily_orders_for_group(
            group_id, g.user_id
        )
    except NotFoundError as err:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Gruppe nicht gefunden",
                description=f"Gruppe mit ID {group_id} konnte nicht gefunden werden.",
                details=str(err),
            )
        )
    except AccessDeniedError as err:
        abort_with_err(
            ErrMsg(
                status_code=403,
                title="Nicht autorisiert",
                description="Sie haben keinen Zugriff auf diese Gruppe.",
                details=str(err),
            )
        )

    return DailyOrderFullSchema(many=True).dump(daily_orders), 200


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
                "in": "body",
                "name": "body",
                "schema": DailyOrderHandedOutSchema,
                "required": True,
                "description": "True if Order was Handed out",
            },
        ],
        "responses": {
            200: {
                "description": "Updated daily order",
                "schema": DailyOrderFullSchema,
            },
            400: {"description": "Bad request"},
            404: {"description": "Not found"},
            403: {"description": "Access denied"},
        },
    }
)
def update_daily_order(daily_order_id: int):
    """
    Update an existing daily order for a person (kitchen staff)
    """

    try:
        order = DailyOrderHandedOutSchema.load(request.json)
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
            daily_order_id, order.handed_out, g.user_id
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
    except AccessDeniedError as err:
        abort_with_err(
            ErrMsg(
                status_code=403,
                title="Nicht autorisiert",
                description="Sie haben keinen Zugriff auf diese Bestellung.",
                details=str(err),
            )
        )
    except BadValueError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Eingabefehler",
                description="Ein Eingabefehler ist aufgetreten.",
                details=str(err),
            )
        )

    return DailyOrderFullSchema().dump(order), 200
