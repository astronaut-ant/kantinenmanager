from uuid import UUID
from marshmallow import ValidationError, Schema, fields
from marshmallow.validate import Length
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err
from src.models.user import UserGroup
from src.services.employees_service import (
    EmployeesService,
    EmployeeAlreadyExistsError,
    GroupDoesNotExistError,
    NameNotAppropriateError,
    FileNotProcessableError,
)
from flask import Blueprint, jsonify, request, g
from flasgger import swag_from
import csv, re

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
                    "employee_number": {"type": "integer"},
                    "group_id": {
                        "type": "string",
                        "example": "123e4567-e89b-12d3-a456-426614174000",
                    },
                    "created": {"type": "string", "format": "date-time"},
                },
            }
        },
        "parameters": [
            {
                "in": "query",
                "name": "first_name",
                "required": False,
                "schema": {"type": "string"},
            },
            {
                "in": "query",
                "name": "last_name",
                "required": False,
                "schema": {"type": "string"},
            },
            {
                "in": "query",
                "name": "employee_number",
                "required": False,
                "schema": {"type": "string"},
            },
            {
                "in": "query",
                "name": "group_name",
                "required": False,
                "schema": {"type": "string"},
            },
            {
                "in": "query",
                "name": "group_id",
                "required": False,
                "schema": {"type": "string"},
            },
        ],
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
# get employee by name with request.args.get
def get_employees():
    """Get all employees that the current user has access to optionally filtered by name
    Get a list of employees (optionally filtered by name)

    Authentication: required
    Authorization: Verwaltung, Standortleitung, Gruppenleitung, Küchenpersonal
    ---
    """
    first_name = request.args.get("first_name")
    last_name = request.args.get("last_name")
    group_name = request.args.get("group_name")
    group_id = request.args.get("group_id")
    employee_number = request.args.get("employee_number")
    employees = EmployeesService.get_employees(
        g.user_group,
        g.user_id,
        first_name=first_name,
        last_name=last_name,
        group_name=group_name,
        group_id=group_id,
        employee_number=employee_number,
    )

    employees_dict = [employee.to_dict() for employee in employees]

    return jsonify(employees_dict)


@employees_routes.get("/api/employees/<uuid:employee_id>")
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
        "tags": ["employees"],
        "parameters": [
            {
                "in": "path",
                "name": "employee_id",
                "required": True,
                "schema": {"type": "string"},
            }
        ],
        "responses": {
            200: {
                "description": "Returns the employee with the given ID",
                "schema": {"$ref": "#/definitions/Employee"},
            },
            404: {"description": "User not found"},
        },
    }
)
def get_employee_by_id(employee_id: UUID):
    """Get an employee by ID
    Get an employee by ID

    Authentication: required
    Authorization: Verwaltung, Standortleitung, Gruppenleitung, Kuechenpersonal
    ---
    """

    user_group = g.user_group
    user_id = g.user_id
    employee = EmployeesService.get_employee_by_id(employee_id, user_group, user_id)
    if employee is None:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Mitarbeiter nicht gefunden",
                description="Es wurde kein Mitarbeiter mit dieser ID gefunden",
            )
        )

    return jsonify(employee.to_dict())


class EmployeesPostBody(Schema):
    """
    Schema for the POST /api/employees endpoint
    """

    first_name = fields.Str(required=True, validate=Length(min=1, max=64))
    last_name = fields.Str(required=True, validate=Length(min=1, max=64))
    employee_number = fields.Int(required=True)
    group_name = fields.Str(required=True, validate=Length(min=1, max=256))
    location_name = fields.Str(required=True, validate=Length(min=1, max=256))


@employees_routes.post("/api/employees")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["employees"],
        "parameters": [
            {
                "in": "body",
                "name": "body",
                "schema": {
                    "type": "object",
                    "properties": {
                        "first_name": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 64,
                        },
                        "last_name": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 64,
                        },
                        "employee_number": {
                            "type": "integer",
                        },
                        "group_name": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 256,
                        },
                        "location_name": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 256,
                        },
                    },
                },
            }
        ],
        "responses": {
            200: {
                "description": "Returns the ID of the newly created employee",
                "schema": {
                    "type": "string",
                    "properties": {
                        "id": {
                            "type": "string",
                            "example": "123e4567-e89b-12d3-a456-426614174000",
                        }
                    },
                },
            },
            400: {"description": "Invalid input"},
        },
    }
)
def create_user():
    """Create a new employee
    Create a new employee
    ---
    """

    try:
        body = EmployeesPostBody().load(request.json)
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
        id = EmployeesService.create_employee(**body)
    except EmployeeAlreadyExistsError:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Kunden-Nr. bereits vergeben",
                description="Die Kunden-Nr. ist bereits vergeben",
            )
        )

    return jsonify({"id": id})


@employees_routes.post("/api/employees_csv")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["employees"],
        "parameters": [
            {
                "in": "path",
                "name": "employee_csv",
                "required": False,
                "schema": {"type": "string"},
            },
            {
                "name": "file",
                "in": "formData",
                "type": "file",
                "required": True,
                "description": "Die CSV-Datei, die hochgeladen werden soll.",
            },
        ],
        "responses": {
            200: {
                "description": "File read in successfully",
                "schema": {"$ref": "#/definitions/Employee"},
            },
            400: {"description": "Bad Request: No File in Request"},
            404: {"description": "Wrong file Format: Need CSV"},
        },
    }
)
def csv_create():
    """Create Employees contained in a CSV File
    Create Employees contained in a CSV File
    ---
    """
    if "file" not in request.files:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Kein Dateiteil in der Anfrage",
                description="In der Anfrage gab es keinen Dateibereich",
            )
        )

    file = request.files["file"]

    if file.filename == "":
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Keine Datei ausgewählt",
                description="Es wurde keine Datei hochgeladen",
            )
        )

    file.stream.seek(0)
    if not ("." in file.filename and file.filename.rsplit(".", 1)[1].lower() == "csv"):
        abort_with_err(
            ErrMsg(
                status_code=415,
                title="Falsches Dateiformat",
                description="Es werden nur .csv Dateien zugelassen",
            )
        )
    try:
        EmployeesService.bulk_create_employees(file)
    except EmployeeAlreadyExistsError:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Ein Nutzer existiert bereits",
                description="Einer der Nutzer existiert bereits",
            )
        )
    except GroupDoesNotExistError:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Gruppe wurde nicht gefunden",
                description="Die Gruppe zu mindestens einem der Benutzer existiert nicht",
            )
        )
    except NameNotAppropriateError:
        abort_with_err(
            ErrMsg(
                status_code=422,
                title="Ein Name ist nicht verarbeitbar",
                description="Der Vor-/Nachname ist entweder zu lang, oder Namen können nicht getrennt werden",
            )
        )
    except FileNotProcessableError:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Datei hat unlesbares Format",
                description="Datei muss utf-8 mit , oder iso-8859-1 mit ; sein",
            )
        )

    return jsonify({"message": "Datei wurde erfolgreich eingelesen"}), 200


class EmployeeUpdateBody(Schema):
    """
    Schema for the PUT /api/employees endpoint
    """

    first_name = fields.Str(required=True, validate=Length(min=1, max=64))
    last_name = fields.Str(required=True, validate=Length(min=1, max=64))
    employee_number = fields.Int(required=True)
    group_name = fields.Str(required=True, validate=Length(min=1, max=256))
    location_name = fields.Str(required=True, validate=Length(min=1, max=256))


@employees_routes.put("/api/employees/<uuid:employee_id>")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["employees"],
        "parameters": [
            {
                "in": "path",
                "name": "employee_id",
                "required": True,
                "schema": {"type": "string"},
            },
            {
                "in": "body",
                "name": "body",
                "schema": {
                    "type": "object",
                    "properties": {
                        "first_name": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 64,
                        },
                        "last_name": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 64,
                        },
                        "employee_number": {"type": "integer"},
                        "group_name": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 256,
                        },
                        "location_name": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 256,
                        },
                    },
                },
            },
        ],
        "responses": {
            200: {
                "description": "Returns the updated employee",
                "schema": {"$ref": "#/definitions/Employee"},
            },
            400: {"description": "Validation error or employee_number already exists"},
            404: {"description": "Employee not found"},
        },
    }
)
def update_employee(employee_id: UUID):
    """Update an employee
    Update an employee identified by ID
    ---
    """

    try:
        body = EmployeeUpdateBody().load(request.json)
    except ValidationError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Format der Daten im Request-Body nicht valide",
                details=err.messages,
            )
        )
    employee = EmployeesService.get_employee_by_id(employee_id, g.user_group, g.user_id)
    if employee is None:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Mitarbeiter:in nicht gefunden",
                description="Es wurde kein:e Mitarbeiter:in mit dieser ID gefunden",
            )
        )

    try:
        EmployeesService.update_employee(employee, **body)
    except EmployeeAlreadyExistsError:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Mitarbeiterummer bereits vergeben",
                description="Diese Mitarbeiternummer ist bereits vergeben",
            )
        )

    return jsonify(employee.to_dict())


@employees_routes.delete("/api/employees/<uuid:employee_id>")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["employees"],
        "parameters": [
            {
                "in": "path",
                "name": "employee_id",
                "required": True,
                "schema": {"type": "string"},
            }
        ],
        "responses": {
            200: {
                "description": "Employee successfully deleted",
                "schema": {
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                },
            },
            404: {"description": "Employee not found"},
        },
    }
)
def delete_employee(employee_id: UUID):
    """Delete an employee
    Delete an employee by ID

    Authentication: required
    Authorization: Verwaltung
    ---
    """
    employee = EmployeesService.get_employee_by_id(employee_id, g.user_group, g.user_id)
    if employee is None:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Mitarbeiter:in nicht gefunden",
                description="Es wurde kein:e Mitarbeiter:in mit dieser ID gefunden",
            )
        )

    EmployeesService.delete_employee(employee)
    return jsonify({"message": "Mitarbeiter:in erfolgreich gelöscht"})
