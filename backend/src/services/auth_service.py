"""Service for authorization and session management."""

from uuid import UUID
import jwt
import secrets
from datetime import datetime, timezone
from argon2 import PasswordHasher
from src.constants import (
    AUTHENTICATION_TOKEN_AUDIENCE,
    AUTHENTICATION_TOKEN_DURATION,
    GEN_PASSWORD_ALPHABET,
    GEN_PASSWORD_LENGTH,
    REFRESH_TOKEN_DURATION,
    REFRESH_TOKEN_LENGTH,
)
from src.repositories.refresh_token_session_repository import (
    RefreshTokenSessionRepository,
)
from src.models.refresh_token_session import RefreshTokenSession
from src.models.user import User, UserGroup
from src.repositories.users_repository import UsersRepository
from src.utils.exceptions import (
    UserBlockedError,
    NotFoundError,
    InvalidCredentialsException,
    UnauthenticatedException,
)
from flask import current_app as app


class AuthService:
    """Service to handle user authentication"""

    @staticmethod
    def login(username: str, password: str) -> tuple[User, str, str]:
        """Validate user credentials

        :param username: The username of the user
        :param password: The password of the user

        :return: The user object, the authentication token and the refresh token

        :raises auth_service.NotFoundError: If the user does not exist
        :raises auth_service.InvalidCredentialsException: If the password is incorrect
        """

        # Fetch user from DB
        user = UsersRepository.get_user_by_username(username)
        if user is None:
            raise NotFoundError(f"Nutzer:in '{username}'")

        # Check password
        if not AuthService.__check_password(password, user.hashed_password):
            raise InvalidCredentialsException("Invalid password")

        # Rehash password if necessary
        if AuthService.__needs_rehash(user.hashed_password):
            user.hashed_password = AuthService.hash_password(password)

        user.last_login = datetime.now()
        UsersRepository.update_user(user)

        if user.blocked:
            # blocked message should be displayed only for the right user,
            # so not to give away information about the existence of the user
            raise UserBlockedError("Account von Nutzer:in ist gesperrt.")

        # Create authentication and refresh tokens
        jwt_secret = app.config["JWT_SECRET"]
        if not jwt_secret:
            raise ValueError("JWT_SECRET not set in app config")

        auth_token = AuthService.__make_auth_token(user, jwt_secret)
        refresh_token = AuthService.__make_refresh_token(user)

        app.logger.info("New successful login")

        return user, auth_token, refresh_token

    @staticmethod
    def authenticate(
        auth_token: str | None, refresh_token: str | None
    ) -> tuple[dict, str, str] | tuple[dict, None, None]:
        """Authenticate a user

        If the authentication token is valid (signed and not expired),
        the user is authenticated and the user's data is returned.

        Otherwise, the refresh token is used to generate a new authentication token.
        A rotation of refresh tokens is implemented to prevent replay attacks. Both
        new tokens are returned to be stored on the clients side.

        If the refresh token is simply invalid, an UnauthenticatedException is raised.
        When the refresh token was used before, the user account will be locked.

        :param auth_token: The authentication token
        :param refresh_token: The refresh token

        :return: Dict with user data, new auth token or None, new refresh token or None

        When the returned tokens are None, the old tokens remain valid and should not be replaced.

        :raises auth_service.UnauthenticatedException: If the user is not authenticated
        """

        # Get JWT secret to verify auth token
        jwt_secret = app.config.get("JWT_SECRET")
        if not jwt_secret:
            raise ValueError("JWT_SECRET not set in app config")

        # Validate auth token
        if auth_token is not None:
            try:
                payload = AuthService.__verify_auth_token(auth_token, jwt_secret)

                user_info = {
                    "id": UUID(payload.get("sub")),
                    "username": payload.get("app-username"),
                    "group": UserGroup[payload.get("app-group")],
                    "first_name": payload.get("app-first-name"),
                    "last_name": payload.get("app-last-name"),
                }

                return user_info, None, None
            except jwt.PyJWTError:
                # Auth token is invalid
                # That's fine, we can try to refresh the token with the refresh token
                pass

        # Validate refresh token

        if refresh_token is None:
            raise UnauthenticatedException("No refresh token provided")

        session = RefreshTokenSessionRepository.get_token(refresh_token)

        if session is None:
            raise UnauthenticatedException("Refresh token not found in DB")

        if session.expires < datetime.now():
            raise UnauthenticatedException("Refresh token expired")

        if session.has_been_used():
            # Block user
            user = UsersRepository.get_user_by_id(session.user_id)
            if user is None:
                raise UnauthenticatedException("Nutzer nicht gefunden.")
            user.blocked = True
            UsersRepository.update_user(user)
            app.logger.warning(
                f"User account '{user.username}' with id '{session.user_id}' blocked due to repeated refresh token usage"
            )
            raise UserBlockedError("Refresh Token wurde bereits verwendet.")

        # Generate new tokens
        user = UsersRepository.get_user_by_id(session.user_id)

        if user is None:
            raise UnauthenticatedException("Nutzer nicht gefunden.")

        if user.blocked:
            raise UserBlockedError("Account von Nutzer:in ist gesperrt.")

        new_auth_token = AuthService.__make_auth_token(user, jwt_secret)
        new_refresh_token = AuthService.__make_refresh_token(user)

        # Mark old refresh token as used
        session.last_used = datetime.now()
        RefreshTokenSessionRepository.update_token(session)

        user_info = {
            "id": user.id,
            "username": user.username,
            "group": user.user_group,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }

        return user_info, new_auth_token, new_refresh_token

    @staticmethod
    def logout(refresh_token: str):
        """Log out the user by deleting the refresh token"""

        session = RefreshTokenSessionRepository.get_token(refresh_token)
        if session is not None:
            RefreshTokenSessionRepository.delete_token(session)

    @staticmethod
    def change_password(user_id: UUID, old_password: str, new_password: str):
        """Change the password of a user

        :param user_id: The ID of the user
        :param old_password: The current password
        :param new_password: The new password

        :raises auth_service.NotFoundError: If the user does not exist
        :raises auth_service.InvalidCredentialsException: If the old password is incorrect
        """

        # Fetch user from DB
        user = UsersRepository.get_user_by_id(user_id)
        if user is None:
            raise NotFoundError(f"Nutzer:in mit ID '{user_id}'")

        # Check password
        if not AuthService.__check_password(old_password, user.hashed_password):
            raise InvalidCredentialsException("Invalid password")

        # Set new password
        user.hashed_password = AuthService.hash_password(new_password)
        UsersRepository.update_user(user)

        # Invalidate all sessions
        AuthService.invalidate_all_refresh_tokens(user_id)

    @staticmethod
    def invalidate_all_refresh_tokens(user_id: UUID):
        """Invalidate all refresh tokens for a user

        Warning: This will only keep users from obtaining new auth tokens.
        Existing auth tokens will remain valid until they expire.

        :param user_id: The ID of the user whose tokens to invalidate
        """

        RefreshTokenSessionRepository.delete_user_tokens(user_id)

    @staticmethod
    def generate_password() -> str:
        """Generate a random password

        :return: The generated password
        """

        return "".join(
            secrets.choice(GEN_PASSWORD_ALPHABET) for _ in range(GEN_PASSWORD_LENGTH)
        )

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password

        :param password: The password to hash

        :return: The hashed password
        """

        ph = AuthService.__get_password_hasher()

        return ph.hash(password)

    @staticmethod
    def __check_password(password: str, hash: str) -> bool:
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
    def __needs_rehash(hash: str) -> bool:
        """Check if a password hash needs to be rehashed

        Passwords need to be rehashed when the Argon2 parameters change.

        :param hash: The hashed password

        :return: True if the hash needs to be rehashed
        """

        ph = AuthService.__get_password_hasher()

        return ph.check_needs_rehash(hash)

    @staticmethod
    def __get_password_hasher() -> PasswordHasher:
        """Get a password hasher with configured settings"""

        # Use sensible defaults for Argon2
        return PasswordHasher()

    @staticmethod
    def __make_auth_token(user: User, jwt_secret: str) -> str:
        """Create an authentication token

        :param user: The user to create the token for
        :param jwt_secret: The secret to sign the token with

        :return: The authentication token
        """

        payload = {
            "sub": str(user.id),  # subject
            "iat": datetime.now(tz=timezone.utc),  # issued at
            "exp": datetime.now(tz=timezone.utc)
            + AUTHENTICATION_TOKEN_DURATION,  # expiration
            "aud": AUTHENTICATION_TOKEN_AUDIENCE,  # audience
            # "iss": "https://example.com",
            "app-username": user.username,
            "app-group": user.user_group.value,
            "app-first-name": user.first_name,
            "app-last-name": user.last_name,
        }

        return jwt.encode(payload, jwt_secret, algorithm="HS256")

    @staticmethod
    def __verify_auth_token(encoded: str, jwt_secret: str) -> dict:
        """Verify an authentication token

        :param encoded: The JWT token to verify
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
            audience=AUTHENTICATION_TOKEN_AUDIENCE,
            options={
                "require": [
                    "exp",
                    "iat",
                    "sub",
                    "aud",
                    "app-username",
                    "app-group",
                    "app-first-name",
                    "app-last-name",
                ]
            },
        )

    @staticmethod
    def __make_refresh_token(user: User) -> str:
        """Create a refresh token for a user

        :param user: The user to create the token for

        :return: The refresh token
        """

        # Generate random token
        token = secrets.token_hex(REFRESH_TOKEN_LENGTH // 2)

        # Regenerate token if it already exists
        while RefreshTokenSessionRepository.get_token(token) is not None:
            token = secrets.token_hex(REFRESH_TOKEN_LENGTH // 2)

        expires = datetime.now() + REFRESH_TOKEN_DURATION

        session = RefreshTokenSession(
            refresh_token=token, user_id=user.id, expires=expires
        )

        RefreshTokenSessionRepository.create_token(session)

        return session.refresh_token
