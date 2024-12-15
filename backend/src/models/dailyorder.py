import uuid
import sqlalchemy
from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import db
from src.models.maindish import MainDish


class DailyOrder(db.Model):
    __tablename__ = "daily_order"

    """Model to represent a daily order

    :param id: The order's ID as UUID4
    :param person_id: The person's ID (foreign key to the person table)
    :param main_dish: The main dish selected
    :param salad_option: Whether a salad is included
    :param handed_out: Whether the order has been handed out
    :param person: A reference to the person that made the order
    """

    # Felder der Tabelle:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    person_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("person.id"))  # unique=True
    location_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("location.id"))
    nothing: Mapped[bool] = mapped_column(
        Boolean, name="nothing", nullable=True, quote=True
    )
    main_dish: Mapped[MainDish] = mapped_column(
        sqlalchemy.Enum(MainDish), nullable=True
    )
    salad_option: Mapped[bool] = mapped_column(Boolean, nullable=False)
    handed_out: Mapped[bool] = mapped_column(Boolean, nullable=True)

    # Beziehung zu anderen Tabellen:
    person: Mapped["Person"] = relationship(back_populates="daily_orders")
    location: Mapped["Location"] = relationship(back_populates="daily_orders")

    def __init__(
        self,
        person_id: uuid.UUID,
        location_id: uuid.UUID,
        nothing: bool,
        main_dish: MainDish,
        salad_option: bool,
        handed_out: bool = False,
    ):
        """Initialize a new daily order

        :param person_id: The person that made the order
        :param location_id: The location the order is for
        :param nothing: Weather the order is empty or not
        :param main_dish: The selected main dish
        :param salad_option: Whether a salad is included
        :param handed_out: Whether the order has been handed out
        """
        self.person_id = person_id
        self.location_id = location_id
        self.nothing = nothing
        self.main_dish = main_dish
        self.salad_option = salad_option
        self.handed_out = handed_out

    def __repr__(self):
        return f"<DailyOrder {self.id!r} {self.person_id!r} {self.main_dish!r} {self.salad_option!r} {self.handed_out!r}>"

    def to_dict(self):
        return {
            "id": self.id,
            "person_id": self.person_id,
            "location_id": self.location_id,
            "nothing": self.nothing,
            "main_dish": self.main_dish,
            "salad_option": self.salad_option,
            "handed_out": self.handed_out,
        }
