from src.models.user import User
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
    def create_user(user: User):
        return UsersRepository.create_user(user)

    @staticmethod
    def login(username, password):
        user = UsersRepository.get_user_by_username(username)
        print(user)
