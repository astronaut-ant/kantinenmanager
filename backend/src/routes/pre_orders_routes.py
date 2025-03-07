from uuid import UUID
from marshmallow import ValidationError
from src.schemas.pre_orders_schemas import (
    OrdersFilterSchema,
    PreOrderFullSchema,
    PreOrdersByGroupLeaderSchema,
)
from src.utils.exceptions import (
    NotFoundError,
    ActionNotPossibleError,
    AccessDeniedError,
    BadValueError,
    AlreadyExistsError,
)
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err
from flask import Blueprint, jsonify, request, g
from flasgger import swag_from
from src.models.user import UserGroup
from src.services.pre_orders_service import OrdersFilters, PreOrdersService


pre_orders_routes = Blueprint("pre_orders_routes", __name__)


# TODO: Test all routes


@pre_orders_routes.get("/api/pre-orders")
@login_required(
    [
        UserGroup.verwaltung,
        UserGroup.standortleitung,
        UserGroup.gruppenleitung,
        UserGroup.kuechenpersonal,
    ]
)
@swag_from(
    {
        "tags": ["pre_orders"],
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
                "description": "filter for pre_orders on or after date-start (YYYY-MM-DD)",
                "type": "string",
                "format": "date",
                "required": False,
                "example": "2024-12-08",
            },
            {
                "in": "query",
                "name": "date-end",
                "description": "filter for pre_orders on or before date-end (YYYY-MM-DD)",
                "type": "string",
                "format": "date",
                "required": False,
                "example": "2024-12-08",
            },
        ],
        "responses": {
            200: {
                "description": "Returns a list of pre_orders",
                "schema": {
                    "type": "array",
                    "items": PreOrderFullSchema,
                },
            },
            400: {"description": "Bad request"},
        },
    }
)
def get_pre_orders():
    """Get all pre-orders
    Returns a list of pre-orders. You can (optionally) filter by person, location, specific date, date range, and group. Filters can be **combined**.
    ---
    """

    try:
        query_params = OrdersFilterSchema().load(request.args)
        filters = OrdersFilters(**query_params)
    except ValidationError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Format der Daten im Request-Body nicht valide",
                details=err.messages,
            )
        )

    pre_orders = PreOrdersService.get_pre_orders(filters, g.user_id, g.user_group)
    return jsonify(pre_orders), 200


@pre_orders_routes.get("/api/pre-orders/<int:preorder_id>")
@login_required(
    [UserGroup.gruppenleitung, UserGroup.kuechenpersonal, UserGroup.verwaltung]
)
@swag_from(
    {
        "tags": ["pre_orders"],
        "parameters": [
            {
                "in": "path",
                "name": "preorder_id",
                "required": True,
                "schema": {"type": "integer"},
            }
        ],
        "responses": {
            200: {
                "description": "Returns a single pre-order",
                "schema": PreOrderFullSchema,
            },
            404: {"description": "Not found"},
            403: {"description": "Access Denied"},
        },
    }
)
def get_pre_order(preorder_id: int):
    """
    Get a single pre-order
    """

    try:
        order = PreOrdersService.get_pre_order_by_id(
            preorder_id, g.user_id, g.user_group
        )
    except NotFoundError as err:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Vorbestellung nicht gefunden",
                description=f"Die gesuchte Vorbestellung wurde nicht gefunden.",
                details=str(err),
            )
        )
    except AccessDeniedError as err:
        abort_with_err(
            ErrMsg(
                status_code=403,
                title="Keine Berechtigung",
                description="Sie haben keine Berechtigung für diese Aktion.",
                details=str(err),
            )
        )

    return jsonify(order), 200


@pre_orders_routes.get("/api/pre-orders/by-group-leader/<uuid:person_id>")
@login_required(groups=[UserGroup.gruppenleitung])
@swag_from(
    {
        "tags": ["pre_orders"],
        "parameters": [
            {
                "in": "path",
                "name": "person_id",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
            }
        ],
        "responses": {
            200: {
                "description": "Returns a list of pre-orders",
                "schema": PreOrdersByGroupLeaderSchema,
            },
            401: {"description": "Unauthorized"},
            403: {"description": "Forbidden"},
        },
    }
)
def get_pre_orders_by_group_leader(person_id: UUID):
    """Get orders by group leader
    Retrieves all groups of the group leader along with the orders of the employees in these groups.
    ---
    """

    try:
        pre_orders = PreOrdersService.get_pre_orders_by_group_leader(
            person_id, g.user_id, g.user_group
        )
    except NotFoundError as err:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Gruppenleitung nicht gefunden",
                description="Gruppenleitung nicht gefunden.",
                details=str(err),
            )
        )

    return jsonify(pre_orders), 200


@pre_orders_routes.post("/api/pre-orders")
@login_required(groups=[UserGroup.gruppenleitung])
@swag_from(
    {
        "tags": ["pre_orders"],
        "parameters": [
            {
                "in": "body",
                "name": "body",
                "schema": {"type": "array", "items": PreOrderFullSchema},
            },
        ],
        "responses": {
            201: {
                "description": "Orders created",
                "schema": {
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                },
            },
            400: {"description": "Bad request"},
            409: {"description": "Conflict"},
        },
    }
)
def create_update_preorders_employees():
    """
    Bulk create and update preorders for employees
    """
    try:
        orders = PreOrderFullSchema(many=True).load(request.json)
    except ValidationError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Format der Daten im Request-Body nicht valide",
                details=err.messages,
            )
        )

    if not orders:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Keine Vorbestellungen übergeben",
                description="Es wurden keine Vorbestellungen übergeben.",
            )
        )

    try:
        PreOrdersService.create_update_bulk_preorders(orders, g.user_id)
    except BadValueError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Datum nicht valide",
                description="Das Datum einer der Vorbestellungen ist nicht valide.",
                details=str(err),
            )
        )
    except ActionNotPossibleError as err:
        abort_with_err(
            ErrMsg(
                status_code=409,
                title="Person gehört nicht zu Standort/Gruppe",
                description="Eine der Personen gehört entweder nicht zum Standort oder zur Gruppe.",
                details=str(err),
            )
        )

    return jsonify({"message": "Vorbestellungen erfolgreich erstellt"}), 201


@pre_orders_routes.post("/api/pre-orders/users")
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
        "tags": ["pre_orders"],
        "parameters": [
            {
                "in": "body",
                "name": "body",
                "schema": PreOrderFullSchema,
            },
        ],
        "responses": {
            201: {
                "description": "Order created",
                "schema": PreOrderFullSchema,
            },
            400: {"description": "Bad request"},
            404: {"description": "Not found"},
            409: {"description": "Conflict"},
        },
    }
)
def create_preorder_user():
    """
    Create a new preorder for an user
    """
    try:
        preorder = PreOrderFullSchema().load(request.json)
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
        order = PreOrdersService.create_preorder_user(preorder, g.user_id)
    except AlreadyExistsError as err:
        abort_with_err(
            ErrMsg(
                status_code=409,
                title="Vorbestellung existiert bereits",
                description="Eine Vorbestellung für diese Person an diesem Datum existiert bereits.",
                details=str(err),
            )
        )
    except BadValueError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Die Daten der Vorbestellung sind nicht valide.",
                details=str(err),
            )
        )
    except AccessDeniedError as err:
        abort_with_err(
            ErrMsg(
                status_code=403,
                title="Keine Berechtigung",
                description="Sie haben keine Berechtigung für diese Aktion.",
                details=str(err),
            )
        )

    return jsonify(order), 201


@pre_orders_routes.put("/api/pre-orders/<int:preorder_id>")
@login_required(
    groups=[
        UserGroup.verwaltung,
        UserGroup.kuechenpersonal,
        UserGroup.standortleitung,
        UserGroup.gruppenleitung,
    ]
)
@swag_from(
    {
        "tags": ["pre_orders"],
        "parameters": [
            {
                "in": "path",
                "name": "preorder_id",
                "required": True,
                "schema": {"type": "integer"},
            },
            {
                "in": "body",
                "name": "body",
                "schema": PreOrderFullSchema,
            },
        ],
        "responses": {
            200: {
                "description": "Updated order",
                "schema": PreOrderFullSchema,
            },
            400: {"description": "Bad request"},
            403: {"description": "Access Denied"},
            404: {"description": "Not found"},
        },
    }
)
def update_preorder_user(preorder_id: UUID):
    """
    Update an existing preorder for an user
    """
    try:
        preorder = PreOrderFullSchema().load(request.json)
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
        order = PreOrdersService.update_preorder_user(preorder, preorder_id, g.user_id)
    except NotFoundError as err:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Vorbestellung nicht gefunden",
                description=f"Vorbestellung mit ID {preorder_id} nicht gefunden.",
                details=str(err),
            )
        )
    except BadValueError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Datum der Vorbestellung nicht valide",
                description="Das Datum der Vorbestellung ist nicht valide.",
                details=str(err),
            )
        )
    except AccessDeniedError as err:
        abort_with_err(
            ErrMsg(
                status_code=403,
                title="Falscher Benutzer",
                description="Sie haben keine Berechtigung für diese Aktion.",
                details=str(err),
            )
        )

    return jsonify(order), 200


@pre_orders_routes.delete("/api/pre-orders/<int:preorder_id>")
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
        "tags": ["pre_orders"],
        "parameters": [
            {
                "in": "path",
                "name": "preorder_id",
                "required": True,
                "schema": {"type": "string", "format": "int"},
            },
        ],
        "responses": {
            204: {
                "description": "Order deleted",
            },
            403: {"description": "Not authorized"},
            404: {"description": "Not found"},
        },
    }
)
def delete_preorder_user(preorder_id: int):
    """
    Delete an existing preorder for an user
    """
    try:
        PreOrdersService.delete_preorder_user(preorder_id, g.user_id)
    except NotFoundError as err:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Vorbestellung nicht gefunden",
                description=f"Vorbestellung mit ID {preorder_id} nicht gefunden.",
                details=str(err),
            )
        )
    except AccessDeniedError as err:
        abort_with_err(
            ErrMsg(
                status_code=403,
                title="Falscher Benutzer",
                description="Sie haben keine Berechtigung für diese Aktion.",
                details=str(err),
            )
        )

    return jsonify({"message": "Vorbestellungen erfolgreich gelöscht"}), 204
