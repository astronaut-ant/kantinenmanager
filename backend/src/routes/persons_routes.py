from uuid import UUID
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err
from src.models.user import UserGroup
from flask import Blueprint
from flasgger import swag_from
from src.services.persons_service import PersonsService
from src.utils.exceptions import NotFoundError

persons_routes = Blueprint("persons_routes", __name__)


@persons_routes.get("/api/persons/create-qr/<uuid:person_id>")
@login_required(groups=[UserGroup.verwaltung])
@swag_from(
    {
        "tags": ["persons"],
        "parameters": [
            {
                "in": "path",
                "name": "person_id",
                "required": True,
                "schema": {"type": "string"},
            }
        ],
        "responses": {
            200: {
                "description": "Successfully created QR code as a PDF for the person",
                "content": {
                    "application/pdf": {
                        "schema": {"type": "string", "format": "binary"}
                    }
                },
            },
            404: {
                "description": "QR code could not be created for the person",
            },
        },
    }
)
def create_qr_code(person_id: UUID):
    """Create the QR code for a person by ID
    Create the QR code for a person by ID

    Authentication: required
    Authorization: Verwaltung
    ---
    """
    try:
        return PersonsService.create_qr_code(person_id)
    except NotFoundError:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Person existiert nicht",
                description="Es existiert keine Person zu der ID in der Datenbank",
            )
        )
