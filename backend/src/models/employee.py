"""Models related to storing user information."""

import enum
from typing import Optional
import sqlalchemy
import uuid
from datetime import datetime
from sqlalchemy import UUID, Boolean, DateTime, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import db
from src.models.person import Person

# Die Models repräsentieren die Datenstrukturen unserer Anwendung.
# Hier verwenden wir hauptsächlich SQLAlchemy und Flask-SQLAlchemy.
# https://flask-sqlalchemy.readthedocs.io/en/stable/quickstart/
# https://www.sqlalchemy.org/


class Employee(Person):
    """Model to represent an employee

    :param id: The user's ID as UUID4
    :param employee_number: The employee's number that is used in the organisation
    :param group_id: The group number the employee is working at
    """

    # Das sind die Attribue (Spalten) der Tabelle:
    id: Mapped[uuid.UUID] = mapped_column(ForeignKey("person.id"), primary_key=True)
    employee_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("group.id"), nullable=False)

    # Das sind die Beziehungen zu anderen Tabellen:
    group: Mapped["Group"] = relationship(back_populates="employees")

    __mapper_args__ = {
        "polymorphic_identity": "employee",
    }

    def __init__(
        self, first_name: str, last_name: str, employee_number: int, group_id: int
    ):
        """Initialize a new employee

        :param first_name: The employee's first name
        :param last_name: The employee's last name
        :param employee_number: The employee's number that is used in the organisation
        :param group_id: The number of the group the employee is working in
        """

        super().__init__(first_name, last_name)
        self.employee_number = employee_number
        self.group_id = group_id

    def __repr__(self):
        return f"<Employee {self.id!r} {self.employee_number!r} {self.group_id!r}>"

    def to_dict(self) -> dict[str, str | int | bool]:
        """Convert the employee to a dictionary

        All complex objects are converted to their string representation.

        :return: A dictionary containing the employee's information
        """

        return {
            "id": str(self.id),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "employee_number": self.employee_number,
            "group_id": self.group_id,
            "created": self.created.timestamp(),
        }
