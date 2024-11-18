"""Model to store refresh tokens for user authentication"""

from datetime import datetime
import sqlalchemy
import uuid
from src.database import db
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column


class RefreshToken(db.Model):
    """Model to represent a refresh token for user authentication

    Refresh tokens are used to generate new access tokens when the old ones expire.
    The database stores all active refresh tokens along with some metadata. The
    browser stores and sends the primary key ('refresh_token') to the server.

    Refresh tokens are long-lived and will be rotated after use. When a refresh token
    is used twice, the user account will be locked.

    :param refresh_token: The token the browser will store
    :param user_id: The ID of the user this token is associated with
    :param created: The date and time when the token was created
    :param expires: The date and time when the token expires
    :param last_used: The date and time when the token was last used. None if never used
    """

    refresh_token: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        sqlalchemy.UUID(as_uuid=True), nullable=False
    )
    created: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expires: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_used: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    def __init__(self, refresh_token: str, user_id: uuid.UUID, expires: datetime):
        """Initialize a new refresh token

        :param refresh_token: The refresh token
        :param user_id: The ID of the user this token is associated with
        """

        self.refresh_token = refresh_token
        self.user_id = user_id
        self.created = datetime.now()
        self.expires = expires
        self.last_used = None

    def __repr__(self):
        return f"<RefreshToken {self.refresh_token}>"

    def has_been_used(self):
        """Check if the refresh token has been used before

        :return: True if the token has been used, False otherwise
        """

        return self.last_used is not None
