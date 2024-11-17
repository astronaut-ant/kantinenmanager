"""Service for authorization and session management."""

import jwt
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
from src.models.user import User
from src.repositories.users_repository import UsersRepository
from flask import current_app as app

AUDIENCE = "grp16-backend"
AUTH_DURATION = timedelta(minutes=10)


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
    def login(username: str, password: str) -> tuple[User, str, str]:
        """Validate user credentials

        :param username: The username of the user
        :param password: The password of the user

        :return: The user object, the Authentification token and the refresh token

        :raises auth_service.UserNotFoundException: If the user does not exist
        :raises auth_service.InvalidCredentialsException: If the password is incorrect
        """

        user = UsersRepository.get_user_by_username(username)
        if user is None:
            raise UserNotFoundException(f"User with username '{username}' not found")

        if not AuthService.check_password(password, user.hashed_password):
            raise InvalidCredentialsException("Invalid password")

        if AuthService.needs_rehash(user.hashed_password):
            user.hashed_password = AuthService.hash_password(password)
            # UsersRepository.update_user(user) # TODO: Implement update_user

        jwt_secret = app.config["JWT_SECRET"]
        if not jwt_secret:
            raise ValueError("JWT_SECRET not set in app config")

        jwt_str = AuthService.__make_jwt(user, jwt_secret)

        try:
            payload = AuthService.__verify_jwt(jwt_str, jwt_secret)
            print(payload)
        except jwt.PyJWTError as e:
            print(e)

        return user, jwt_str, ""

    def __make_jwt(user: User, jwt_secret: str) -> str:
        """Create a JWT token for a user

        :param user: The user to create the token for
        :param jwt_secret: The secret to sign the token with

        :return: The JWT token
        """

        payload = {
            "sub": str(user.id),  # subject
            "iat": datetime.now(tz=timezone.utc),  # issued at
            "exp": datetime.now(tz=timezone.utc) + AUTH_DURATION,  # expiration
            "aud": AUDIENCE,  # audience
            # "iss": "https://example.com",
            "app-username": user.username,
            "app-group": user.user_group.value,
        }

        return jwt.encode(payload, jwt_secret, algorithm="HS256")

    def __verify_jwt(encoded: str, jwt_secret: str) -> dict:
        """Verify a JWT token

        :param jwt: The JWT token to verify
        :param jwt_secret: The secret to verify the token with

        :return: The payload of the token

        Note: The base class for all PyJWT errors is jwt.PyJWTError

        :raises jwt.ExpiredSignatureError: If the token has expired
        :raises jwt.InvalidAudienceError: If the audience is invalid
        :raises jwt.InvalidIssuedAtError: If the issued at time is invalid
        :raises jwt.MissingRequiredClaimError: If a required claim is missing
        :raises jwt.InvalidSignatureError: If the signature is invalid
        """

        return jwt.decode(
            encoded,
            jwt_secret,
            algorithms=["HS256"],
            audience=AUDIENCE,
            options={
                "require": ["exp", "iat", "sub", "aud", "app-username", "app-group"]
            },
        )
