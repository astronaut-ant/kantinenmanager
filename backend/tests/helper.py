from datetime import datetime, timedelta
import uuid
import pytest

from src.models.dish_price import DishPrice
from src.models.group import Group
from src.models.location import Location
from src import app as project_app
from src.models.refresh_token_session import RefreshTokenSession
from src.models.user import User, UserGroup
from src.models.employee import Employee


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
def user_verwaltung():
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
def user_standortleitung():
    user = User(
        first_name="Standort",
        last_name="Leitung",
        username="standortleitung",
        hashed_password="$argon2id$v=19$m=65536,t=3,p=4$3rfCHeNLgFGKSyeZU0tl5w$rpsECi3FkYbvf2DEyPrDwp5/lPD3RUecZARuaRSVrWQ",  # password: password
        user_group=UserGroup.standortleitung,
    )
    user.id = uuid.uuid4()
    return user


@pytest.fixture()
def user_gruppenleitung():
    user = User(
        first_name="Gruppen",
        last_name="Leitung",
        username="gruppenleitung",
        hashed_password="$argon2id$v=19$m=65536,t=3,p=4$3rfCHeNLgFGKSyeZU0tl5w$rpsECi3FkYbvf2DEyPrDwp5/lPD3RUecZARuaRSVrWQ",  # password: password
        user_group=UserGroup.gruppenleitung,
    )
    user.id = uuid.uuid4()
    return user


@pytest.fixture()
def user_kuechenpersonal():
    user = User(
        first_name="Kuechen",
        last_name="Personal",
        username="kuechenpersonal",
        hashed_password="$argon2id$v=19$m=65536,t=3,p=4$3rfCHeNLgFGKSyeZU0tl5w$rpsECi3FkYbvf2DEyPrDwp5/lPD3RUecZARuaRSVrWQ",  # password: password
        user_group=UserGroup.kuechenpersonal,
    )
    user.id = uuid.uuid4()
    return user


@pytest.fixture()
def employee(group):
    employee = Employee(
        first_name="John",
        last_name="Doe",
        employee_number=12345,
        group_id=group.id,
    )
    employee.id = uuid.uuid4()
    employee.group = group
    return employee


@pytest.fixture()
def location(user_standortleitung):
    location = Location(
        location_name="Test Location", user_id_location_leader=user_standortleitung.id
    )
    location.id = uuid.uuid4()
    return location


@pytest.fixture()
def group(user_gruppenleitung, location):
    group = Group(
        group_name="Test Group",
        group_number=1,
        user_id_group_leader=user_gruppenleitung.id,
        user_id_replacement=None,
        location_id=location.id,
    )
    group.id = uuid.uuid4()
    return group


@pytest.fixture()
def session(user_verwaltung):
    return RefreshTokenSession(
        refresh_token="token",
        user_id=user_verwaltung.id,
        expires=datetime.now() + timedelta(days=1),
    )


@pytest.fixture()
def dish_price():
    return DishPrice(
        date=datetime.now(),
        main_dish_price=5.5,
        salad_price=2.5,
        prepayment=15.0,
    )
