import uuid
import sqlalchemy
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import db
from src.models.maindish import MainDish


class PreOrder(db.Model):
    __tablename__ = "pre_order"

    """Model to represent a preorder

    :param id: The pre-order's ID as UUID4
    :param person_id: The person's ID (foreign key to the person table)
    :param date: The date of the pre-order
    :param main_dish: The selected main dish
    :param salad_option: Whether a salad is included
    :param last_changed: The date and time when the order was last changed
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
    last_changed: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Beziehung zu anderen Tabellen:
    person: Mapped["Person"] = relationship(back_populates="pre_orders")

    def __init__(
        self,
        date: datetime,
        main_dish: MainDish,
        salad_option: bool,
        person: "Person",
    ):
        """Initialize a new pre-order

        :param date: The date of the pre-order
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
        return f"<Pre-Order {self.id!r} {self.person_id!r} {self.date!r} {self.main_dish!r} {self.salad_option!r}>"
