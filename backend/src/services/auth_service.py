"""Service for authorization and session management."""

from argon2 import PasswordHasher
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
    def hash_password(password: str) -> str:
        """Hash a password

        :param password: The password to hash

        :return: The hashed password
        """

        ph = AuthService.__get_password_hasher()

        return ph.hash(password)

    @staticmethod
    def check_password(password: str, hash: str) -> bool:
        """Check if a password matches a hash

        :param password: The password to check
        :param hash: The hashed password

        :return: True if the password matches the hash
        """

        ph = AuthService.__get_password_hasher()

        try:
            ph.verify(hash, password)
            return True
        except Exception:
            return False

    @staticmethod
    def needs_rehash(hash: str) -> bool:
        """Check if a password hash needs to be rehashed

        :param hash: The hashed password

        :return: True if the hash needs to be rehashed
        """

        ph = AuthService.__get_password_hasher()

        return ph.check_needs_rehash(hash)

    @staticmethod
    def __get_password_hasher() -> PasswordHasher:
        """Get a password hasher with configured settings"""

        return PasswordHasher()

    @staticmethod
    def login(username: str, password: str) -> User:
        """Validate user credentials

        :param username: The username of the user
        :param password: The password of the user

        :return: The user object if the credentials are valid

        :raises auth_service.UserNotFoundException: If the user does not exist
        :raises auth_service.InvalidCredentialsException: If the password is incorrect
        """

        user = UsersRepository.get_user_by_username(username)
        if user is None:
            raise UserNotFoundException(f"User with username '{username}' not found")

        if not AuthService.check_password(password, user.password):
            raise InvalidCredentialsException("Invalid password")

        if AuthService.needs_rehash(user.password):
            user.password = AuthService.hash_password(password)
            # UsersRepository.update_user(user) # TODO: Implement update_user

        return user
