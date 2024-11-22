"""Models related to storing user information."""

import enum
import sqlalchemy
import uuid
from datetime import datetime
from sqlalchemy import UUID, Boolean, DateTime, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import db
from src.models.person import Person
from src.models.group import Group
from src.models.location import Location

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
class User(Person):
    """Model to represent a user

    :param id: The user's ID as UUID4
    :param username: The user's username for login
    :param hashed_password: The user's hashed password
    :param user_group: The user's group
    :param created: The date and time when the user was created
    :param last_login: The date and time when the user last logged in
    """

    # Das sind die Attribue (Spalten) der Tabelle:
    id: Mapped[uuid.UUID] = mapped_column(ForeignKey("person.id"), primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)
    user_group: Mapped[UserGroup] = mapped_column(
        sqlalchemy.Enum(UserGroup), nullable=False
    )
    last_login: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    blocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Das sind die Beziehungen zu anderen Tabellen:
    group: Mapped["Group"] = relationship(back_populates="group_leader", uselist=False)
    location: Mapped["Location"] = relationship(
        back_populates="location_leader", uselist=False
    )

    __mapper_args__ = {
        "polymorphic_identity": "user",
    }

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

        super().__init__(first_name, last_name)
        self.username = username
        self.hashed_password = hashed_password
        self.user_group = user_group
        self.last_login = None
        self.blocked = False

    def __repr__(self):
        return f"<User {self.id!r} {self.username!r} {self.user_group.value!r}>"

    def to_dict_without_pw_hash(self) -> dict[str, str | int | bool]:
        """Convert the user to a dictionary without the password hash

        All complex objects are converted to their string representation.

        :return: A dictionary containing the user's information
        """

        return {
            "id": str(self.id),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "user_group": self.user_group.value,
            "created": self.created.timestamp(),
            "last_login": self.last_login.timestamp() if self.last_login else 0,
            "blocked": self.blocked,
        }
