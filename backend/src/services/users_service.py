from src.services.auth_service import AuthService
from src.models.user import User, UserGroup
from src.repositories.users_repository import UsersRepository

# Services enthalten die Businesslogik der Anwendung.
# Sie werden von den Routen aufgerufen und ziehen sich
# die notwendigen Daten aus den Repositories.
#
# Hier würde so etwas reinkommen wie die Ertellung des QR-Codes
# oder die Validierung, dass ein Nutzer die korrekten Anmeldedaten
# eingegeben hat.


class UsersService:
    @staticmethod
    def get_users():
        return UsersRepository.get_users()

    @staticmethod
    def create_user(username: str, password: str, user_group: UserGroup) -> int:
        hashed_password = AuthService.hash_password(password)

        user = User(username=username, password=hashed_password, user_group=user_group)

        return UsersRepository.create_user(user)
