"""Service for handling user management."""

from typing import Optional
from uuid import UUID
from src.repositories.groups_repository import GroupsRepository
from src.repositories.locations_repository import LocationsRepository
from src.models.location import Location
from src.services.auth_service import AuthService
from src.models.user import User, UserGroup
from src.repositories.users_repository import UsersRepository
from src.utils.exceptions import (
    NotFoundError,
    AlreadyExistsError,
    ActionNotPossibleError,
)


class UsersService:
    """Service for handling user management."""

    @staticmethod
    def get_users(user_group_filter: Optional[UserGroup] = None) -> list[User]:
        """Get all users saved in the database."""
        return UsersRepository.get_users(user_group_filter)

    @staticmethod
    def get_user_by_id(user_id: UUID) -> User | None:
        """Retrieve a user by their ID

        :param user_id: The ID of the user to retrieve

        :return: The user with the given ID or None if no user was found
        """

        return UsersRepository.get_user_by_id(user_id)

    @staticmethod
    def get_user_by_username(username: str) -> User | None:
        """Retrieve a user by their username

        :param username: The username of the user to retrieve

        :return: The user with the given username or None if no user was found
        """

        return UsersRepository.get_user_by_username(username)

    @staticmethod
    def create_user(
        first_name: str,
        last_name: str,
        username: str,
        user_group: UserGroup,
        location_id: Optional[UUID] = None,
        password: Optional[str] = None,
    ) -> tuple[UUID, str]:
        """Create a new user in the database.

        :param first_name: The first name of the new user
        :param last_name: The last name of the new user
        :param username: The username of the new user
        :param user_group: The user group of the new user
        :param location_id: The location of the new user
        :param password: The password of the new user. If None, a random password is generated (still needed for mock data)

        :return: A tuple containing the ID of the new user and the initial password

        :raises AlreadyExistsError: If a user with the given username already exists
        """

        if UsersRepository.get_user_by_username(username):
            raise AlreadyExistsError(ressource=f"Nutzer:in {username}")

        if UsersRepository.get_hidden_user_by_username(username):
            raise AlreadyExistsError(ressource=f"Nutzer:in {username} (gelöscht)")

        if location_id and (
            LocationsRepository.get_location_by_id(location_id) is None
        ):
            raise NotFoundError(f"Standort mit ID {location_id}")

        if password is None:
            password = AuthService.generate_password()

        hashed_password = AuthService.hash_password(password)

        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            hashed_password=hashed_password,
            user_group=user_group,
            location_id=location_id,
        )

        id = UsersRepository.create_user(user)

        return id, password

    @staticmethod
    def update_user(
        user: User,
        first_name: str,
        last_name: str,
        username: str,
        user_group: UserGroup,
        location: Location | None = None,
    ) -> User:
        """Update a user in the database.

        :param user: The user to update
        :param first_name: The new first name of the user
        :param last_name: The new last name of the user
        :param username: The new username of the user
        :param user_group: The new user group of the user
        :param location: The new location of the user

        :return: The updated user

        :raises AlreadyExistsError: If a user with the given username already exists
        """

        if username != user.username and UsersRepository.get_user_by_username(username):
            raise AlreadyExistsError(ressource=f"Nutzer:in {username}")

        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.user_group = user_group
        user.location = location

        UsersRepository.update_user(user)

        return user

    @staticmethod
    def block_user(user: User):
        """Block a user.

        :param user: The user to block
        """
        user.blocked = True

        UsersRepository.update_user(user)

    @staticmethod
    def unblock_user(user: User):
        """Unblock a user.

        :param user: The user to unblock
        """
        user.blocked = False

        UsersRepository.update_user(user)

    @staticmethod
    def delete_user(user: User):
        """Delete a user from the database.

        :param user: The user to delete
        """

        if user.user_group == UserGroup.gruppenleitung and (
            user.leader_of_group or user.replacement_leader_of_groups
        ):
            raise ActionNotPossibleError(
                f"{user.first_name} {user.last_name} leitet/vertritt eine Gruppe und kann nicht gelöscht werden."
            )
        if user.user_group == UserGroup.standortleitung and user.leader_of_location:
            raise ActionNotPossibleError(
                f"{user.first_name} {user.last_name} leitet einen Standort und kann nicht gelöscht werden."
            )

        AuthService.invalidate_all_refresh_tokens(user.id)
        UsersRepository.delete_user(user)

    @staticmethod
    def reset_password(user: User) -> str:
        """Reset the password of a user to a new random password.

        The user's sessions get invalidated.

        :param user: The user whose password to reset

        :return: The new password
        """

        new_password = AuthService.generate_password()
        hashed_password = AuthService.hash_password(new_password)

        user.hashed_password = hashed_password

        UsersRepository.update_user(user)

        AuthService.invalidate_all_refresh_tokens(user.id)

        return new_password

    @staticmethod
    def get_group_leader(user_id: UUID) -> list[User]:
        """Get all users with the user group 'gruppenleitung'

        When the requesting user is standortleitung, only group leaders
        with their or no location are returned.

        :param user_id: The ID of the requesting user
        """

        user = UsersRepository.get_user_by_id(user_id)
        if user is None:
            raise NotFoundError(f"Nutzer:in mit ID {user_id}")

        group_leaders = UsersRepository.get_group_leader()

        if user.user_group == UserGroup.standortleitung:
            group_leaders = [
                leader
                for leader in group_leaders
                if leader.location_id in [None, user.location_id]
            ]

        return group_leaders

    @staticmethod
    def get_location_leader() -> list[User]:
        """Get all users with the user group 'standortleitung'"""

        return UsersRepository.get_location_leader()
