from uuid import UUID
from src.models.user import UserGroup
from src.models.group import Group
from src.repositories.groups_repository import GroupsRepository
from src.repositories.users_repository import UsersRepository
from src.repositories.locations_repository import LocationsRepository
from src.repositories.employees_repository import EmployeesRepository
from src.utils.exceptions import AlreadyExistsError, NotFoundError, BadValueError
from src.utils.pdf_creator import PDFCreationUtils


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

        location_exists = LocationsRepository.get_location_by_id(location_id)
        if not location_exists:
            raise NotFoundError(f"Standort mit ID {location_id}")

        if GroupsRepository.get_group_by_name_and_location(group_name, location_id):
            raise AlreadyExistsError(
                ressource=f"Gruppe {group_name}", details="an diesem Standort."
            )

        group_number_exists = GroupsRepository.get_group_by_number(group_number)
        if group_number_exists:
            raise AlreadyExistsError(ressource=f"Gruppe {group_number}")

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

        for g in groups:
            group_name = g.group_name
            location_name = LocationsRepository.get_location_by_id(
                g.location_id
            ).location_name

            if location_name not in locations:
                locations[location_name] = []

            locations[location_name].append(group_name)

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
        return PDFCreationUtils.create_batch_qr_codes(employees=employees, group=group)
