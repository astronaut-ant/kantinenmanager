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
    OrderAlreadyExistsForPersonAndDate,
    PersonNotPartOfGroup,
    PersonNotPartOfLocation,
    WrongUserError,
)


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
        quesry_params = OrdersGetQuery().load(request.args)
        filters = OrdersFilters(**quesry_params)
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

    orders = OrdersService.get_orders(filters)
    pprint(orders)

    return []


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
            "Order": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "person_id": {"type": "string"},
                    "location_id": {"type": "string"},
                    "date": {"type": "string", "format": "date"},
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
def create_orders_employees():
    """
    Bulk create preorders for employees
    """
    try:
        orders = OrdersPostPutBody(many=True).load(request.json)
        if not orders:
            return jsonify({"message": "Keine neuen Bestellungen"}), 200
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
        OrdersService.create_bulk_orders(orders, g.user_group, g.user_id)
    except ValueError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Datum liegt in der Vergangenheit",
                description="Das Datum liegt in der Vergangenheit.",
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
    except OrderAlreadyExistsForPersonAndDate as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Bestellung existiert bereits",
                description="Eine Bestellung für eine der Personen existiert bereits für diesen Tag.",
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


@orders_routes.put("/api/orders")
@login_required(groups=[UserGroup.gruppenleitung])
@swag_from(
    {
        "tags": ["orders"],
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
                "description": "Order changed",
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
def update_orders_employees():
    """
    Bulk update preorders for employees
    """
    try:
        orders = OrdersPostPutBody(many=True).load(request.json)
        if not orders:
            return jsonify({"message": "Keine übermittelten Bestellungen"}), 200
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
        OrdersService.create_bulk_orders(orders, g.user_group, g.user_id)
    except ValueError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Datum liegt in der Vergangenheit",
                description="Das Datum liegt in der Vergangenheit.",
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
    except OrderAlreadyExistsForPersonAndDate as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Bestellung existiert bereits",
                description="Eine Bestellung für eine der Personen existiert bereits für diesen Tag.",
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
                "description": "Order changed",
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
def create_order_user(user_id: UUID):
    """
    Create a new preorder for an user
    """
    try:
        order = OrdersPostPutBody().load(request.json)
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
        OrdersService.create_order_user(order, g.user_group, g.user_id)
    except ValueError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Datum liegt in der Vergangenheit",
                description="Das Datum liegt in der Vergangenheit.",
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
    except OrderAlreadyExistsForPersonAndDate as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Bestellung existiert bereits",
                description="Eine Bestellung für eine der Personen existiert bereits für diesen Tag.",
                details=str(err),
            )
        )
    return jsonify({"message": "Bestellung erfolgreich erstellt"}), 201


@orders_routes.put("/api/orders/<uuid:user_id>")
@login_required(
    groups=[UserGroup.verwaltung, UserGroup.standortleitung, UserGroup.gruppenleitung]
)
# swag_from()
def update_order_user(user_id: UUID):
    """
    Update a preorder for an user
    """
    #
    return jsonify({"message": "Bestellung erfolgreich geändert"}), 201
