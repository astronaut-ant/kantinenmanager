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

    employees_dict = [employee.to_dict() for employee in employees]

    return jsonify(employees_dict)


@employees_routes.get("/api/employees/<uuid:employee_id>")
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
    """Get a employee by ID
    Get a employee by ID

    Authentication: required
    Authorization: Verwaltung
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


# TODO: def get_employee_by_id_kitchen(employee_id: UUID):


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
                title="Nutzername bereits vergeben",
                description="Der Nutzername ist bereits vergeben",
            )
        )

    return jsonify({"id": id})


@employees_routes.post("/api/employees_csv")
@login_required(groups=[UserGroup.verwaltung])
# @swag_from kommmt wenn mein GitHub Copilot zugelassen wurde, das hilft einem doch dabei richtig?
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

    if "." in file.filename and file.filename.rsplit(".", 1)[1].lower() == "csv":
        abort_with_err(
            ErrMsg(
                status_code=401,
                title="Falsches Dateiformat",
                description="Es werden nur .csv Dateien zugelassen",
            )
        )

    try:
        try:
            file.stream.seek(0)
            reader = csv.DictReader(file.stream.read().decode("utf-8").splitlines())
        except UnicodeDecodeError:
            file.stream.seek(0)
            reader = csv.DictReader(
                file.stream.read().decode("iso-8859-1").splitlines()
            )
    except ValueError:
        try:
            file.stream.seek(0)
            reader = csv.DictReader(
                file.stream.read().decode("utf-8").splitlines(), delimiter=";"
            )
        except UnicodeDecodeError:
            file.stream.seek(0)
            reader = csv.DictReader(
                file.stream.read().decode("iso-8859-1").splitlines(), delimiter=";"
            )
    except UnicodeDecodeError:
        abort_with_err(
            ErrMsg(
                status_code=402,
                title="Unlesbare Datei",
                description="Datei kann nicht mit utf-8 oder iso-8859-1 decodiert werden",
            )
        )

    for row in reader:
        if (
            not row.get("Kunden-Nr.")
            or not row.get("Kürzel")
            or not row.get("Bereich")
            or not row.get("Gruppe-Nr.")
            or not row.get("Gruppen-Name 1")
            or not row.get("Gruppen-Name 2")
        ):
            abort_with_err(
                ErrMsg(
                    status_code=403,
                    title="Falsche Daten in CSV Datei",
                    description="Die Daten in der CSV entsprechen nicht der normalen Vorlage",
                )
            )

        match = re.match(r"([A-Z][a-z]+)([A-Z][a-z][1-9]+)", row["Kürzel"])
        if match:
            firstname = match.group(1)
            lastname = match.group(2)
        else:
            continue

        try:
            EmployeesService.create_employee(
                first_name=firstname,
                last_name=lastname,
                employee_number=row["Kunden-Nr."],
                group_name=row["Gruppen-Name 1"],
                location_name=row["Bereich"],
            )
        except EmployeeAlreadyExistsError:
            continue

    return jsonify({"message": "Datei wurde erfolgreich eingelesen"}), 200
