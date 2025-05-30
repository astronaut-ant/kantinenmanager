import uuid
import sqlalchemy
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import db
from src.models.maindish import MainDish


class OldOrder(db.Model):
    __tablename__ = "old_order"

    """Model to represent an old order

    :param id: The order's ID as UUID4
    :param person_id: The person's ID (foreign key to the person table)
    :param date: The date of the order
    :param main_dish: The selected main dish
    :param salad_option: Whether a salad was included
    :param handed_out: Whether the order was handed out
    :param person: A reference to the person that made the order
    """

    # Felder der Tabelle:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    person_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "person.id",
            name="fk_oldorder_person",
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    location_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "location.id",
            name="fk_oldorder_location",
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
        nullable=False,
    )
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    nothing: Mapped[bool] = mapped_column(
        Boolean, name="nothing", nullable=True, quote=True
    )
    main_dish: Mapped[MainDish] = mapped_column(
        sqlalchemy.Enum(MainDish), nullable=True
    )
    salad_option: Mapped[bool] = mapped_column(Boolean, nullable=False)
    handed_out: Mapped[bool] = mapped_column(Boolean, nullable=True)

    # Beziehung zu anderen Tabellen:
    person: Mapped["Person"] = relationship(back_populates="old_orders")
    location: Mapped["Location"] = relationship(back_populates="old_orders")

    def __init__(
        self,
        location_id: uuid.UUID,
        date: datetime,
        nothing: bool,
        main_dish: MainDish,
        salad_option: bool,
        handed_out: bool,
        person_id: uuid.UUID = None,
    ):
        """Initialize a new old order

        :param person_id: The id of the person that made the order
        :param location_id: The id of the location of the order
        :param date: The date of the order
        :param nothing: Whether the order is empty
        :param main_dish: The selected main dish
        :param salad_option: Whether a salad is included
        :param handed_out: Whether the order was handed out
        """
        self.location_id = location_id
        self.date = date
        self.nothing = nothing
        self.main_dish = main_dish
        self.salad_option = salad_option
        self.handed_out = handed_out
        self.person_id = person_id

    def __repr__(self):
        return f"<OldOrder {self.id!r} {self.person_id!r} {self.date!r} {self.main_dish!r} {self.salad_option!r} {self.handed_out!r}>"

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "person_id": self.person_id,
            "location_id": self.location_id,
            "nothing": self.nothing,
            "main_dish": (self.main_dish.name if self.main_dish else None),
            "salad_option": self.salad_option,
            "handed_out": self.handed_out,
        }
