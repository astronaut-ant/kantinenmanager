"""Repository to handle database operations for user data."""

from sqlalchemy import select
from src.models.user import User
from src.database import db

# Repositories kapseln den Zugriff auf die Datenbank. Sie enthalten die Logik,
# um Daten zu manipulieren und zu lesen.

# Hauptsächlich verwenden wir hier Methoden und Funktionalität vom ORM:
# SQLAlchemy: https://www.sqlalchemy.org/
# Damit SQLAlchemy besser mit Flask spielt, gibt es diese Extension:
# https://flask-sqlalchemy.readthedocs.io/en/stable/quickstart/


class UsersRepository:
    """Repository to handle database operations for user data."""

    @staticmethod
    def get_users():
        """Get all users saved in the database"""
        return db.session.scalars(select(User)).all()

    @staticmethod
    def create_user(user: User):
        """Create a new user in the database"""
        db.session.add(
            user
        )  # Beginne eine neue DB-Transaktion und speichere user in DB
        db.session.commit()  # Führe COMMIT aus, um die Transaktion abzuschließen
        # Bei beiden werden unter der Haube SQL-Statements generiert und an die DB gesendet.

        # Die ID Spalte hat 'AUTO INCREMENT' gesetzt. Jedes eingefügte Element erhält
        # eine neue, hochgezählte ID.
        # SQLAlchemy synchronisiert obiges `user` Objekt mit der DB. Wir haben jetzt also
        # Zugriff auf die zugewiesene ID.
        return user.id

    @staticmethod
    def get_user_by_username(username) -> User | None:
        """Retrieve a user by their username"""

        return db.session.scalars(select(User).where(User.username == username)).first()
