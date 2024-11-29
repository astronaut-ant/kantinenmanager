from sqlalchemy.orm import Session
from models.group import Group
from uuid import UUID
from src.database import db


class GroupsRepository:
    """Repository to handle database operations for group data."""

    @staticmethod
    def create_group(
        group_name: str,
        user_id_group_leader: UUID,
        location_id: UUID,
        user_id_replacement: UUID = None,
    ) -> Group:
        """Create a new group in the database."""
        new_group = Group(
            group_name=group_name,
            user_id_group_leader=user_id_group_leader,
            user_id_replacement=user_id_replacement,
            location_id=location_id,
        )
        db.add(new_group)
        db.commit()
        db.refresh(new_group)
        return new_group

    @staticmethod
    def _get_group(group_id: UUID) -> Group | None:
        """Helper method to retrieve a group by ID."""
        return db.query(Group).filter(Group.id == group_id).first()

    @staticmethod
    def assign_group_leader(group_id: UUID, user_id: UUID) -> Group | None:
        """Assign a user as the leader of a group."""
        group = GroupsRepository._get_group(db, group_id)
        if group:
            group.user_id_group_leader = user_id
            db.commit()
            db.refresh(group)
            return group
        return None

    @staticmethod
    def remove_group_leader(group_id: UUID) -> Group | None:
        """Remove the leader from a group."""
        group = GroupsRepository._get_group(db, group_id)
        if group:
            group.user_id_group_leader = None
            db.commit()
            db.refresh(group)
            return group
        return None

    @staticmethod
    def assign_group_replacement(group_id: UUID, user_id: UUID) -> Group | None:
        """Assign a user as the replacement for a group leader."""
        group = GroupsRepository._get_group(db, group_id)
        if group:
            group.user_id_replacement = user_id
            db.commit()
            db.refresh(group)
            return group
        return None

    @staticmethod
    def remove_group_replacement(group_id: UUID) -> Group | None:
        """Remove the replacement from a group leader."""
        group = GroupsRepository._get_group(db, group_id)
        if group:
            group.user_id_replacement = None
            db.commit()
            db.refresh(group)
            return group
        return None