from uuid import UUID

from flask import Blueprint, jsonify, request, g
from flasgger import swag_from
from marshmallow import ValidationError

from src.models.user import UserGroup
from src.schemas.employee_schemas import EmployeeChangeSchema, EmployeeFullNestedSchema
from src.services.employees_service import EmployeesService
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err
from src.utils.exceptions import (
    AlreadyExistsError,
    BadValueError,
    NotFoundError,
    AccessDeniedError,
)

employees_routes = Blueprint("employees_routes", __name__)


# Bei jedem GET Request (siehe HTTP) auf /api/users wird die get_employees Funktion aufgerufen und alle Emplyoees, die Scope des Nutzers sind zurückgegeben
@employees_routes.get("/api/employees")
@login_required()
@swag_from(
    {
        "tags": ["employees"],
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
                    "items": EmployeeFullNestedSchema,
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

    return EmployeeFullNestedSchema(many=True).dump(employees)


@employees_routes.get("/api/employees/<uuid:employee_id>")
@login_required()
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
                "schema": EmployeeFullNestedSchema,
            },
            404: {"description": "Employee not found"},
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
    try:
        employee = EmployeesService.get_employee_by_id(
            employee_id, g.user_group, g.user_id
        )
    except NotFoundError as err:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Mitarbeiter nicht gefunden",
                description="Es wurde kein Mitarbeiter mit dieser ID gefunden",
                details=str(err),
            )
        )

    return EmployeeFullNestedSchema().dump(employee)


@employees_routes.post("/api/employees")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["employees"],
        "parameters": [
            {
                "in": "body",
                "name": "body",
                "schema": EmployeeChangeSchema,
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
def create_employee():
    """Create a new employee
    Create a new employee
    ---
    """

    try:
        body = EmployeeChangeSchema().load(request.json)
        id = EmployeesService.create_employee(**body)
    except ValidationError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Format der Daten im Request-Body nicht valide",
                details=err.messages,
            )
        )
    except AlreadyExistsError:
        abort_with_err(
            ErrMsg(
                status_code=409,
                title="Kunden-Nr. bereits vergeben",
                description="Die Kunden-Nr. ist bereits vergeben",
            )
        )
    except NotFoundError as err:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Gruppe nicht gefunden",
                description="Die Gruppe existiert nicht",
                details=str(err),
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
    except AlreadyExistsError:
        abort_with_err(
            ErrMsg(
                status_code=409,
                title="Ein Nutzer existiert bereits",
                description="Einer der Nutzer existiert bereits",
            )
        )
    except NotFoundError:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Gruppe wurde nicht gefunden",
                description="Die Gruppe zu mindestens einem der Benutzer existiert nicht",
            )
        )
    except BadValueError as err:
        abort_with_err(
            ErrMsg(
                status_code=422,
                title="Übergebene Daten nicht verarbeitbar",
                description="Die übergebene Datei oder ein Name darin können nicht verarbeitet werden.",
                details=str(err),
            )
        )

    return jsonify({"message": "Datei wurde erfolgreich eingelesen"}), 200


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
                "schema": {"type": "string", "format": "uuid"},
            },
            {"in": "body", "name": "body", "schema": EmployeeChangeSchema},
        ],
        "responses": {
            200: {
                "description": "Returns the updated employee",
                "schema": EmployeeFullNestedSchema,
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
        body = EmployeeChangeSchema().load(request.json)
        employee = EmployeesService.get_employee_by_id(
            employee_id, g.user_group, g.user_id
        )
        EmployeesService.update_employee(employee, **body)

    except ValidationError as err:
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Validierungsfehler",
                description="Format der Daten im Request-Body nicht valide",
                details=str(err),
            )
        )
    except NotFoundError as err:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Mitarbeiter:in nicht gefunden",
                description="Es wurde kein Mitarbeiter:in mit dieser ID gefunden",
                details=str(err),
            )
        )
    except AlreadyExistsError as err:
        abort_with_err(
            ErrMsg(
                status_code=409,
                title="Mitarbeiter:in-Nummer bereits vergeben",
                description="Diese Mitarbeiter:in-Nummer ist bereits vergeben",
                details=str(err),
            )
        )

    return EmployeeFullNestedSchema().dump(employee)


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
    try:
        employee = EmployeesService.get_employee_by_id(
            employee_id, g.user_group, g.user_id
        )
    except NotFoundError as err:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Mitarbeiter:in nicht gefunden",
                description="Mitarbeiter:inn wurde",
                details=str(err),
            )
        )

    EmployeesService.delete_employee(employee)
    return jsonify({"message": "Mitarbeiter:in erfolgreich gelöscht"})


@employees_routes.delete("/api/employees/")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["employees"],
        "parameters": [
            {
                "in": "body",
                "name": "employee_ids",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "employee_ids": {
                            "type": "array",
                            "items": {"type": "string", "format": "uuid"},
                            "description": "List of employee IDs to generate QR codes for",
                        }
                    },
                },
            }
        ],
        "responses": {
            200: {
                "description": "Successfully deleted employees",
                "schema": {
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                },
            },
            404: {"description": "Employee not found"},
        },
    }
)
def delete_list_of_employees():
    data = request.get_json()
    if (
        not data
        or "employee_ids" not in data
        or not isinstance(data["employee_ids"], list)
    ):
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Ungültiges Format",
                description="Die Anfrage muss eine Liste von UUIDs enthalten",
            )
        )

    try:
        employee_ids = [UUID(id_str) for id_str in data["employee_ids"]]
    except (ValueError, TypeError):
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Ungültige UUID",
                description="Eine oder mehrere IDs sind keine gültigen UUIDs",
            )
        )

    for employee_id in employee_ids:
        try:
            employee = EmployeesService.get_employee_by_id(
                employee_id, g.user_group, g.user_id
            )
        except NotFoundError as err:
            abort_with_err(
                ErrMsg(
                    status_code=404,
                    title="Mitarbeiter:in nicht gefunden",
                    description="Ein oder mehrere Mitarbeiter wurden nicht gefunden",
                    details=str(err),
                )
            )
        except AccessDeniedError as err:
            abort_with_err(
                ErrMsg(
                    status_code=403,
                    title="Zugriff verweigert",
                    description="Sie haben keine Berechtigung für diese Operation",
                    details=str(err),
                )
            )
        EmployeesService.delete_employee(employee)

    return jsonify({"message": "Mitarbeiter:innen erfolgreich gelöscht"})


@employees_routes.get("/api/employees/qr-codes")
@login_required(
    groups=[UserGroup.verwaltung, UserGroup.standortleitung, UserGroup.gruppenleitung]
)
@swag_from(
    {
        "tags": ["employees"],
        "responses": {
            200: {
                "description": "Successfully created QR codes as a PDF",
                "content": {
                    "application/pdf": {
                        "schema": {"type": "string", "format": "binary"}
                    }
                },
            },
            404: {
                "description": "QR codes could not be created",
            },
        },
    }
)
def get_qr_code_for_all_employees_by_user_scope():
    try:
        qr_codes = EmployeesService.get_qr_code_for_all_employees_by_user_scope(
            user_group=g.user_group, user_id=g.user_id
        )
    except NotFoundError as err:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Mitarbeiter:innen nicht gefunden",
                description="Es wurden keine Mitarbeiter:innen gefunden",
                details=str(err),
            )
        )
    return qr_codes


@employees_routes.post("/api/employees/qr-codes-by-list")
@login_required(
    groups=[UserGroup.verwaltung, UserGroup.standortleitung, UserGroup.gruppenleitung]
)
@swag_from(
    {
        "tags": ["employees"],
        "parameters": [
            {
                "in": "body",
                "name": "employee_ids",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "employee_ids": {
                            "type": "array",
                            "items": {"type": "string", "format": "uuid"},
                            "description": "List of employee IDs to generate QR codes for",
                        }
                    },
                },
            }
        ],
        "responses": {
            200: {
                "description": "Successfully created QR codes as a PDF",
                "content": {
                    "application/pdf": {
                        "schema": {"type": "string", "format": "binary"}
                    }
                },
            },
            400: {"description": "Invalid request format"},
        },
    }
)
def get_qr_code_for_employees_list():
    """Generate QR codes PDF for specific employees
    Creates a PDF containing QR codes for the employees specified by their IDs

    Authentication: required
    Authorization: Verwaltung, Standortleitung, Gruppenleitung
    ---
    """

    data = request.get_json()
    if (
        not data
        or "employee_ids" not in data
        or not isinstance(data["employee_ids"], list)
    ):
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Ungültiges Format",
                description="Die Anfrage muss eine Liste von UUIDs enthalten",
            )
        )

    try:
        employee_ids = [UUID(id_str) for id_str in data["employee_ids"]]
    except (ValueError, TypeError):
        abort_with_err(
            ErrMsg(
                status_code=400,
                title="Ungültige UUID",
                description="Eine oder mehrere IDs sind keine gültigen UUIDs",
            )
        )

    try:
        qr_codes = EmployeesService.get_qr_code_for_employees_list(
            employee_ids=employee_ids, user_group=g.user_group, user_id=g.user_id
        )
    except NotFoundError as err:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Mitarbeiter:innen nicht gefunden",
                description="Eine oder mehrere Mitarbeiter:innen mit angegebenen IDs nicht gefunden",
                details=str(err),
            )
        )

    return qr_codes
