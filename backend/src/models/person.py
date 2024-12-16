"""Models related to storing user information."""

import uuid
from typing import List
from datetime import datetime
from sqlalchemy import UUID, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import db

# Die Models repräsentieren die Datenstrukturen unserer Anwendung.
# Hier verwenden wir hauptsächlich SQLAlchemy und Flask-SQLAlchemy.
# https://flask-sqlalchemy.readthedocs.io/en/stable/quickstart/
# https://www.sqlalchemy.org/


class Person(db.Model):
    """Model to represent a person that uses the system

    :param id: The user's ID as UUID4
    :param first_name: The user's first name
    :param last_name: The user's last name
    """

    # Das sind die Attribue (Spalten) der Tabelle:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str] = mapped_column(String(64), nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    type: Mapped[str]

    # Das sind die Beziehungen zu anderen Tabellen (SQLAlchemy löst den import, auch wenn Fehler angezeigt wird):
    pre_orders: Mapped[List["PreOrder"]] = relationship(
        back_populates="person", cascade="all, delete-orphan"
    )
    daily_orders: Mapped[List["DailyOrder"]] = relationship(
        back_populates="person", cascade="all, delete-orphan"
    )
    old_orders: Mapped[List["OldOrder"]] = relationship(
        back_populates="person",
        passive_deletes=True,
    )

    # __mapper_args__ ist ein spezielles Attribut, das SQLAlchemy verwendet, um
    # Informationen über die Vererbungshierarchie zu speichern. In diesem Fall
    # wird es verwendet, um die Klasse Person als Basisklasse für die Klasse
    # Employee und User zu kennzeichnen.
    __mapper_args__ = {
        "polymorphic_identity": "person",
        "polymorphic_on": "type",
    }

    def __init__(
        self,
        first_name: str,
        last_name: str,
    ):
        """Initialize a new person

        :param first_name: The user's first name
        :param last_name: The user's last name
        """

        self.first_name = first_name
        self.last_name = last_name
        self.created = datetime.now()

    def __repr__(self):
        return f"<Person {self.id!r}>"
