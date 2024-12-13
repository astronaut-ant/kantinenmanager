from src.models.employee import Employee
from src.models.location import Location
from src.models.user import UserGroup
from src.models.group import Group
from uuid import UUID
from src.database import db
from sqlalchemy import func, or_, select


class GroupsRepository:
    """Repository to handle database operations for group data."""

    @staticmethod
    def create_group(
        group_name: str,
        user_id_group_leader: UUID,
        location_id: UUID,
        user_id_replacement: UUID = None,
    ) -> UUID:
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
    def get_groups_by_group_leader(person_id: UUID):
        """Get all groups belonging to a group leader.

        Each group contains a boolean indicating if the group is the users own group.
        """

        query = (
            select(
                Group.id,
                Group.group_name,
                (Group.user_id_group_leader == person_id).label("is_home_group"),
            )
            .join(Group.employees)
            .where(
                or_(
                    Group.user_id_group_leader == person_id,
                    Group.user_id_replacement == person_id,
                )
            )
            .group_by(Group.id)
        )

        return db.session.execute(query).mappings().all()

    @staticmethod
    def update_group(group: Group) -> None:
        """Update a group in the database."""
        # SQLAlchemy automatically tracks changes to objects, we only need to commit the session to save the changes

        db.session.commit()

    @staticmethod
    def get_groups_by_userscope(user_id, user_group) -> list[Group]:
        """Get all groups with locations."""
        if user_group == UserGroup.verwaltung:
            return db.session.query(Group).all()

        if user_group == UserGroup.standortleitung:
            return (
                db.session.query(Group)
                .join(Location)
                .filter(Location.user_id_location_leader == user_id)
                .all()
            )

        if user_group == UserGroup.gruppenleitung:
            return (
                db.session.query(Group)
                .filter(
                    or_(
                        Group.user_id_group_leader == user_id,
                        Group.user_id_replacement == user_id,
                    )
                )
                .all()
            )

        return []

    @staticmethod
    def get_group_by_name_and_location(
        group_name: str, location_id: UUID
    ) -> Group | None:
        """Retrieve a group by its name and location."""
        return (
            db.session.query(Group)
            .filter(Group.group_name == group_name, Group.location_id == location_id)
            .first()
        )

    @staticmethod
    def delete_group(group: Group) -> None:
        """Delete a group from the database."""
        db.session.delete(group)
        db.session.commit()
        return None
