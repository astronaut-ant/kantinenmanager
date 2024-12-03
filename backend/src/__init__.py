from datetime import datetime
from flask import Flask
from flasgger import Swagger
from flask_cors import CORS
from dotenv import load_dotenv
import os

from src.models.environment import Environment
from src.utils.error import register_error_handlers

from .middlewares.auth_middleware import register_auth_middleware
from .database import create_initial_admin, init_db
from .routes.general_routes import general_routes
from .routes.users_routes import users_routes
from .routes.auth_routes import auth_routes
from .routes.employees_routes import employees_routes


app = Flask(__name__)  # Globally accessible Flask app instance

swagger_template = {
    "info": {
        "title": "API Bestellverwaltung",
        "description": "API for our data",
        "version": "0.0.1",
    }
}


def startup() -> None:
    """Start the application."""

    start_time = datetime.now()  # Record the start time of the application

    configure(app, start_time)

    init_db(app)

    if app.config["ENV"] != Environment.MIGRATION:
        # Don't create the initial admin user when running migrations
        # because the required tables might not exist yet
        create_initial_admin(
            app,
            app.config["INITIAL_ADMIN_USERNAME"],
            app.config["INITIAL_ADMIN_PASSWORD"],
        )

    if app.config["ENV"] == Environment.DEVELOPMENT:
        CORS(
            app,
            resources={r"/api/*": {"origins": "http://localhost:3000"}},
            supports_credentials=True,
        )
        swagger = Swagger(app, template=swagger_template)

    register_routes(app)

    print(f"Application started in {app.config['ENV'].value} mode.")


def configure(app: Flask, start_time: datetime) -> None:
    """Configure the application based on the environment variables."""

    load_dotenv()  # parse .env file if it exists

    env = os.getenv("FLASK_ENV")

    initial_admin_username = os.getenv("INITIAL_ADMIN_USERNAME")
    initial_admin_password = os.getenv("INITIAL_ADMIN_PASSWORD")

    db_database = os.getenv("DB_DATABASE")
    db_user = os.getenv("DB_USER")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_password = os.getenv("DB_PASSWORD")

    jwt_secret = os.getenv("JWT_SECRET")

    if (
        not env
        or not db_database
        or not initial_admin_username
        or not initial_admin_password
        or not db_user
        or not db_host
        or not db_port
        or not db_password
        or not jwt_secret
    ):
        raise Exception(
            "Missing environment variables. Please run `docker compose run init` to create the .env file."
        )

    all_env = set(item.value for item in Environment)
    if env not in all_env:
        raise Exception(
            f"Invalid environment. Please use one of the following: {all_env}"
        )

    app.config["APP_START_TIME"] = start_time
    app.config["ENV"] = Environment(env)
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
    )
    app.config["JWT_SECRET"] = jwt_secret
    app.config["MAX_CONTENT_LENGTH"] = 20971520
    app.config["INITIAL_ADMIN_USERNAME"] = initial_admin_username
    app.config["INITIAL_ADMIN_PASSWORD"] = initial_admin_password


def register_routes(app: Flask) -> None:
    """Register all routes for the application."""

    register_error_handlers(app)
    register_auth_middleware(app)

    app.register_blueprint(general_routes)
    app.register_blueprint(users_routes)
    app.register_blueprint(auth_routes)
    app.register_blueprint(employees_routes)


startup()
