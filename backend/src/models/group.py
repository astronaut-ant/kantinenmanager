import sqlalchemy
import uuid
from typing import Set
from sqlalchemy import UUID, Boolean, DateTime, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import db
from src.models.user import User
from src.models.location import Location
from src.models.location import Employee


class Group(db.Model):
    """Model to represent a group

    :param id: The groups ID as UUID4
    :param group_name: The Name of the Group
    :param user_id_groupleader: The ID of the Groupleader as UUID4
    :param user_id_replacement: The ID of the Replacement for the Groupleader as UUID4 else none
    :param location_id: The ID of the Location containing the Group
    """

    # Das sind die Attribue (Spalten) der Tabelle:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    group_name: Mapped[str] = mapped_column(String(64), nullable=False)
    user_id_groupleader: Mapped[uuid.UUID] = relationship(
        ForeignKey(User.id), nullable=False
    )
    user_id_replacement: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(User.id), nullable=True
    )
    location_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(Location.id), nullable=False
    )

    # Das sind die Beziehungen zu anderen Tabellen:
    employees: Mapped[Set["Employee"]] = relationship(back_populates="group")
    group_leader: Mapped["User"] = relationship(back_populates="group")

    def __init__(
        self,
        group_name: str,
        user_id_groupleader: uuid.UUID,
        location_id: uuid.UUID,
    ):
        """Initialize a new group

        :param group_name: Name of the Group
        :param user_id_groupleader: ID of the Groupleader
        :param location_id: ID of the Location
        """

        self.group_name = group_name
        self.user_id_groupleader = user_id_groupleader
        location_id = location_id

    def __repr__(self):
        return f"<Group {self.id!r} {self.group_name!r} {self.user_id_groupleader!r} {self.user_id_replacement} {self.location_id}>"
