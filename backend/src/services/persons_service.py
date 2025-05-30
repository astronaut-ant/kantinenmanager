from uuid import UUID
from src.repositories.persons_repository import PersonsRepository
from src.utils.exceptions import NotFoundError
from src.utils.pdf_creator import PDFCreationUtils


class PersonsService:
    """Service for handling person management."""

    @staticmethod
    def create_qr_code_person(person_id: UUID):
        """Create a QR code for a person.

        :param person_id: The ID of the person to create the QR code for

        :return: The QR code as a Response object
        """

        person = PersonsRepository.get_person_by_id(person_id)
        if not person:
            raise NotFoundError(f"Person mit ID {person_id}")

        return PDFCreationUtils.create_qr_code_person(person)
