"""Repository to handle database operations for refresh token sessions."""

from sqlalchemy import select
from src.models.refresh_token_session import RefreshTokenSession
from src.database import db


class RefreshTokenSessionRepository:
    """Repository to handle database operations for refresh token sessions."""

    @staticmethod
    def get_token(token: str) -> RefreshTokenSession | None:
        """Retrieve a refresh token from the database

        :param token: The refresh token to retrieve

        :return: The refresh token with the given token or None if no token was found
        """

        return db.session.scalars(
            select(RefreshTokenSession).where(
                RefreshTokenSession.refresh_token == token
            )
        ).first()

    @staticmethod
    def create_token(token: RefreshTokenSession):
        """Create a new refresh token in the database

        :param token: The refresh token to create
        """

        db.session.add(token)
        db.session.commit()

    @staticmethod
    def update_token(token: RefreshTokenSession):
        """Update a refresh token in the database

        :param token: The refresh token to update
        """

        # SQLAlchemy automatically detects changes to the object and updates the database

        db.session.commit()

    @staticmethod
    def delete_token(token: str):
        """Delete a refresh token from the database

        :param token: The refresh token to delete
        """

        raise NotImplementedError("Not implemented yet")
