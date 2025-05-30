import uuid
import datetime
import pytest
from sqlalchemy import text
from src.models.dish_price import DishPrice
from src.models.oldorder import OldOrder
from src.models.dailyorder import DailyOrder
from src.models.maindish import MainDish
from src.models.preorder import PreOrder
from src.models.location import Location
from src import app as project_app
from src.database import create_initial_admin, db as project_db
from src.models.user import User, UserGroup
from src.utils.db_utils import insert_mock_data
from src.models.group import Group
from src.models.employee import Employee

######################################### BASE FIXTURES #########################################

PASSWORD = "password"
JWT_SECRET = "super_secret"


@pytest.fixture()
def app():
    project_app.config["JWT_SECRET"] = JWT_SECRET
    project_app.config["TESTING"] = True
    yield project_app


@pytest.fixture()
def client(app):
    with app.app_context():
        yield app.test_client()


@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        project_db.create_all()
        # * Set it to ON to enable foreign key constraints as
        # * this is not enabled by default in SQLite.
        # * I tried to use ON as default but it was very flakey.
        project_db.session.execute(text("PRAGMA foreign_keys = OFF"))
        yield project_db
        project_db.drop_all()


@pytest.fixture(scope="function")
def seed(app, db):
    create_initial_admin(app, "admin", "password")
    insert_mock_data(app)


def login(user: User, client):
    res = client.post(
        "/api/login",
        json={"username": user.username, "password": PASSWORD},
    )
    assert res.status_code == 200
    return res


def join_headers(headers):
    return "; ".join(f"{key}: {value}" for key, value in headers.items())


def get_auth_token(headers):
    return join_headers(headers).split("auth_token=")[1].split(";")[0]


def get_refresh_token(headers):
    return join_headers(headers).split("refresh_token=")[1].split(";")[0]


################################################### USERS: BASE, ALTERNATE, ALTERNATE LOCATION ###################################################


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
def user_gruppenleitung_alt(location):
    user = User(
        first_name="Gruppen",
        last_name="Leitung",
        username="gruppenleitung_alt",
        hashed_password="$argon2id$v=19$m=65536,t=3,p=4$3rfCHeNLgFGKSyeZU0tl5w$rpsECi3FkYbvf2DEyPrDwp5/lPD3RUecZARuaRSVrWQ",  # password: password
        user_group=UserGroup.gruppenleitung,
        location_id=location.id,
    )
    user.id = uuid.uuid4()
    return user


@pytest.fixture()
def user_kuechenpersonal_alt(location):
    user = User(
        first_name="Kuechen",
        last_name="Personal",
        username="kuechenpersonal_alt",
        hashed_password="$argon2id$v=19$m=65536,t=3,p=4$3rfCHeNLgFGKSyeZU0tl5w$rpsECi3FkYbvf2DEyPrDwp5/lPD3RUecZARuaRSVrWQ",  # password: password
        user_group=UserGroup.kuechenpersonal,
        location_id=location.id,
    )
    user.id = uuid.uuid4()
    return user


@pytest.fixture()
def user_standortleitung_alt_location():
    user = User(
        first_name="Standort",
        last_name="Leitung",
        username="standortleitung_alt_location",
        hashed_password="$argon2id$v=19$m=65536,t=3,p=4$3rfCHeNLgFGKSyeZU0tl5w$rpsECi3FkYbvf2DEyPrDwp5/lPD3RUecZARuaRSVrWQ",  # password: password
        user_group=UserGroup.standortleitung,
    )
    user.id = uuid.uuid4()
    return user


@pytest.fixture()
def user_gruppenleitung_alt_location(location_alt):
    user = User(
        first_name="Gruppen",
        last_name="Leitung",
        username="gruppenleitung_alt_location",
        hashed_password="$argon2id$v=19$m=65536,t=3,p=4$3rfCHeNLgFGKSyeZU0tl5w$rpsECi3FkYbvf2DEyPrDwp5/lPD3RUecZARuaRSVrWQ",  # password: password
        user_group=UserGroup.gruppenleitung,
        location_id=location_alt.id,
    )
    user.id = uuid.uuid4()
    return user


@pytest.fixture()
def user_kuechenpersonal_alt_location(location_alt):
    user = User(
        first_name="Kuechen",
        last_name="Personal",
        username="kuechenpersonal_alt_location",
        hashed_password="$argon2id$v=19$m=65536,t=3,p=4$3rfCHeNLgFGKSyeZU0tl5w$rpsECi3FkYbvf2DEyPrDwp5/lPD3RUecZARuaRSVrWQ",  # password: password
        user_group=UserGroup.kuechenpersonal,
        location_id=location_alt.id,
    )
    user.id = uuid.uuid4()
    return user


@pytest.fixture()
def users():
    users = []
    for x in range(0, 10):
        user = User(
            first_name=f"User{x}",
            last_name=f"Lastname{x}",
            username=f"user{x}",
            hashed_password="$argon2id$v=19$m=65536,t=3,p=4$3rfCHeNLgFGKSyeZU0tl5w$rpsECi3FkYbvf2DEyPrDwp5/lPD3RUecZARuaRSVrWQ",  # password: password
            user_group=UserGroup.verwaltung,
        )
        user.id = uuid.uuid4()
        users.append(user)
    return users


################################################### LOCATIONS ###################################################


@pytest.fixture()
def location(user_standortleitung):
    location = Location(
        location_name="Test Location", user_id_location_leader=user_standortleitung.id
    )
    location.id = uuid.uuid4()
    return location


@pytest.fixture()
def other_location():
    location = Location(
        location_name="Other Location", user_id_location_leader=uuid.uuid4()
    )
    location.id = uuid.uuid4()
    return location


@pytest.fixture()
def location_alt(user_standortleitung_alt_location):
    location = Location(
        location_name="Another Test Location",
        user_id_location_leader=user_standortleitung_alt_location.id,
    )
    location.id = uuid.uuid4()
    return location


################################################### GROUPS ###################################################


@pytest.fixture
def group(location, user_gruppenleitung):
    group = Group(
        group_name="Test Group",
        location_id=location.id,
        user_id_group_leader=user_gruppenleitung.id,
        user_id_replacement=None,
        group_number=123,
    )
    group.id = uuid.uuid4()
    return group


@pytest.fixture
def other_group(other_location):
    group = Group(
        group_name="Other Group",
        location_id=other_location.id,
        user_id_group_leader=uuid.uuid4(),
        user_id_replacement=None,
        group_number=234,
    )
    group.id = uuid.uuid4()
    return group


@pytest.fixture
def group_alt(location, user_gruppenleitung_alt):
    group = Group(
        group_name="Test Group",
        location_id=location.id,
        user_id_group_leader=user_gruppenleitung_alt.id,
        user_id_replacement=None,
        group_number=234,
    )
    group.id = uuid.uuid4()
    return group


@pytest.fixture
def group_alt_location(location_alt, user_gruppenleitung_alt_location):
    group = Group(
        group_name="Test Group",
        location_id=location_alt.id,
        user_id_group_leader=user_gruppenleitung_alt_location.id,
        user_id_replacement=None,
        group_number=345,
    )
    group.id = uuid.uuid4()
    return group


################################################### EMPLOYEES ###################################################


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


@pytest.fixture
def employees_alt(group_alt):
    employees = []
    for x in range(5):
        employee = Employee(
            first_name=f"FirstName{x+10}",
            last_name=f"LastName{x+10}",
            employee_number=2000 + x,
            group_id=group_alt.id,
        )
        employee.id = uuid.uuid4()
        employees.append(employee)
    return employees


@pytest.fixture
def employees_alt_location(group_alt_location):
    employees = []
    for x in range(5):
        employee = Employee(
            first_name=f"FirstName{x+100}",
            last_name=f"LastName{x+100}",
            employee_number=3000 + x,
            group_id=group_alt_location.id,
        )
        employee.id = uuid.uuid4()
        employees.append(employee)
    return employees


################################################### ORDERS ###################################################


@pytest.fixture
def pre_order(location):
    forward = datetime.date.today().weekday()
    if forward > 2 and forward < 5:  # weekend
        forward = 4
    else:
        forward = 2

    pre_order = PreOrder(
        person_id=uuid.uuid4(),
        location_id=location.id,
        date=(datetime.datetime.now() + datetime.timedelta(days=forward)).date(),
        nothing=False,
        main_dish=MainDish.rot,
        salad_option=True,
    )
    return pre_order


@pytest.fixture
def pre_orders(employees, location):
    forward = datetime.date.today().weekday()
    if forward > 2 and forward < 5:  # weekend
        forward = 4
    else:
        forward = 2

    pre_orders = []
    for employee in employees:
        pre_order = PreOrder(
            person_id=employee.id,
            location_id=location.id,
            date=(datetime.datetime.now() + datetime.timedelta(days=forward)).date(),
            nothing=False,
            main_dish=MainDish.rot,
            salad_option=True,
        )
        pre_orders.append(pre_order)
    return pre_orders


@pytest.fixture
def pre_orders_alt(employees_alt, location):
    forward = datetime.date.today().weekday()
    if forward > 2 and forward < 5:  # weekend
        forward = 4
    else:
        forward = 2

    pre_orders = []
    for employee in employees_alt:
        pre_order = PreOrder(
            person_id=employee.id,
            location_id=location.id,
            date=(datetime.datetime.now() + datetime.timedelta(days=forward)).date(),
            nothing=False,
            main_dish=MainDish.rot,
            salad_option=True,
        )
        pre_orders.append(pre_order)
    return pre_orders


#################### DAILY ORDERS ####################


@pytest.fixture
def daily_order(location):
    daily_order = DailyOrder(
        person_id=uuid.uuid4(),
        location_id=location.id,
        date=datetime.datetime.now().date(),
        nothing=False,
        main_dish=MainDish.rot,
        salad_option=True,
    )
    return daily_order


@pytest.fixture
def daily_orders(employees, location):
    daily_orders = []
    for employee in employees:
        daily_order = DailyOrder(
            person_id=employee.id,
            location_id=location.id,
            date=datetime.datetime.now().date(),
            nothing=False,
            main_dish=MainDish.rot,
            salad_option=True,
        )
        daily_orders.append(daily_order)
    return daily_orders


@pytest.fixture
def daily_orders_alt(employees_alt, location):
    daily_orders = []
    for employee in employees_alt:
        daily_order = DailyOrder(
            person_id=employee.id,
            location_id=location.id,
            date=datetime.datetime.now().date(),
            nothing=False,
            main_dish=MainDish.blau,
            salad_option=True,
        )
        daily_orders.append(daily_order)
    return daily_orders


@pytest.fixture
def daily_orders_alt_location(employees_alt_location, location_alt):
    daily_orders = []
    for employee in employees_alt_location:
        daily_order = DailyOrder(
            person_id=employee.id,
            location_id=location_alt.id,
            date=datetime.datetime.now().date(),
            nothing=False,
            main_dish=MainDish.rot,
            salad_option=True,
        )
        daily_orders.append(daily_order)
    return daily_orders


#################### OLD ORDERS ####################


@pytest.fixture
def old_order(location):
    old_order = OldOrder(
        person_id=uuid.uuid4(),
        location_id=location.id,
        date=(datetime.datetime.now() - datetime.timedelta(days=1)).date(),
        nothing=False,
        main_dish=MainDish.rot,
        handed_out=True,
        salad_option=True,
    )
    return old_order


@pytest.fixture
def old_orders(employees, location):
    old_orders = []
    forward = datetime.date.today().weekday()
    if forward > 0 and forward < 6:  # weekend
        forward = 1
    else:
        forward = 3

    for employee in employees:
        old_order = OldOrder(
            person_id=employee.id,
            location_id=location.id,
            date=(datetime.datetime.now() - datetime.timedelta(days=forward)).date(),
            nothing=False,
            main_dish=MainDish.rot,
            handed_out=True,
            salad_option=True,
        )
        old_orders.append(old_order)
    return old_orders


@pytest.fixture
def old_orders_alt(employees_alt, location):
    old_orders = []
    forward = datetime.date.today().weekday()
    if forward > 0 and forward < 6:
        forward = 1
    else:
        forward = 3

    for employee in employees_alt:
        old_order = OldOrder(
            person_id=employee.id,
            location_id=location.id,
            date=(datetime.datetime.now() - datetime.timedelta(days=forward)).date(),
            nothing=False,
            main_dish=MainDish.blau,
            handed_out=True,
            salad_option=True,
        )
        old_orders.append(old_order)
    return old_orders


#################### OTHER THINGS ####################


@pytest.fixture()
def today():
    return datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


@pytest.fixture()
def dish_price(today):
    return DishPrice(
        date=today,
        main_dish_price=5.5,
        salad_price=2.5,
        prepayment=15.0,
    )


@pytest.fixture()
def dish_price_alt(today):
    return DishPrice(
        date=today - datetime.timedelta(days=10),
        main_dish_price=2.5,
        salad_price=1.5,
        prepayment=10.0,
    )
