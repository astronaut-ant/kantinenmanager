import enum
import sqlalchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from src.database import db

# Die Models repräsentieren die Datenstrukturen unserer Anwendung.
# Hier verwenden wir hauptsächlich SQLAlchemy und Flask-SQLAlchemy.
# https://flask-sqlalchemy.readthedocs.io/en/stable/quickstart/
# https://www.sqlalchemy.org/


class UserGroup(enum.Enum):
    verwaltung = "verwaltung"
    standortleitung = "standortleitung"
    gruppenleitung = "gruppenleitung"
    kuechenpersonal = "kuechenpersonal"


# Jede Klasse, die von db.Model erbt, wird auf eine Tabelle unserer
# Datenbank gemappt. Eine Instanz dieser Klasse kommt einer Zeile
# der Datenbank gleich.
class User(db.Model):
    # Das sind die Attribue (Spalten) der Tabelle:
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64))
    password: Mapped[str] = mapped_column(String(256))
    user_group: Mapped[UserGroup] = mapped_column(sqlalchemy.Enum(UserGroup))

    def __repr__(self):
        return f"<User {self.id!r} {self.username!r} {self.user_group!r}>"
