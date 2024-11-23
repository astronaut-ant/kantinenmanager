from uuid import UUID
from marshmallow import ValidationError, Schema, fields
from marshmallow.validate import Length
from src.utils.auth_utils import login_required
from src.models.user import UserGroup
from src.services.employees_service import EmployeesService
from flask import Blueprint, jsonify, request, g
from flasgger import swag_from

employees_routes = Blueprint("employees_routes", __name__)


# Bei jedem GET Request (siehe HTTP) auf /api/users wird die get_employees Funktion aufgerufen und alle Emplyoees, die Scope des Nutzers sind zurückgegeben
@employees_routes.get("/api/employees")
@login_required(
    groups=[
        UserGroup.verwaltung,
        UserGroup.standortleitung,
        UserGroup.gruppenleitung,
    ]
)
@swag_from(
    {
        "tags": ["employees"],
        "definitions": {
            "Employee": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "example": "123e4567-e89b-12d3-a456-426614174000",
                    },
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "employee_number": {
                        "type": "integer"
                    },  # what if employee has no number?
                    "group_id": {
                        "type": "string",
                        "example": "123e4567-e89b-12d3-a456-426614174000",
                    },
                    "created": {"type": "string", "format": "date-time"},
                },
            }
        },
        "responses": {
            200: {
                "description": "Returns a list of the employees belonging to the scope of the user",
                "schema": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Employee"},
                },
            }
        },
    }
)
def get_employees():
    """Get all employees that the current user has access to
    Get a list of employees

    Authentication: required
    Authorization: Verwaltung, Standortleitung, Gruppenleitung, Küchenpersonal
    ---
    """
    user_group = g.user_group
    user_id = g.user_id
    employees = EmployeesService.get_employees(user_group, user_id)

    return jsonify(employees)
