from src.models.user import User
from src.database import db

# Repositories kapseln den Zugriff auf die Datenbank. Sie enthalten die Logik,
# um Daten zu manipulieren und zu lesen.

# Hauptsächlich verwenden wir hier Methoden und Funktionalität vom ORM:
# SQLAlchemy: https://www.sqlalchemy.org/
# Damit SQLAlchemy besser mit Flask spielt, gibt es diese Extension:
# https://flask-sqlalchemy.readthedocs.io/en/stable/quickstart/


class UsersRepository:
    @staticmethod
    def get_users():
        return User.query.all()  # Gibt uns eine Liste aller User Objekte (von der DB)

    @staticmethod
    def create_user(user: User):
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
