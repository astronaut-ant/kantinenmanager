"""Repository to handle database operations for refresh token data."""

from sqlalchemy import select
from src.models.refresh_token import RefreshToken
from src.database import db


class RefreshTokenRepository:
    """Repository to handle database operations for refresh token data."""

    @staticmethod
    def get_token(token: str) -> RefreshToken | None:
        """Retrieve a refresh token from the database

        :param token: The refresh token to retrieve

        :return: The refresh token with the given token or None if no token was found
        """

        return db.session.scalars(
            select(RefreshToken).where(RefreshToken.refresh_token == token)
        ).first()

    @staticmethod
    def create_token(token: RefreshToken):
        """Create a new refresh token in the database

        :param token: The refresh token to create
        """

        db.session.add(token)
        db.session.commit()

    @staticmethod
    def update_token(token: RefreshToken):
        """Update a refresh token in the database

        :param token: The refresh token to update
        """

        # SQLAlchemy automatically detects changes to the object and updates the database

        db.session.commit()
