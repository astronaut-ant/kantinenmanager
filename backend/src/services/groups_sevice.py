from src.models.group import Group
from src.models.location import Location
from src.models.user import User
from src.repositories.groups_repository import GroupsRepository
from uuid import UUID
import re


class GroupDoesNotExistError(Exception):
    """Exception raised when a group does not exist at a given location."""

    def __init__(self, group_id: UUID):
        super().__init__(f"Die Gruppe mit der ID {group_id} existiert nicht.")


class GroupsService:
    """Service for managing groups, group leaders, and replacements."""

    @staticmethod
    def create_group(
        db,
        group_name: str,
        user_id_group_leader: UUID,
        location_id: UUID,
        user_id_replacement: UUID = None,
    ):
        group_leader_exists = (
            db.query(User).filter(User.id == user_id_group_leader).first()
        )
        if not group_leader_exists:
            raise ValueError(
                f"Der User mit der ID {user_id_group_leader} existiert nicht."
            )

        location_exists = db.query(Location).filter(Location.id == location_id).first()
        if not location_exists:
            raise ValueError(f"Die Location mit der ID {location_id} existiert nicht.")

        return GroupsRepository.create_group(
            db,
            group_name,
            user_id_group_leader,
            location_id,
            user_id_replacement,
        )

    @staticmethod
    def add_group_leader(db, group_id: UUID, user_id: UUID):
        """Assign a user as the leader of a group."""
        group = GroupsRepository.assign_group_leader(db, group_id, user_id)
        if not group:
            raise GroupDoesNotExistError(group_id)
        return group

    @staticmethod
    def remove_group_leader(db, group_id: UUID):
        """Remove the leader from a group."""
        group = GroupsRepository.remove_group_leader(db, group_id)
        if not group:
            raise GroupDoesNotExistError(group_id)
        return group

    @staticmethod
    def add_group_replacement(db, group_id: UUID, user_id: UUID):
        """Assign a user as the replacement for a group leader."""
        group = GroupsRepository.assign_group_replacement(db, group_id, user_id)
        if not group:
            raise GroupDoesNotExistError(group_id)
        return group

    @staticmethod
    def remove_group_replacement(db, group_id: UUID):
        """Remove the replacement from a group leader."""
        group = GroupsRepository.remove_group_replacement(db, group_id)
        if not group:
            raise GroupDoesNotExistError(group_id)
        return group

    @staticmethod
    def get_all_groups_with_locations():
        """Get all groups with locations."""
        locations = {}
        groups = GroupsRepository.get_all_groups_with_locations()
        for group in groups:
            match = re.match(r"^(.*?)\s*-\s*(.*)$", group.group_name)
            group_name = match.group(1)
            group_location = match.group(2)
            if group_location not in locations:
                locations[group_location] = []
            locations[group_location].append(group_name)
        return locations
