from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


# Von dieser Klasse erben selbstdefinierten SQLAlchemy Models.
# Das ist notwendig, damit unsere Models in Base.metadata
# registriert werden und somit SQLAlchemy weiß, welche Tabellen
# es in der Datenbank erstellen muss.
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base, engine_options={"echo": True})


def init_db(app):
    db.init_app(app)

    import src.models.user
    import src.models.employee
    import src.models.person

    import src.models.group
    import src.models.location

    import src.models.preorder

    with app.app_context():
        # Hier werden alle Tabellen erstellt, zu denen
        # SQL-Alchemy Models finden kann. Das ist erstmal nur
        # temporär. Später würde man das mit DB-Migrationen
        # machen.
        db.create_all()
