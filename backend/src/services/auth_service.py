"""Service for authorization and session management."""

from src.models.user import User
from src.repositories.users_repository import UsersRepository


class UserNotFoundException(Exception):
    """User does not exist"""

    pass


class InvalidCredentialsException(Exception):
    """User credentials are invalid"""

    pass


class AuthService:
    """Service for user authentication"""

    @staticmethod
    def login(username: str, password: str) -> User:
        """Validate user credentials

        Args:
            username: The username of the user
            password: The password of the user

        Returns:
            The user object if the credentials are valid

        Raises:
            UserNotFoundException: If the user does not exist
            InvalidCredentialsException: If the password is incorrect
        """

        # todo
        user = UsersRepository.get_user_by_username(username)
        if user is None:
            raise UserNotFoundException(f"User with username '{username}' not found")

        if user.password != password:
            raise InvalidCredentialsException("Invalid password")

        return user
