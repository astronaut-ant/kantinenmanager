from src.models.user import User
from src.repositories.users_repository import UsersRepository


class UsersService:
    @staticmethod
    def create_user(user: User):
        return UsersRepository.create_user(user)
