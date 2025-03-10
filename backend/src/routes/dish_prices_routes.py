from datetime import datetime, time
from flask import Blueprint, request
from flasgger import swag_from
from marshmallow import ValidationError

from src.utils.exceptions import BadValueError, NotFoundError
from src.utils.error import ErrMsg, abort_with_err
from src.services.dish_prices_service import DishPricesService
from src.schemas.dish_prices_schemas import DishPriceBaseSchema, DishPriceFullSchema
from src.models.user import UserGroup
from src.utils.auth_utils import login_required


dish_prices_routes = Blueprint("dish_prices_routes", __name__)


@dish_prices_routes.get("/api/dish_prices")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["dish_price"],
        "responses": {
            200: {
                "description": "List of all dish prices",
                "schema": {"type": "array", "items": DishPriceFullSchema},
            }
        },
    }
)
def get_dish_prices():
    """Get all dish prices"""

    prices = DishPricesService.get_prices()

    return DishPriceFullSchema(many=True).dump(prices)


@dish_prices_routes.get("/api/dish_prices/<date>")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["dish_price"],
        "parameters": [
            {
                "in": "path",
                "name": "date",
                "type": "string",
                "format": "date",
                "required": True,
                "example": "2025-01-01",
                "description": "The date of the dish price to retrieve",
            }
        ],
        "responses": {
            200: {
                "description": "Dish price valid at date",
                "schema": DishPriceFullSchema,
            }
        },
    }
)
def get_dish_price_by_date(date: datetime):
    """Get a dish price valid at a specific date

    Get the dish price that was or will be valid at the specified date.
    ---
    """

    try:
        parsed_date = DishPriceBaseSchema(only=("date",)).load({"date": date})
        dt = datetime.combine(
            parsed_date.get("date"), time(0, 0)
        )  # convert date to datetime
    except ValidationError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Ungültiges Datum",
                details=err.messages,
            )
        )

    price = DishPricesService.get_price_valid_at_date(dt)

    if price is None:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Preis existiert nicht",
                description="Es existiert kein Preis für das angegebene Datum",
            )
        )

    return DishPriceFullSchema().dump(price)


@dish_prices_routes.get("/api/dish_prices/current")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["dish_price"],
        "responses": {
            200: {
                "description": "Today's dish price",
                "schema": DishPriceFullSchema,
            }
        },
    }
)
def get_current_dish_price():
    """Get the current dish price

    Get the price that is valid today.
    ---
    """

    price = DishPricesService.get_current_price()

    if price is None:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Preis existiert nicht",
                description="Es existiert kein Preis.",
            )
        )

    return DishPriceFullSchema().dump(price)


@dish_prices_routes.post("/api/dish_prices")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["dish_price"],
        "parameters": [
            {
                "in": "body",
                "name": "body",
                "required": True,
                "schema": DishPriceFullSchema,
            }
        ],
        "responses": {
            201: {
                "description": "Newly created dish price",
                "schema": DishPriceFullSchema,
            }
        },
    }
)
def create_dish_price():
    """Create a new dish price"""

    try:
        body = DishPriceFullSchema().load(request.json)
    except ValidationError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Format der Daten im Request-Body nicht valide",
                details=err.messages,
            )
        )

    dt = datetime.combine(body.get("date"), time(0, 0))

    try:
        price = DishPricesService.create_price(
            date=dt,
            main_dish_price=body.get("main_dish_price"),
            salad_price=body.get("salad_price"),
            prepayment=body.get("prepayment"),
        )
    except BadValueError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Fehler beim Erstellen",
                description=str(err),
            )
        )

    return DishPriceFullSchema().dump(price), 201


@dish_prices_routes.put("/api/dish_prices/<date>")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["dish_price"],
        "parameters": [
            {
                "in": "path",
                "name": "date",
                "type": "string",
                "format": "date",
                "required": True,
                "example": "2025-01-01",
                "description": "The starting date of the dish price to update",
            },
            {
                "in": "body",
                "name": "body",
                "required": True,
                "schema": DishPriceFullSchema,
            },
        ],
        "responses": {
            200: {
                "description": "Updated dish price",
                "schema": DishPriceFullSchema,
            }
        },
    }
)
def update_dish_price(date: datetime):
    """Update an existing dish price"""

    try:
        parsed_date = DishPriceBaseSchema(only=("date",)).load({"date": date})
        dt = datetime.combine(
            parsed_date.get("date"), time(0, 0)
        )  # convert date to datetime
    except ValidationError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Ungültiges Datum",
                details=err.messages,
            )
        )

    try:
        body = DishPriceFullSchema().load(request.json)
    except ValidationError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Format der Daten im Request-Body nicht valide",
                details=err.messages,
            )
        )

    new_dt = datetime.combine(body.get("date"), time(0, 0))

    try:
        price = DishPricesService.update_price(
            old_date=dt,
            date=new_dt,
            main_dish_price=body.get("main_dish_price"),
            salad_price=body.get("salad_price"),
            prepayment=body.get("prepayment"),
        )
    except BadValueError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Fehler beim Aktualisieren",
                description=str(err),
            )
        )
    except NotFoundError as err:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Preis existiert nicht",
                description=str(err),
            )
        )

    return DishPriceFullSchema().dump(price)


@dish_prices_routes.delete("/api/dish_prices/<date>")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["dish_price"],
        "parameters": [
            {
                "in": "path",
                "name": "date",
                "type": "string",
                "format": "date",
                "required": True,
                "example": "2025-01-01",
                "description": "The starting date of the dish price to delete",
            }
        ],
        "responses": {204: {"description": "Delete a dish price"}},
    }
)
def delete_dish_price(date: datetime):
    """Delete a dish price"""

    try:
        parsed_date = DishPriceBaseSchema(only=("date",)).load({"date": date})
        dt = datetime.combine(
            parsed_date.get("date"), time(0, 0)
        )  # convert date to datetime
    except ValidationError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Ungültiges Datum",
                details=err.messages,
            )
        )

    try:
        DishPricesService.delete_price(dt)
    except NotFoundError as err:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Preis existiert nicht",
                description=str(err),
            )
        )

    return "", 204
