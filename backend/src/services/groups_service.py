from uuid import UUID
from src.models.user import UserGroup
from src.models.group import Group
from src.repositories.groups_repository import GroupsRepository
from src.repositories.users_repository import UsersRepository
from src.repositories.locations_repository import LocationsRepository
from src.repositories.employees_repository import EmployeesRepository
from src.utils.exceptions import AlreadyExistsError, NotFoundError, BadValueError

# TODO: Add to PDFCreator
from src.models.employee import Employee
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from flask import make_response, send_file
import qrcode


class GroupsService:
    """Service for managing groups, group leaders, and replacements."""

    @staticmethod
    def create_group(
        group_name: str,
        group_number: int,
        user_id_group_leader: UUID,
        location_id: UUID,
        user_id_replacement: UUID = None,
    ) -> UUID:

        if GroupsRepository.get_group_by_name_and_location(group_name, location_id):
            raise AlreadyExistsError(
                ressource=f"Gruppe {group_name}", details="an diesem Standort."
            )

        group_leader_exists = UsersRepository.get_user_by_id(user_id_group_leader)
        if not group_leader_exists:
            raise NotFoundError(f"Gruppenleitung mit ID {user_id_group_leader}")
        if group_leader_exists.user_group != UserGroup.gruppenleitung:
            raise BadValueError(
                f"Nutzer:in mit ID {user_id_group_leader} ist keine Gruppenleitung."
            )
        if GroupsRepository.check_if_user_already_group_leader(user_id_group_leader):
            raise BadValueError(
                f"Nutzer:in mit ID {user_id_group_leader} ist bereits Gruppenleitung."
            )

        if user_id_replacement:
            group_replacement_exists = UsersRepository.get_user_by_id(
                user_id_replacement
            )
            if not group_replacement_exists:
                raise NotFoundError(f"Nutzer:in mit ID {user_id_replacement}")
            if group_replacement_exists.user_group != UserGroup.gruppenleitung:
                raise BadValueError(
                    f"Nutzer:in mit ID {user_id_replacement} ist keine Gruppenleitung."
                )

        location_exists = LocationsRepository.get_location_by_id(location_id)
        if not location_exists:
            raise NotFoundError(f"Standort mit ID {location_id}")

        group_number_exists = GroupsRepository.get_group_by_number(group_number)
        if group_number_exists:
            raise AlreadyExistsError(ressource=f"Gruppe {group_number}")

        return GroupsRepository.create_group(
            group_name,
            group_number,
            user_id_group_leader,
            location_id,
            user_id_replacement,
        )

    @staticmethod
    def get_group_by_id(group_id: UUID) -> Group:
        """Retrieve a group by its ID or raise an error."""
        group = GroupsRepository.get_group_by_id(group_id)
        if not group:
            raise NotFoundError(f"Gruppe mit ID {group_id}")
        return group

    @staticmethod  # Hier könnte es sinnvoll sein Schemas zu verwenden
    def get_all_groups_with_locations(user_id, user_group) -> dict[str, list[str]]:
        """Get all groups with locations."""

        locations = {}
        groups = GroupsRepository.get_groups_by_userscope(user_id, user_group)

        for group in groups:
            # seperate group name and location name by splitting at the first "-"
            # match = re.match(r"^(.*?)\s*-\s*(.*)$", group.group_name)
            # for tests use .group_name instead of match.group(1)
            # group_name = match.group(1)
            group_name = group.group_name
            group_location = group.location.location_name

            if group_location not in locations:
                locations[group_location] = []

            locations[group_location].append(group_name)

        return locations

    @staticmethod
    def get_groups(user_id, user_group) -> list[Group]:
        """Get all groups for respective user."""
        return GroupsRepository.get_groups_by_userscope(user_id, user_group)

    @staticmethod
    def delete_group(group_id: UUID):
        """Delete a group by its ID."""
        group = GroupsRepository.get_group_by_id(group_id)
        if not group:
            raise NotFoundError(f"Gruppe mit ID {group_id}")
        GroupsRepository.delete_group(group)

    @staticmethod
    def update_group(
        group_id: UUID,
        group_name: str,
        group_number: int,
        user_id_group_leader: UUID,
        location_id: UUID,
        user_id_replacement: UUID = None,
    ) -> Group:
        """Updates a group."""
        group = GroupsRepository.get_group_by_id(group_id)
        if not group:
            raise NotFoundError(f"Gruppe mit ID {group_id}")

        if user_id_group_leader != group.user_id_group_leader:
            group_leader_exists = UsersRepository.get_user_by_id(user_id_group_leader)
            if not group_leader_exists:
                raise NotFoundError(f"Nutzer:in mit ID {user_id_group_leader}")
            if group_leader_exists.user_group != UserGroup.gruppenleitung:
                raise BadValueError(
                    f"Nutzer:in mit ID {user_id_group_leader} ist keine Gruppenleitung."
                )
            group.user_id_group_leader = user_id_group_leader

        if user_id_replacement and (user_id_replacement != group.user_id_replacement):
            group_replacement_exists = UsersRepository.get_user_by_id(
                user_id_replacement
            )
            if not group_replacement_exists:
                raise NotFoundError(f"Nutzer:in mit ID {user_id_replacement}")
            if group_replacement_exists.user_group != UserGroup.gruppenleitung:
                raise BadValueError(
                    f"Vertretungs-Nutzer:in mit ID {user_id_replacement} ist keine Gruppenleitung."
                )
            group.user_id_replacement = user_id_replacement
        elif user_id_replacement is None:
            group.user_id_replacement = None

        # Soll die Location eine Gruppe änderbar sein?
        if location_id != group.location_id:
            location_exists = LocationsRepository.get_location_by_id(location_id)
            if not location_exists:
                raise NotFoundError(f"Standort mit ID {location_id}")
            group.location_id = location_id

        if group_number != group.group_number:
            group_number_exists = GroupsRepository.get_group_by_number(group_number)
            if group_number_exists:
                raise AlreadyExistsError(ressource=f"Gruppe {group_number}")
            group.group_number = group_number

        group.group_name = group_name
        GroupsRepository.update_group(group)
        return group

    @staticmethod
    def create_batch_qr_codes(group_id: UUID, user_id: UUID, user_group: UserGroup):
        """Create a batch of QR codes for a group."""
        group = GroupsRepository.get_group_by_id(group_id)
        employees = EmployeesRepository.get_employees_by_user_scope(
            user_group=user_group, user_id=user_id, group_id=group_id
        )
        if not employees:
            raise NotFoundError(f"Mitarbeiter:innen der Gruppe mit ID {group_id}")
        # return PDFCreator.create_batch_qr_codes(group, employees)
        return GroupsService.create_qr_codes(group, employees)

    @staticmethod
    def create_qr_codes(group: Group, employees: list[Employee]):
        """Create a PDF with QR codes for a list of employees.

        :param employees: List of employee objects to create QR codes for
        :return: The PDF with QR codes as a Response object
        """

        pdf_buffer = BytesIO()
        page_width, page_height = A4
        c = canvas.Canvas(pdf_buffer, pagesize=A4)

        # QR code settings
        qr_size = 150  # Adjust size to fit 3 per row
        margin = 30  # Margin between QR codes
        cols = 3  # Number of QR codes per row
        x_start = margin
        y_start = page_height - margin - qr_size

        x_position = x_start
        y_position = y_start

        for idx, employee in enumerate(employees):
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(employee.id)
            qr.make(fit=True)
            img = qr.make_image(fill="black", back_color="white")

            # Convert QR image to ImageReader
            qr_buffer = BytesIO()
            img.save(qr_buffer, format="PNG")
            qr_buffer.seek(0)
            qr_image = ImageReader(qr_buffer)

            # Draw QR code and text
            c.drawImage(qr_image, x_position, y_position, width=qr_size, height=qr_size)
            c.setFont("Helvetica", 10)
            c.drawCentredString(
                x_position + qr_size / 2,
                y_position - 12,
                f"{employee.first_name} {employee.last_name}",
            )

            # Update position for next QR code
            x_position += qr_size + margin

            if (idx + 1) % cols == 0:
                x_position = x_start
                y_position -= qr_size + 2 * margin

                # Start a new page if needed
                if y_position < margin:
                    c.showPage()
                    y_position = y_start

        c.save()
        pdf_buffer.seek(0)

        response = make_response(
            send_file(
                pdf_buffer,
                mimetype="application/pdf",
                as_attachment=True,
                download_name=f"{group.group_name}_qr_codes.pdf",
            )
        )
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        return response
