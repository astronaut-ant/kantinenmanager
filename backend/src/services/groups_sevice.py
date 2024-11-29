from models.group import Group
from models.location import Location
from models.user import User
from repositories.groups_repository import GroupsRepository
from uuid import UUID


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
            user_id_groupleader: UUID,
            location_id: UUID,
            user_id_replacement: UUID = None,
    ):
        group_leader_exists = db.query(User).filter(User.id == user_id_groupleader).first()
        if not group_leader_exists:
            raise ValueError(f"Der User mit der ID {user_id_groupleader} existiert nicht.")
        
        location_exists = db.query(Location).filter(Location.id == location_id).first()
        if not location_exists:
            raise ValueError(f"Die Location mit der ID {location_id} existiert nicht.")
        
        return GroupsRepository.create_group(
            db,
            group_name,
            user_id_groupleader,
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