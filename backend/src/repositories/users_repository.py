"""Repository to handle database operations for user data."""

from sqlalchemy import delete, select, or_, and_
from src.models.user import User, UserGroup
from src.models.group import Group
from src.models.preorder import PreOrder
from src.models.location import Location
from src.database import db
from uuid import UUID
from typing import Optional


class UsersRepository:
    """Repository to handle database operations for user data."""

    @staticmethod
    def get_users(user_group_filter: Optional[UserGroup] = None) -> list[User]:
        """Get all users saved in the database

        :params user_group: optional filter for user group
        :return: A list of all users with all properties, optionally filtered by user group
        """
        if user_group_filter:
            return db.session.scalars(
                select(User).where(
                    and_(
                        User.user_group == user_group_filter,
                        User.hidden == False,
                    )
                )
            ).all()

        return db.session.scalars(select(User).where(User.hidden == False)).all()

    @staticmethod
    def get_user_by_id(user_id: UUID) -> User | None:
        """Retrieve a user by their ID

        :param user_id: The ID of the user to retrieve

        :return: The user with the given ID or None if no user was found
        """
        # TODO: Test this method

        return db.session.scalars(
            select(User).where(
                and_(
                    User.id == user_id,
                    User.hidden == False,
                )
            )
        ).first()

    @staticmethod
    def get_user_by_username(username) -> User | None:
        """Retrieve a user by their username

        :param username: The username of the user to retrieve

        :return: The user with the given username or None if no user was found
        """

        return db.session.scalars(
            select(User).where(
                and_(
                    User.username == username,
                    User.hidden == False,
                )
            )
        ).first()

    @staticmethod
    def get_users_by_user_group(group: UserGroup) -> list[User]:
        """Get users by user group

        :return: A list of all users with user group
        """

        return list(
            db.session.scalars(
                select(User).where(
                    and_(
                        User.user_group == group,
                        User.hidden == False,
                    )
                )
            ).all()
        )

    @staticmethod
    def get_group_leader():
        """Get all group leaders"""
        return db.session.scalars(
            select(User).where(
                and_(
                    User.user_group == UserGroup.gruppenleitung,
                    User.hidden == False,
                )
            )
        ).all()

    @staticmethod
    def get_location_leader():
        """Get all location leaders"""
        return db.session.scalars(
            select(User).where(
                and_(
                    User.user_group == UserGroup.standortleitung,
                    User.hidden == False,
                )
            )
        ).all()

    @staticmethod
    def get_hidden_users():
        """Get all hidden users"""
        return db.session.scalars(select(User).where(User.hidden == True)).all()

    @staticmethod
    def get_hidden_user_by_id(user_id: UUID):
        """Get hidden users by id"""
        return db.session.scalars(
            select(User.id).where(User.hidden == True, User.id == user_id)
        ).first()

    @staticmethod
    def get_hidden_user_by_username(username):
        """Get hidden users by username"""
        return db.session.scalars(
            select(User.id).where(User.hidden == True, User.username == username)
        ).first()

    @staticmethod
    def create_user(user: User):
        """Create a new user in the database"""
        db.session.add(user)
        db.session.commit()

        return user.id

    @staticmethod
    def update_user(user: User):
        """Update a user in the database"""

        db.session.commit()

    @staticmethod
    def delete_user(user: User):
        """Set the hidden flag for a user to True and delete all pre_orders belonging to that person"""

        db.session.execute(delete(PreOrder).where(PreOrder.person_id == user.id))
        user.hidden = True
        db.session.commit()

    @staticmethod
    def get_group_and_location_leaders():
        """Get all group and location leaders"""
        return db.session.scalars(
            select(User)
            .where(
                and_(
                    or_(
                        User.id == Group.user_id_group_leader,
                        User.id == Location.user_id_location_leader,
                    ),
                    User.hidden == False,
                )
            )
            .join(Group, Group.user_id_group_leader == User.id)
            .join(Location, Location.user_id_location_leader == User.id)
        ).all()
