"""Routes for health checks."""

from datetime import datetime
from flask import Blueprint, current_app as app, redirect
from flasgger import swag_from

from src.database import check_db_connection

from src.utils.cronjobs import push_orders_to_next_table as push


general_routes = Blueprint("general_routes", __name__)


@general_routes.get("/")
def index():
    return redirect("/api/health", code=302)


@general_routes.get("/api/health")
@swag_from(
    {
        "tags": ["general"],
        "responses": {
            200: {
                "description": "Health check",
                "schema": {
                    "type": "object",
                    "properties": {
                        "health_status": {"type": "string"},
                        "database": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string"},
                            },
                        },
                        "uptime": {"type": "string"},
                    },
                },
            }
        },
    }
)
def health():
    """Health check endpoint for the API.
    Checks the application's uptime and the database connection.
    """

    db_health = check_db_connection()
    start_time = app.config.get("APP_START_TIME")

    return {
        "health_status": "OK" if db_health else "error",
        "database": {
            "status": "OK" if db_health else "error",
        },
        "uptime": str(datetime.now() - start_time),
    }


# Test route for testing cronjobs
@general_routes.get("/api/push")
def push():
    push()
    return "Success"
