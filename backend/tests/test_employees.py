from datetime import datetime, timedelta
import uuid
import pytest
from src import app as project_app


@pytest.fixture()
def app():
    project_app.config["TESTING"] = True
    yield project_app


@pytest.fixture
def client(app):
    return app.test_client()
