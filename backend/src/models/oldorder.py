import uuid
import sqlalchemy
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import db
from src.models.person import Person
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
    person_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("person.id"))
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    main_dish: Mapped[MainDish] = mapped_column(
        sqlalchemy.Enum(MainDish), nullable=True
    )
    salad_option: Mapped[bool] = mapped_column(Boolean, nullable=False)
    handed_out: Mapped[bool] = mapped_column(Boolean, nullable=True)

    # Beziehung zu anderen Tabellen:
    person: Mapped["Person"] = relationship(back_populates="old_orders")

    def __init__(
        self,
        person: "Person",
        date: datetime,
        main_dish: MainDish,
        salad_option: bool,
        handed_out: bool,
    ):
        """Initialize a new old order

        :param person: The person that made the order
        :param date: The date of the order
        :param main_dish: The selected main dish
        :param salad_option: Whether a salad is included
        :param handed_out: Whether the order was handed out
        """
        self.person = person
        self.date = date
        self.main_dish = main_dish
        self.salad_option = salad_option
        self.handed_out = handed_out

    def __repr__(self):
        return f"<OldOrder {self.id!r} {self.person_id!r} {self.date!r} {self.main_dish!r} {self.salad_option!r} {self.handed_out!r}>"
