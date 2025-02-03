from flask import send_file, make_response
import qrcode
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from uuid import UUID
from src.models.person import Person  # noqa: F401
from src.repositories.persons_repository import PersonsRepository
from src.utils.exceptions import NotFoundError


class PersonsService:
    """Service for handling person management."""

    @staticmethod
    def create_qr_code(person_id: UUID):
        """Create a QR code for a person.

        :param person_id: The ID of the person to create the QR code for

        :return: The QR code as a Response object
        """

        person = PersonsRepository.get_person_by_id(person_id)
        if not person:
            raise NotFoundError(f"Person mit ID {person_id}")

        # QR-Code generieren
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(person.id)
        qr.make(fit=True)
        img = qr.make_image(fill="black", back_color="white")

        # QR-Code-Bild in einem BytesIO-Objekt im Speicher speichern
        qr_buffer = BytesIO()
        img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        pdf_buffer = BytesIO()
        page_width, page_height = A4
        c = canvas.Canvas(pdf_buffer, pagesize=A4)

        # Position für den QR-Code
        qr_size = 200
        x_center = (page_width - qr_size) / 2
        y_position = (page_height / 2) + 180  # Position in der oberen Hälfte

        # BytesIO-Objekt in ein ImageReader-Objekt umwandeln, um das QR-Code-Bild in die Canvas einzubetten
        qr_image = ImageReader(qr_buffer)
        c.drawImage(qr_image, x_center, y_position, width=qr_size, height=qr_size)

        # Text unterhalb des QR-Codes hinzufügen
        text_y_position = y_position - 20
        c.setFont("Helvetica", 12)
        c.drawCentredString(
            page_width / 2,
            text_y_position,
            f"{person.first_name} {person.last_name}",
        )
        c.save()
        pdf_buffer.seek(0)

        response = make_response(
            send_file(
                pdf_buffer,
                mimetype="application/pdf",
                as_attachment=True,
                download_name=f"qr-code_{person.first_name}{person.last_name}.pdf",
            )
        )
        # Explicitly expose the Content-Disposition header for the frontend
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        return response
