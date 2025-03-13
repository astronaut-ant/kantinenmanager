from datetime import datetime, timedelta, date
import uuid
import pytest

from src.models.dish_price import DishPrice
from src.models.group import Group
from src.models.location import Location
from src import app as project_app
from src.models.refresh_token_session import RefreshTokenSession
from src.models.user import User, UserGroup
from src.models.employee import Employee
from src.models.preorder import PreOrder
from src.models.maindish import MainDish
from src.models.oldorder import OldOrder
from src.models.person import Person


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
def user_gruppenleitung_alt():
    user = User(
        first_name="Gruppen",
        last_name="Leitung2",
        username="gruppenleitung_alt",
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


######################################### EMPLOYEES #########################################


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


@pytest.fixture
def employees(group):
    employees = []
    for x in range(5):
        employee = Employee(
            first_name=f"FirstName{x}",
            last_name=f"LastName{x}",
            employee_number=1000 + x,
            group_id=group.id,
        )
        employee.id = uuid.uuid4()
        employees.append(employee)
    return employees


@pytest.fixture()
def employees_alt(group_alt):
    employees = []
    for x in range(5):
        employee = Employee(
            first_name=f"FirstName{x}",
            last_name=f"LastName{x}",
            employee_number=1000 + x,
            group_id=group_alt.id,
        )
        employee.id = uuid.uuid4()
        employees.append(employee)
    return employees


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
def group_alt(user_gruppenleitung_alt, location):
    group = Group(
        group_name="Test Group 2",
        group_number=2,
        user_id_group_leader=user_gruppenleitung_alt.id,
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


######################################### ORDERS #########################################


@pytest.fixture
def pre_order(location):
    forward = date.today().weekday()
    if forward > 2 and forward < 5:  # weekend
        forward = 4
    else:
        forward = 2

    preorder = PreOrder(
        person_id=uuid.uuid4(),
        location_id=location.id,
        date=(datetime.now() + timedelta(days=forward)).date(),
        nothing=False,
        main_dish=MainDish.rot,
        salad_option=True,
    )
    return preorder


@pytest.fixture
def pre_order_alt(location):
    forward = date.today().weekday()
    if forward > 2 and forward < 5:
        forward = 4
    else:
        forward = 2

    preorder = PreOrder(
        person_id=uuid.uuid4(),
        location_id=location.id,
        date=(datetime.now() + timedelta(days=forward)).date(),
        nothing=False,
        main_dish=MainDish.rot,
        salad_option=True,
    )
    return preorder


@pytest.fixture
def pre_orders(employees, location):
    forward = date.today().weekday()
    if forward > 2 and forward < 5:  # weekend
        forward = 4
    else:
        forward = 2

    pre_orders = []
    for employee in employees:
        pre_order = PreOrder(
            person_id=employee.id,
            location_id=location.id,
            date=(datetime.now() + timedelta(days=forward)).date(),
            nothing=False,
            main_dish=MainDish.rot,
            salad_option=True,
        )
        pre_orders.append(pre_order)
    return pre_orders


@pytest.fixture
def pre_orders_alt(employees_alt, location):
    forward = date.today().weekday()
    if forward > 2 and forward < 5:  # weekend
        forward = 4
    else:
        forward = 2

    pre_orders = []
    for employee in employees_alt:
        pre_order = PreOrder(
            person_id=employee.id,
            location_id=location.id,
            date=(datetime.now() + timedelta(days=forward)).date(),
            nothing=False,
            main_dish=MainDish.rot,
            salad_option=True,
        )
        pre_orders.append(pre_order)
    return pre_orders
