"""Models related to storing location information."""

from typing import Set
import uuid
from sqlalchemy import UUID, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import db

# Die Models repräsentieren die Datenstrukturen unserer Anwendung.
# Hier verwenden wir hauptsächlich SQLAlchemy und Flask-SQLAlchemy.
# https://flask-sqlalchemy.readthedocs.io/en/stable/quickstart/
# https://www.sqlalchemy.org/


# Jede Klasse, die von db.Model erbt, wird auf eine Tabelle unserer
# Datenbank gemappt. Eine Instanz dieser Klasse kommt einer Zeile
# der Datenbank gleich.
class Location(db.Model):
    """Model to represent a location

    :param id: The location's ID as UUID4
    :param location_name: The loction's name
    :param location_leader: The ID of the location leader as UUID4
    :param location_leader: The location leader
    :param groups: The groups at the location
    """

    # Das sind die Attribue (Spalten) der Tabelle:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    location_name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    user_id_location_leader: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id"), nullable=False
    )

    # Das sind die Beziehungen zu anderen Tabellen:
    location_leader: Mapped["User"] = relationship(
        back_populates="leader_of_location",
        uselist=False,
        foreign_keys=[user_id_location_leader],
    )
    groups: Mapped[Set["Group"]] = relationship(back_populates="location")
    users: Mapped[Set["User"]] = relationship(
        back_populates="location", foreign_keys="User.location_id"
    )
    daily_orders: Mapped[Set["DailyOrder"]] = relationship(back_populates="location")
    pre_orders: Mapped[Set["PreOrder"]] = relationship(back_populates="location")
    old_orders: Mapped[Set["OldOrder"]] = relationship(back_populates="location")

    def __init__(
        self,
        location_name: str,
        user_id_location_leader: uuid.UUID,
    ):
        """Initialize a new location

        :param location_name: The loction's name
        :param user_id_location_leader: The ID of the location leader as UUID4
        """

        self.location_name = location_name
        self.user_id_location_leader = user_id_location_leader

    def __repr__(self):
        return f"<Location {self.id!r} {self.location_name!r}>"

    def to_dict(self) -> dict[str, str | int | bool]:
        """Convert the location to a dictionary

        All complex objects are converted to their string representation.

        :return: A dictionary containing the locations's information
        """

        return {
            "id": str(self.id),
            "location_name": self.location_name,
            "user_id_location_leader": str(self.user_id_location_leader),
        }
