import uuid
from typing import Set
from sqlalchemy import UUID, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import db


class Group(db.Model):
    """Model to represent a group

    :param id: The groups ID as UUID4
    :param group_name: The Name of the Group
    :param user_id_group_leader: The ID of the group leader as UUID4
    :param user_id_replacement: The ID of the Replacement for the group leader as UUID4 else none
    :param location_id: The ID of the Location containing the Group
    :param employees: The employees working in the group
    :param group_leader: The group leader
    :param group_leader_replacement: The Replacement for the group leader
    :param location: The Location containing the Group
    """

    # Das sind die Attribue (Spalten) der Tabelle:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    group_name: Mapped[str] = mapped_column(String(64), nullable=False)
    user_id_group_leader: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id"), nullable=False
    )
    user_id_replacement: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id"), nullable=True
    )
    location_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("location.id"), nullable=False
    )

    # Das sind die Beziehungen zu anderen Tabellen:
    employees: Mapped[Set["Employee"]] = relationship(back_populates="group")
    group_leader: Mapped["User"] = relationship(
        back_populates="leader_of_group", foreign_keys=[user_id_group_leader]
    )
    group_leader_replacement: Mapped["User"] = relationship(
        back_populates="replacement_leader_of_groups",
        foreign_keys=[user_id_replacement],
    )
    location: Mapped["Location"] = relationship(back_populates="groups")

    def __init__(
        self,
        group_name: str,
        user_id_group_leader: uuid.UUID,
        user_id_replacement: uuid.UUID,
        location_id: uuid.UUID,
    ):
        """Initialize a new group

        :param group_name: Name of the Group
        """
        self.group_name = group_name
        self.user_id_group_leader = user_id_group_leader
        self.user_id_replacement = user_id_replacement
        self.location_id = location_id

    def __repr__(self):
        return f"<Group {self.id!r} {self.group_name!r}>"

    def to_dict(self) -> dict[str, str | int | bool]:
        """Convert the group to a dictionary

        All complex objects are converted to their string representation.

        :return: A dictionary containing the group's information
        """

        return {
            "id": str(self.id),
            "group_name": self.group_name,
            "user_id_group_leader": str(self.user_id_group_leader),
            "user_id_replacement": str(self.user_id_replacement),
            "location_id": str(self.location_id),
        }
