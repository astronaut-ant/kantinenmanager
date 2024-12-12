from pprint import pprint
from uuid import UUID
from marshmallow import ValidationError, Schema, fields
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err
from flask import Blueprint, jsonify, request, g
from flasgger import swag_from
from src.models.user import UserGroup
from src.models.maindish import MainDish
from src.services.pre_orders_service import (
    OrdersFilters,
    PreOrdersService,
    PersonNotPartOfGroup,
    PersonNotPartOfLocation,
    WrongUserError,
)


pre_orders_routes = Blueprint("pre_orders_routes", __name__)


class OrdersGetQuery(Schema):
    """
    Schema for the GET /api/daily-orders endpoint

    Uses ISO 8601-formatted date strings (YYYY-MM-DD)
    """

    person_id = fields.UUID(data_key="person-id", required=False)
    location_id = fields.UUID(data_key="location-id", required=False)
    group_id = fields.UUID(data_key="group-id", required=False)
    date = fields.Date(data_key="date", required=False)
    date_start = fields.Date(data_key="date-start", required=False)
    date_end = fields.Date(data_key="date-end", required=False)


@pre_orders_routes.get("/api/pre-orders")
@login_required()  # TODO Permissions
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
                    "items": {"$ref": "#/definitions/PreOrder"},
                },
            },
            401: {"description": "Unauthorized"},
            403: {"description": "Forbidden"},
        },
    }
)
def get_pre_orders():
    """Get all pre-orders
    Returns a list of pre-orders. You can (optionally) filter by person, location, specific date, date range, and group. Filters can be **combined**.
    ---
    """

    try:
        query_params = OrdersGetQuery().load(request.args)
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

    pre_orders = PreOrdersService.get_pre_orders(filters)
    return jsonify([order.to_dict() for order in pre_orders]), 200


@pre_orders_routes.get("/api/pre-orders/<int:preorder_id>")
@login_required()  # TODO Permissions
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
                "schema": {"$ref": "#/definitions/PreOrder"},
            },
            404: {"description": "Not found"},
        },
    }
)
def get_pre_order(preorder_id: int):
    """
    Get a single pre-order
    """

    order = PreOrdersService.get_pre_order_by_id(preorder_id)
    if order is None:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Bestellung nicht gefunden",
                description=f"Bestellung mit ID {preorder_id} nicht gefunden.",
            )
        )

    return jsonify(order.to_dict()), 200


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
            200: {},
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
    abort_with_err(
        ErrMsg(
            status_code=501,
            title="Not implemented",
            description="This endpoint is not implemented yet.",
        )
    )


class PreOrdersPostPutBody(Schema):
    """
    Schema for the POST and PUT /api/locations endpoint
    """

    person_id = fields.UUID(required=True)
    location_id = fields.UUID(required=True)
    date = fields.Date(required=True)  # ISO 8601-formatted date string
    nothing = fields.Boolean(required=True, default=False)
    main_dish = fields.Enum(MainDish, required=False, default=None)
    salad_option = fields.Boolean(required=False, default=False)


@pre_orders_routes.post("/api/pre-orders")
@login_required(groups=[UserGroup.gruppenleitung], disabled=True)
@swag_from(
    {
        "tags": ["pre_orders"],
        "definitions": {
            "PreOrder": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "example": 1},
                    "person_id": {
                        "type": "string",
                        "format": "uuid",
                        "example": "123e4567-e89b-12d3-a456-426614174000",
                    },
                    "location_id": {
                        "type": "string",
                        "format": "uuid",
                        "example": "123e4567-e89b-12d3-a456-426614174000",
                    },
                    "date": {
                        "type": "string",
                        "format": "date",
                        "example": "2024-12-08",
                    },
                    "nothing": {"type": "boolean", "example": False},
                    "main_dish": {
                        "type": "string",
                        "enum": ["rot", "blau"],
                        "nullable": True,
                    },
                    "salad_option": {"type": "boolean", "example": True},
                    "last_changed": {"type": "number", "example": 1733780000.000099},
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
                            "main_dish": {"type": "string", "nullable": True},
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
                "description": "Orders created",
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
def create_update_preorders_employees():
    """
    Bulk create and update preorders for employees
    """
    try:
        orders = PreOrdersPostPutBody(many=True).load(request.json)
        if not orders:
            return jsonify({"message": "Keine Bestellungen übergeben."}), 200
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
        PreOrdersService.create_update_bulk_preorders(orders, g.user_group, g.user_id)
    except ValueError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Datum nicht valide",
                description="Das Datum einer der Bestellungen ist nicht valide.",
                details=str(err),
            )
        )
    except PersonNotPartOfGroup as err:
        abort_with_err(
            ErrMsg(
                status_code=401,
                title="Person gehört nicht zur Gruppe",
                description="Eine der Personen gehört nicht zur Gruppe.",
                details=str(err),
            )
        )
    except PersonNotPartOfLocation as err:
        abort_with_err(
            ErrMsg(
                status_code=401,
                title="Person gehört nicht zum Standort",
                description="Eine der Personen gehört nicht zum Standort.",
                details=str(err),
            )
        )
    return jsonify({"message": "Bestellungen erfolgreich erstellt"}), 201


@pre_orders_routes.post("/api/pre-orders/<uuid:user_id>")
@login_required(
    groups=[UserGroup.verwaltung, UserGroup.standortleitung, UserGroup.gruppenleitung]
)
@swag_from(
    {
        "tags": ["pre_orders"],
        "parameters": [
            {
                "in": "path",
                "name": "user_id",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
            },
            {
                "in": "body",
                "name": "body",
                "schema": {
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
                        "nothing": {"type": "boolean"},
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
        ],
        "responses": {
            201: {
                "description": "Order created",
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
def create_preorder_user(user_id: UUID):
    """
    Create a new preorder for an user
    """
    try:
        preorder = PreOrdersPostPutBody().load(request.json)
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
        PreOrdersService.create_preorder_user(preorder, g.user_id)
    except ValueError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Datum der Bestellung nicht valide",
                description="Das Datum der Bestellung ist nicht valide.",
                details=str(err),
            )
        )
    except WrongUserError as err:
        abort_with_err(
            ErrMsg(
                status_code=401,
                title="Falscher Benutzer",
                description="Der Benutzer hat keine Berechtigung für diese Aktion.",
                details=str(err),
            )
        )
    return jsonify({"message": "Bestellung erfolgreich aufgenommen."}), 201


@pre_orders_routes.put("/api/pre-orders/<int:preorder_id>")
@login_required(
    groups=[UserGroup.verwaltung, UserGroup.standortleitung, UserGroup.gruppenleitung]
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
                "schema": {
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
                        "nothing": {"type": "boolean"},
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
        ],
        "responses": {
            200: {
                "description": "Order updated",
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
def update_preorder_user(preorder_id: UUID):
    """
    Update an existing preorder for an user
    """
    try:
        preorder = PreOrdersPostPutBody().load(request.json)
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
        PreOrdersService.update_preorder_user(preorder, preorder_id, g.user_id)
    except ValueError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Datum der Bestellung nicht valide",
                description="Das Datum der Bestellung ist nicht valide.",
                details=str(err),
            )
        )
    except WrongUserError as err:
        abort_with_err(
            ErrMsg(
                status_code=401,
                title="Falscher Benutzer",
                description="Der Benutzer hat keine Berechtigung für diese Aktion.",
                details=str(err),
            )
        )
    return jsonify({"message": "Bestellung erfolgreich aktualisiert."}), 200


@pre_orders_routes.delete("/api/pre-orders/<uuid:preorder_id>")
@login_required(
    groups=[UserGroup.verwaltung, UserGroup.standortleitung, UserGroup.gruppenleitung]
)
@swag_from(
    {
        "tags": ["pre_orders"],
        "parameters": [
            {
                "in": "path",
                "name": "preorder_id",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
            },
        ],
        "responses": {
            200: {
                "description": "Order deleted",
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
def delete_preorder_user(preorder_id: UUID):
    """
    Delete an existing preorder for an user
    """
    try:
        PreOrdersService.delete_preorder_user(preorder_id, g.user_id)
    except WrongUserError as err:
        abort_with_err(
            ErrMsg(
                status_code=401,
                title="Falscher Benutzer",
                description="Der Benutzer hat keine Berechtigung für diese Aktion.",
                details=str(err),
            )
        )
    return jsonify({"message": "Bestellung erfolgreich gelöscht."}), 200
