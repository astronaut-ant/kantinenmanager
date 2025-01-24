from uuid import UUID
import re
from src.models.user import UserGroup
from src.models.group import Group
from src.repositories.groups_repository import GroupsRepository
from src.repositories.users_repository import UsersRepository
from src.repositories.locations_repository import LocationsRepository
from src.utils.exceptions import (
    GroupAlreadyExists,
    GroupDoesNotExistError,
    LeaderDoesNotExist,
    LocationDoesNotExist,
)


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
            raise GroupAlreadyExists(
                f"Die Gruppe {group_name} existiert bereits an diesem Standort."
            )

        group_leader_exists = UsersRepository.get_user_by_id(user_id_group_leader)
        if not group_leader_exists:
            raise LeaderDoesNotExist(
                f"Der User mit der ID {user_id_group_leader} existiert nicht."
            )
        if group_leader_exists.user_group != UserGroup.gruppenleitung:
            raise ValueError(
                f"Der User mit der ID {user_id_group_leader} ist kein Gruppenleiter."
            )
        if GroupsRepository.check_if_user_already_group_leader(user_id_group_leader):
            raise ValueError(
                f"Der User mit der ID {user_id_group_leader} ist bereits Gruppenleiter."
            )

        if user_id_replacement:
            group_replacement_exists = UsersRepository.get_user_by_id(
                user_id_replacement
            )
            if not group_replacement_exists:
                raise ValueError(
                    f"Der User mit der ID {user_id_replacement} existiert nicht."
                )
            if group_replacement_exists.user_group != UserGroup.gruppenleitung:
                raise ValueError(
                    f"Der User mit der ID {user_id_replacement} ist kein Gruppenleiter."
                )

        location_exists = LocationsRepository.get_location_by_id(location_id)
        if not location_exists:
            raise LocationDoesNotExist(
                f"Die Location mit der ID {location_id} existiert nicht."
            )

        group_number_exists = GroupsRepository.get_group_by_number(group_number)
        if group_number_exists:
            raise GroupAlreadyExists(
                f"Die Gruppe mit der Nummer {group_number} existiert bereits."
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
            raise GroupDoesNotExistError(f"Gruppe mit ID {group_id} eistiert nicht.")
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
            raise GroupDoesNotExistError(
                f"Die Gruppe mit der ID {group_id} existiert nicht."
            )
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
            raise GroupDoesNotExistError(group_id)

        if user_id_group_leader != group.user_id_group_leader:
            group_leader_exists = UsersRepository.get_user_by_id(user_id_group_leader)
            if not group_leader_exists:
                raise ValueError(
                    f"Der User mit der ID {user_id_group_leader} existiert nicht."
                )
            if group_leader_exists.user_group != UserGroup.gruppenleitung:
                raise ValueError(
                    f"Der User mit der ID {user_id_group_leader} ist kein Gruppenleiter."
                )
            group.user_id_group_leader = user_id_group_leader

        if user_id_replacement and (user_id_replacement != group.user_id_replacement):
            group_replacement_exists = UsersRepository.get_user_by_id(
                user_id_replacement
            )
            if not group_replacement_exists:
                raise ValueError(
                    f"Der User mit der ID {user_id_replacement} existiert nicht."
                )
            if group_replacement_exists.user_group != UserGroup.gruppenleitung:
                raise ValueError(
                    f"Der Ersatz-User mit der ID {user_id_replacement} ist kein Gruppenleiter."
                )
            group.user_id_replacement = user_id_replacement
        elif user_id_replacement is None:
            group.user_id_replacement = None

        # Soll die Location eine Gruppe änderbar sein?
        if location_id != group.location_id:
            location_exists = LocationsRepository.get_location_by_id(location_id)
            if not location_exists:
                raise ValueError(
                    f"Die Location mit der ID {location_id} existiert nicht."
                )
            group.location_id = location_id

        if group_number != group.group_number:
            group_number_exists = GroupsRepository.get_group_by_number(group_number)
            if group_number_exists:
                raise GroupAlreadyExists(
                    f"Die Gruppe mit der Nummer {group_number} existiert bereits."
                )
            group.group_number = group_number

        group.group_name = group_name
        GroupsRepository.update_group(group)
        return group
