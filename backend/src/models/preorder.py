import enum
import uuid
import sqlalchemy
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.person import Person
from src.database import db


class MainDish(enum.Enum):
    """Enum to represent the two different main dishes in the application"""

    # The values need to be lowercase for validation to work
    rot = "rot"
    blau = "blau"


class Preorder(db.Model):
    """Model to represent a preorder

    :param id: The order's ID as UUID4
    :param person_id: The person's ID (foreign key to the person table)
    :param date: The date of the preorder
    :param main_dish: The main dish selected
    :param salad_option: Whether a salad is included
    :param last_changed: The date and time when the order was last changed
    :param person: A reference to the person that made the order
    """

    # Das sind die Attribue (Spalten) der Tabelle:
    # Order ID
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    person_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("person.id"))
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    main_dish: Mapped[MainDish] = mapped_column(
        sqlalchemy.Enum(MainDish), nullable=True
    )
    salad_option: Mapped[bool] = mapped_column(Boolean, nullable=False)
    last_changed: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Das sind die Beziehungen zu anderen Tabellen:
    person: Mapped["Person"] = relationship(back_populates="preorders")

    def __init__(
        self,
        date: datetime,
        main_dish: MainDish,
        salad_option: bool,
        person: "Person",
    ):
        """Initialize a new preorder

        :param date: The date of the preorder
        :param main_dish: The selected main dish
        :param salad_option: Whether a salad is included
        :param person: The person that made the order
        """
        self.date = date
        self.main_dish = main_dish
        self.salad_option = salad_option
        self.last_changed = datetime.now()
        self.person = person

    def __repr__(self):
        return f"<PreOrder {self.id!r} {self.person_id!r} {self.date!r} {self.main_dish!r} {self.salad_option!r}>"
