from src.models.user import User
from src.database import db


class UsersRepository:
    @staticmethod
    def create_user(user: User):
        db.session.add(user)
        db.session.commit()

        return user.id
