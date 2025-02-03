from marshmallow import ValidationError
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err
from flask import Blueprint, request, g
from flasgger import swag_from
from datetime import datetime
from src.models.user import UserGroup
from src.repositories.orders_repository import OrdersFilters
from src.schemas.pre_orders_schemas import OrdersFilterSchema
from src.services.reports_service import (
    ReportsService,
    LocationDoesNotExist,
    AccessDeniedError,
)

reports_routes = Blueprint("reports_routes", __name__)


@reports_routes.get("/api/reports/locations")
@login_required(
    groups=[UserGroup.verwaltung, UserGroup.standortleitung, UserGroup.kuechenpersonal]
)
@swag_from(
    {
        "tags": ["reports"],
        "parameters": [
            {
                "in": "query",
                "name": "location_id",
                "description": "choose the location for the invoice",
                "required": True,
                "schema": {
                    "type": "string",
                    "format": "uuid",
                },
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
                "description": "Report generated successfully",
                "content": {
                    "application/pdf": {
                        "schema": {"type": "string", "format": "binary"}
                    }
                },
            },
            400: {"description": "Validation error"},
        },
    }
)
def get_report():
    """Get reports for orders filtered by date and location"""

    ds_str = request.args.get("date-start")
    de_str = request.args.get("date-end")

    try:
        location_id = request.args.get("location_id")
        if not location_id:
            abort_with_err(
                ErrMsg(
                    status_code=400,
                    title="Validierungsfehler",
                    description="Es wurde kein Standort übergeben",
                    details="Die Abfrage erfordert mindestens einen Standort.",
                )
            )

        filters = OrdersFilters(
            date_start=datetime.strptime(ds_str, "%Y-%m-%d").date() if ds_str else None,
            date_end=datetime.strptime(de_str, "%Y-%m-%d").date() if de_str else None,
            location_id=location_id,
        )

    except ValidationError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Format der Daten in der Query nicht valide",
                details=err.messages,
            )
        )

    try:
        return ReportsService.get_location_report(
            filters=filters,
            user_id=g.user_id,
            user_group=g.user_group,
        )

    except ValueError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Es wurde kein Standort übergeben",
                details=str(err),
            )
        )
    except LocationDoesNotExist as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Einer der Standorte existiert nicht",
                description="Einer der Standorte existiert nicht in der Datenbank mit gegebener ID",
            )
        )
    except AccessDeniedError as err:
        abort_with_err(
            ErrMsg(
                status_code=403,
                title="Zugriff verweigert",
                description=f"Nutzer:in {g.user_id} hat keine Berechtigung, einen der Standort zu sehen",
            )
        )


@reports_routes.get("/api/invoices")
@login_required(groups=[UserGroup.verwaltung], disabled=True)
@swag_from(
    {
        "tags": ["reports"],
        "parameters": [
            {
                "in": "query",
                "name": "location-id",
                "description": "Choose the location for the invoice",
                "required": False,
                "schema": {
                    "type": "string",
                    "format": "uuid",
                },
            },
            {
                "in": "query",
                "name": "group-id",
                "description": "Choose the group for the invoice",
                "required": False,
                "schema": {
                    "type": "string",
                    "format": "uuid",
                },
            },
            {
                "in": "query",
                "name": "person-id",
                "description": "Choose the person for the invoice",
                "required": False,
                "schema": {
                    "type": "string",
                    "format": "uuid",
                },
            },
            {
                "in": "query",
                "name": "date-start",
                "description": "Insert the start date for the invoice",
                "required": True,
                "schema": {"type": "string", "format": "date"},
                "example": "2024-12-08",
            },
            {
                "in": "query",
                "name": "date-end",
                "description": "Insert the end date for the invoice",
                "required": True,
                "schema": {"type": "string", "format": "date"},
                "example": "2024-12-08",
            },
        ],
        "responses": {
            200: {
                "description": "Report generated successfully",
                "content": {
                    "application/pdf": {
                        "schema": {"type": "string", "format": "binary"}
                    }
                },
            },
            400: {"description": "Validation error"},
        },
    }
)
def get_invoices():
    """Get invoices for orders filtered by date and person"""

    try:
        query_params = OrdersFilterSchema().load(request.args)
        filters = OrdersFilters(**query_params)

        if not filters.person_id and not filters.group_id and not filters.location_id:
            abort_with_err(
                ErrMsg(
                    status_code=400,
                    title="Validierungsfehler",
                    description="Es wurde keine UUID übergeben",
                    details="Die Abfrage erfordert die UUID eines Standorts, einer Gruppe oder einer Person.",
                )
            )
    except ValidationError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Format der Daten in der Query nicht valide",
                details=err.messages,
            )
        )

    try:
        return ReportsService.get_printed_invoice(filters=filters)
    except BadValueError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Es muss eine ID übergeben werden. (Standort, Gruppe oder Person)",
                details=err.messages,
            )
        )
