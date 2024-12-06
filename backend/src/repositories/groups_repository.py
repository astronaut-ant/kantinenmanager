from src.models.group import Group
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
        db.session.add(new_group)
        db.session.commit()

        return new_group.id

    @staticmethod
    def get_group_by_id(group_id: UUID) -> Group | None:
        """Helper method to retrieve a group by ID."""
        return db.session.query(Group).filter(Group.id == group_id).first()

    @staticmethod
    def assign_group_leader(group_id: UUID, user_id: UUID) -> Group | None:
        """Assign a user as the leader of a group."""
        group = GroupsRepository.get_group_by_id(group_id)
        if group:
            group.user_id_group_leader = user_id

            # SQLAlchemy automatically tracks changes to objects
            # we only need to commit the session to save the changes

            db.session.commit()
            return group

        return None

    @staticmethod
    def remove_group_leader(group_id: UUID) -> Group | None:
        """Remove the leader from a group."""
        group = GroupsRepository.get_group_by_id(group_id)
        if group:
            group.user_id_group_leader = None

            # SQLAlchemy automatically tracks changes to objects
            # we only need to commit the session to save the changes

            db.session.commit()
            return group
        return None

    @staticmethod
    def assign_group_replacement(group_id: UUID, user_id: UUID) -> Group | None:
        """Assign a user as the replacement for a group leader."""
        group = GroupsRepository.get_group_by_id(group_id)
        if group:
            group.user_id_replacement = user_id

            # SQLAlchemy automatically tracks changes to objects
            # we only need to commit the session to save the changes

            db.session.commit()
            return group
        return None

    @staticmethod
    def remove_group_replacement(group_id: UUID) -> Group | None:
        """Remove the replacement from a group leader."""
        group = GroupsRepository.get_group_by_id(group_id)
        if group:
            group.user_id_replacement = None

            # SQLAlchemy automatically tracks changes to objects
            # we only need to commit the session to save the changes

            db.session.commit()
            return group
        return None

    @staticmethod
    def update_group(group: Group) -> None:
        """Update a group in the database."""

        # SQLAlchemy automatically tracks changes to objects
        # we only need to commit the session to save the changes

        db.session.commit()

    @staticmethod
    def get_all_groups() -> list[Group]:
        """Get all groups with locations."""
        return db.session.query(Group).all()

    @staticmethod
    def delete_group(group: Group) -> None:
        """Delete a group from the database."""
        db.session.delete(group)
        db.session.commit()
        return None
