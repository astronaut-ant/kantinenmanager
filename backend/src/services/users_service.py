"""Service for handling user management."""

from typing import Optional
from uuid import UUID
from src.repositories.locations_repository import LocationsRepository
from src.models.location import Location
from src.services.auth_service import AuthService
from src.models.user import User, UserGroup
from src.repositories.users_repository import UsersRepository
from src.utils.exceptions import (
    LocationDoesNotExist,
    UserAlreadyExistsError,
    UserCannotBeDeletedError,
)

# Services enthalten die Businesslogik der Anwendung.
# Sie werden von den Routen aufgerufen und ziehen sich
# die notwendigen Daten aus den Repositories.
#
# Hier würde so etwas reinkommen wie die Ertellung des QR-Codes
# oder die Validierung, dass ein Nutzer die korrekten Anmeldedaten
# eingegeben hat.


class UsersService:
    """Service for handling user management."""

    @staticmethod
    def get_users(user_group_filter: Optional[UserGroup] = None) -> list[User]:
        """Get all users saved in the database."""
        if user_group_filter:
            try:
                user_group_filter = UserGroup(user_group_filter)
            except ValueError as err:
                pass

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

        :raises UserAlreadyExistsError: If a user with the given username already exists
        """

        if UsersRepository.get_user_by_username(username):
            raise UserAlreadyExistsError(
                f"User with username {username} already exists"
            )

        if location_id and LocationsRepository.get_location_by_id(location_id) is None:
            raise LocationDoesNotExist(
                f"Standort mit ID '{location_id}' existiert nicht"
            )

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

        :raises UserAlreadyExistsError: If a user with the given username already exists
        """

        if username != user.username and UsersRepository.get_user_by_username(username):
            raise UserAlreadyExistsError(
                f"User with username {username} already exists"
            )

        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.user_group = user_group
        user.location = location

        UsersRepository.update_user(user)

        return user

    @staticmethod
    def delete_user(user: User):
        """Delete a user from the database.

        :param user: The user to delete
        """
        leader_ids = {
            leader.id for leader in UsersRepository.get_group_and_location_leaders()
        }

        if user.id in leader_ids:
            raise UserCannotBeDeletedError(
                f"The user {user.first_name} {user.last_name} is a group or location leader and cannot be deleted right now."
            )

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
    def get_group_leader() -> list[User]:
        """Get all users with the user group 'gruppenleitung'"""

        return UsersRepository.get_group_leader()

    @staticmethod
    def get_location_leader() -> list[User]:
        """Get all users with the user group 'standortleitung'"""

        return UsersRepository.get_location_leader()
