from marshmallow import ValidationError
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err
from flask import Blueprint, jsonify, request, g
from flasgger import swag_from
from datetime import datetime
from src.models.user import UserGroup
from src.repositories.orders_repository import OrdersFilters
from src.services.reports_service import (
    ReportsService,
    OrderType,
    LocationDoesNotExist,
    AccessDeniedError,
)

reports_routes = Blueprint("reports_routes", __name__)


@reports_routes.get("/api/reports")
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
                "description": "Filter by location ID",
                "required": True,
                "schema": {"type": "string", "format": "uuid"},
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

    d_str = request.args.get("date")
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
            date=datetime.strptime(d_str, "%Y-%m-%d").date() if d_str else None,
            date_start=datetime.strptime(ds_str, "%Y-%m-%d").date() if ds_str else None,
            date_end=datetime.strptime(de_str, "%Y-%m-%d").date() if de_str else None,
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
        return ReportsService.get_printed_report(
            filters=filters,
            location_id=location_id,
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
