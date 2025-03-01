import uuid
import pytest
from src import app as project_app
from src.database import create_initial_admin, db as project_db
from src.models.user import User, UserGroup
from src.utils.db_utils import insert_mock_data


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
        yield project_db
        project_db.drop_all()


@pytest.fixture(scope="function")
def seed(app, db):
    create_initial_admin(app, "admin", "password")
    insert_mock_data(app)


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


def join_headers(headers):
    return "; ".join(f"{key}: {value}" for key, value in headers.items())


def get_auth_token(headers):
    return join_headers(headers).split("auth_token=")[1].split(";")[0]


def get_refresh_token(headers):
    return join_headers(headers).split("refresh_token=")[1].split(";")[0]
