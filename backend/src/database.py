from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase


# Von dieser Klasse erben selbstdefinierten SQLAlchemy Models.
# Das ist notwendig, damit unsere Models in Base.metadata
# registriert werden und somit SQLAlchemy weiß, welche Tabellen
# es in der Datenbank erstellen muss.
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base, engine_options={"echo": True})


def init_db(app: Flask):
    db.init_app(app)

    import src.models.user
    import src.models.employee
    import src.models.person

    import src.models.group
    import src.models.location

    import src.models.preorder
    import src.models.dailyorder
    import src.models.oldorder

    with app.app_context():
        # Hier werden alle Tabellen erstellt, zu denen
        # SQL-Alchemy Models finden kann. Das ist erstmal nur
        # temporär. Später würde man das mit DB-Migrationen
        # machen.
        db.create_all()


def create_initial_admin(app: Flask, username: str, password: str):
    """Create an initial admin user if no users of group 'verwaltung' exist yet."""

    from src.models.user import UserGroup
    from src.repositories.users_repository import UsersRepository
    from src.services.users_service import UsersService

    with app.app_context():
        users = UsersRepository.get_users_by_user_group(UserGroup.verwaltung)

        if len(users) > 0:
            return

        UsersService.create_user(
            first_name=username,
            last_name=username,
            username=username,
            password=password,
            user_group=UserGroup.verwaltung,
        )

        print(f"Created initial admin user {username}")


def check_db_connection():
    """Check if the database connection is working."""

    try:
        db.session.execute(text("SELECT 1"))
    except Exception as e:
        print("Database connection failed")
        print(e)
        return False
    return True
