"""Models related to storing employee information."""

from typing import Optional
import uuid
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.person import Person

# Die Models repräsentieren die Datenstrukturen unserer Anwendung.
# Hier verwenden wir hauptsächlich SQLAlchemy und Flask-SQLAlchemy.
# https://flask-sqlalchemy.readthedocs.io/en/stable/quickstart/
# https://www.sqlalchemy.org/


class Employee(Person):
    """Model to represent an employee

    :param id: The employee's ID as UUID4
    :param first_name: The employee's first name
    :param last_name: The employee's last name
    :param employee_number: The employee's number that is used in the organisation
    :param group_id: The group ID the employee is working at
    :param group: A reference to the group the employee is working in
    :param created: The date and time when the employee was created
    """

    # Das sind die Attribue (Spalten) der Tabelle:
    id: Mapped[uuid.UUID] = mapped_column(ForeignKey("person.id"), primary_key=True)
    employee_number: Mapped[int] = mapped_column(Integer, nullable=False)
    group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("group.id"), nullable=False)

    # Das sind die Beziehungen zu anderen Tabellen:
    group: Mapped["Group"] = relationship(back_populates="employees")

    __mapper_args__ = {
        "polymorphic_identity": "employee",
    }

    def __init__(
        self, first_name: str, last_name: str, employee_number: int, group_id: uuid.UUID
    ):
        """Initialize a new employee

        :param first_name: The employee's first name
        :param last_name: The employee's last name
        :param employee_number: The employee's number that is used in the organisation
        :param group_id: The group ID the employee is working at
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
            "created": self.created.timestamp(),
            "group": self.group.to_dict(),
        }

    def to_dict_reduced(self) -> dict[str, str | int | bool]:
        """Convert the employee to a dictionary with reduced information

        All complex objects are converted to their string representation.

        :return: A dictionary containing the employee's information
        """

        return {
            "id": str(self.id),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "employee_number": self.employee_number,
        }
