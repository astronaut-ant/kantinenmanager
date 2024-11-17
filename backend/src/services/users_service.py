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


class UsersService:
    """Service for handling user management."""

    @staticmethod
    def get_users() -> list[User]:
        """Get all users saved in the database."""

        return UsersRepository.get_users()

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
        """

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
