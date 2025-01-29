from datetime import datetime
from sqlalchemy import DateTime, Float
from sqlalchemy.orm import mapped_column, Mapped

from src.database import db


class DishPrice(db.Model):
    """Model to represent dish prices in history

    :param date: The starting date the prices are valid for
    :param main_dish_price: The price of the main dish
    :param salad_price: The price of the salad
    """

    date: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    main_dish_price: Mapped[float] = mapped_column(Float, nullable=False)
    salad_price: Mapped[float] = mapped_column(Float, nullable=False)

    def __rep__(self):
        return f"<DishPrice {self.date} {self.main_dish_price} {self.salad_price}>"
