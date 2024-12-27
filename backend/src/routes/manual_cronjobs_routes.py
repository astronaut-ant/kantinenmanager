from flask import Blueprint, jsonify
from flasgger import swag_from
from flask import current_app as app

from src.utils.cronjobs import push_orders_to_next_table
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err
from src.models.user import UserGroup


manual_cronjobs_routes = Blueprint("manual_cronjobs_routes", __name__)


@manual_cronjobs_routes.get("/api/batch/pre-to-daily-to-old-order")
@login_required(groups=[UserGroup.kuechenpersonal], disabled=True)
@swag_from(
    {
        "tags": ["manual_cronjobs"],
        "responses": {
            200: {
                "description": "Converts pre orders to daily orders and daily orders to old orders",
                "schema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"},
                    },
                },
            },
            404: {"description": "Bad request"},
        },
    }
)
def write_pre_to_daily_to_old_order():
    """
    Converts pre orders to daily orders and daily orders to old orders
    """

    try:
        push_orders_to_next_table(app)
    except Exception as e:
        abort_with_err(
            ErrMsg(
                status_code=500,
                title="Internal Server Error",
                description="Bestellungen konnten nicht verschoben werden.",
                details=str(e),
            )
        )

    return jsonify({"message": "Bestellungen erfolgreich verschoben."}), 200
