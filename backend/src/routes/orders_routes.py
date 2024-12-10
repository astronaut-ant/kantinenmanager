from pprint import pprint
from uuid import UUID
from marshmallow import ValidationError, Schema, fields
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err
from flask import Blueprint, jsonify, request, g
from flasgger import swag_from
from src.models.user import UserGroup
from src.models.maindish import MainDish
from src.services.orders_service import (
    OrdersFilters,
    OrdersService,
    PersonNotPartOfGroup,
    PersonNotPartOfLocation,
    WrongUserError,
    WrongLocationError,
)


orders_routes = Blueprint("orders_routes", __name__)


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


@orders_routes.get("/api/pre-orders")
@login_required()  # TODO Permissions
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

    orders = OrdersService.get_pre_orders(filters)
    return jsonify([order.to_dict() for order in orders]), 200


@orders_routes.get("/api/pre-orders/<int:preorder_id>")
@login_required()  # TODO Permissions
@swag_from(
    {
        "tags": ["orders"],
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

    order = OrdersService.get_pre_order_by_id(preorder_id)
    if order is None:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Bestellung nicht gefunden",
                description=f"Bestellung mit ID {preorder_id} nicht gefunden.",
            )
        )

    return jsonify(order.to_dict()), 200


@orders_routes.get("/api/pre-orders/by-group-leader/<uuid:person_id>")
@login_required(groups=[UserGroup.gruppenleitung])
@swag_from(
    {
        "tags": ["orders"],
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
def get_orders_by_group_leader(person_id: UUID):
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


@orders_routes.get("/api/daily-orders")
@login_required()  # TODO Permissions
@swag_from(
    {
        "tags": ["orders"],
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


@orders_routes.get("/api/daily-orders/<int:daily_order_id>")
@login_required()  # TODO Permissions
@swag_from(
    {
        "tags": ["orders"],
    }
)
def get_daily_orders_for_person(daily_order_id: int):
    """
    Get daily orders for a person
    """
    abort_with_err(
        ErrMsg(
            status_code=501,
            title="Not implemented",
            description="This endpoint is not implemented yet.",
        )
    )


class OrdersPostPutBody(Schema):
    """
    Schema for the POST and PUT /api/locations endpoint
    """

    person_id = fields.UUID(required=True)
    location_id = fields.UUID(required=True)
    date = fields.Date(required=True)  # ISO 8601-formatted date string
    main_dish = fields.Enum(MainDish, required=False, default=None)
    salad_option = fields.Boolean(required=False, default=False)


@orders_routes.post("/api/orders")
@login_required(groups=[UserGroup.gruppenleitung])
@swag_from(
    {
        "tags": ["orders"],
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
        orders = OrdersPostPutBody(many=True).load(request.json)
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
        OrdersService.create_update_bulk_preorders(orders, g.user_group, g.user_id)
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


@orders_routes.post("/api/orders/<uuid:user_id>")
@login_required(
    groups=[UserGroup.verwaltung, UserGroup.standortleitung, UserGroup.gruppenleitung]
)
@swag_from(
    {
        "tags": ["orders"],
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
        preorder = OrdersPostPutBody().load(request.json)
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
        OrdersService.create_preorder_user(preorder, g.user_id)
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


@orders_routes.put("/api/orders/<int:preorder_id>")
@login_required(
    groups=[UserGroup.verwaltung, UserGroup.standortleitung, UserGroup.gruppenleitung]
)
@swag_from(
    {
        "tags": ["orders"],
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
def update_preorder_user(preorder_id: UUID):
    """
    Update an existing preorder for an user
    """
    try:
        preorder = OrdersPostPutBody().load(request.json)
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
        OrdersService.update_preorder_user(preorder, preorder_id, g.user_id)
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
    return jsonify({"message": "Bestellung erfolgreich aktualisiert."}), 201


@orders_routes.delete("/api/orders/<uuid:preorder_id>")
@login_required(
    groups=[UserGroup.verwaltung, UserGroup.standortleitung, UserGroup.gruppenleitung]
)
@swag_from(
    {
        "tags": ["orders"],
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
        OrdersService.delete_preorder_user(preorder_id, g.user_id)
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


# QR-Code scannen
@orders_routes.get("/api/orders/daily/<uuid:person_id>")
@login_required(groups=[UserGroup.kuechenpersonal])
@swag_from(
    {
        "tags": ["orders"],
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
        daily_order = OrdersService.get_daily_order(person_id, g.user_id)
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


@orders_routes.put("/api/orders/daily/<uuid:daily_order_id>")
@login_required(groups=[UserGroup.kuechenpersonal])
@swag_from(
    {
        "tags": ["orders"],
        "parameters": [
            {
                "in": "path",
                "name": "daily_order_id",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
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
def update_daily_order(daily_order_id: UUID):
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
        OrdersService.update_daily_order(daily_order_id, handed_out, g.user_id)
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
