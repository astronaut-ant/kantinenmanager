from datetime import datetime, timedelta
import uuid
import pytest

from src import app as project_app
from src.models.refresh_token_session import RefreshTokenSession
from src.models.user import User, UserGroup


# * Fixtures bieten eine Möglichkeit, Code zu schreiben, der von mehreren Tests verwendet wird.
# * Die unteren Fixtures erzeugen ein Objekt, das automatisch an die Tests übergeben wird,
# * wenn sie als Argument in der Testfunktion definiert sind.

PASSWORD = "password"
JWT_SECRET = "super_secret"


@pytest.fixture()
def app():
    project_app.config["JWT_SECRET"] = JWT_SECRET
    project_app.config["TESTING"] = True
    yield project_app


@pytest.fixture()
def user():
    user = User(
        first_name="Jane",
        last_name="Doe",
        username="janedoe",
        hashed_password="$argon2id$v=19$m=65536,t=3,p=4$3rfCHeNLgFGKSyeZU0tl5w$rpsECi3FkYbvf2DEyPrDwp5/lPD3RUecZARuaRSVrWQ",  # password: password
        user_group=UserGroup.verwaltung,
    )
    user.id = uuid.uuid4()
    return user


@pytest.fixture()
def session(user):
    return RefreshTokenSession(
        refresh_token="token",
        user_id=user.id,
        expires=datetime.now() + timedelta(days=1),
    )
