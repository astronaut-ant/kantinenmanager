"""Models related to storing user information."""

import enum
import sqlalchemy
import uuid
from datetime import datetime
from sqlalchemy import UUID, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from src.database import db

# Die Models repräsentieren die Datenstrukturen unserer Anwendung.
# Hier verwenden wir hauptsächlich SQLAlchemy und Flask-SQLAlchemy.
# https://flask-sqlalchemy.readthedocs.io/en/stable/quickstart/
# https://www.sqlalchemy.org/


class UserGroup(enum.Enum):
    """Enum to represent the different user groups in the application"""

    # The values need to be lowercase for validation to work
    verwaltung = "verwaltung"
    standortleitung = "standortleitung"
    gruppenleitung = "gruppenleitung"
    kuechenpersonal = "kuechenpersonal"


# Jede Klasse, die von db.Model erbt, wird auf eine Tabelle unserer
# Datenbank gemappt. Eine Instanz dieser Klasse kommt einer Zeile
# der Datenbank gleich.
class User(db.Model):
    """Model to represent a user

    :param id: The user's ID as UUID4
    :param first_name: The user's first name
    :param last_name: The user's last name
    :param username: The user's username for login
    :param hashed_password: The user's hashed password
    :param user_group: The user's group
    :param created: The date and time when the user was created
    :param last_login: The date and time when the user last logged in
    """

    # Das sind die Attribue (Spalten) der Tabelle:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str] = mapped_column(String(64), nullable=False)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)
    user_group: Mapped[UserGroup] = mapped_column(
        sqlalchemy.Enum(UserGroup), nullable=False
    )
    created: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_login: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    def __init__(
        self,
        first_name: str,
        last_name: str,
        username: str,
        hashed_password: str,
        user_group: UserGroup,
    ):
        """Initialize a new user

        :param first_name: The user's first name
        :param last_name: The user's last name
        :param username: The user's username for login
        :param hashed_password: The user's hashed password
        :param user_group: The user's group
        """

        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.hashed_password = hashed_password
        self.user_group = user_group
        self.created = datetime.now()
        self.last_login = None

    def __repr__(self):
        return f"<User {self.id!r} {self.username!r} {self.user_group.value!r}>"
