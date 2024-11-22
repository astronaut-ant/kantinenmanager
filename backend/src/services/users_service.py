"""Service for handling user management."""

from uuid import UUID
from src.services.auth_service import AuthService
from src.models.user import User, UserGroup
from src.repositories.users_repository import UsersRepository

# Services enthalten die Businesslogik der Anwendung.
# Sie werden von den Routen aufgerufen und ziehen sich
# die notwendigen Daten aus den Repositories.
#
# Hier würde so etwas reinkommen wie die Ertellung des QR-Codes
# oder die Validierung, dass ein Nutzer die korrekten Anmeldedaten
# eingegeben hat.


class UserAlreadyExistsError(Exception):
    """Exception raised when a username is already taken."""

    pass


class UsersService:
    """Service for handling user management."""

    @staticmethod
    def get_users() -> list[User]:
        """Get all users saved in the database."""

        return UsersRepository.get_users()

    @staticmethod
    def get_user_by_id(user_id: UUID) -> User | None:
        """Retrieve a user by their ID

        :param user_id: The ID of the user to retrieve

        :return: The user with the given ID or None if no user was found
        """

        return UsersRepository.get_user_by_id(user_id)

    @staticmethod
    def create_user(
        first_name: str,
        last_name: str,
        username: str,
        password: str,
        user_group: UserGroup,
    ) -> tuple[UUID, str]:
        """Create a new user in the database.

        :param first_name: The first name of the new user
        :param last_name: The last name of the new user
        :param username: The username of the new user
        :param password: The password of the new user
        :param user_group: The user group of the new user

        :return: A tuple containing the ID of the new user and the initial password

        :raises UserAlreadyExistsError: If a user with the given username already exists
        """

        if UsersRepository.get_user_by_username(username):
            raise UserAlreadyExistsError(
                f"User with username {username} already exists"
            )

        hashed_password = AuthService.hash_password(password)

        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            hashed_password=hashed_password,
            user_group=user_group,
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
    ):
        """Update a user in the database.

        :param user: The user to update
        :param first_name: The new first name of the user
        :param last_name: The new last name of the user
        :param username: The new username of the user
        :param user_group: The new user group of the user
        """

        if username != user.username and UsersRepository.get_user_by_username(username):
            raise UserAlreadyExistsError(
                f"User with username {username} already exists"
            )

        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.user_group = user_group

        UsersRepository.update_user(user)

    @staticmethod
    def delete_user(user: User):
        """Delete a user from the database.

        :param user_id: The ID of the user to delete
        """

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
