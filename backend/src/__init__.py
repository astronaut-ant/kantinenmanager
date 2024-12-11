from datetime import datetime
from flask import Flask
from flasgger import Swagger
from flask_cors import CORS
from dotenv import load_dotenv
import os

from src.utils.db_utils import insert_mock_data
from src.environment import Environment, get_features
from src.utils.error import register_error_handlers

from .middlewares.auth_middleware import register_auth_middleware
from .database import create_initial_admin, init_db, setup_test_db
from .routes.general_routes import general_routes
from .routes.users_routes import users_routes
from .routes.auth_routes import auth_routes
from .routes.employees_routes import employees_routes
from .routes.persons_routes import persons_routes
from .routes.groups_routes import groups_routes
from .routes.locations_routes import locations_routes
from .routes.pre_orders_routes import pre_orders_routes
from .routes.daily_orders_routes import daily_orders_routes
from .routes.old_orders_routes import old_orders_routes


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

    configure(app)

    print(f"Application starting in {app.config['ENV'].value} mode.")

    features = app.config["FEATURES"]

    print("\nFeatures:")

    if features.DATABASE == "real":
        print("--- Database enabled             ---")
        init_db(app)
    elif features.DATABASE == "in-memory":
        print("--- In-memory database enabled   ---")
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            "sqlite:///:memory:"  # Override the database URI
        )
        setup_test_db(app)
    else:
        print("--- Database disabled            ---")

    if features.TESTING_MODE:
        print("--- Testing mode enabled         ---")
        app.config["TESTING"] = True
    else:
        print("--- Testing mode disabled        ---")

    if features.CORS:
        print("--- CORS enabled                 ---")
        CORS(
            app,
            resources={r"/api/*": {"origins": "http://localhost:3000"}},
            supports_credentials=True,
        )
    else:
        print("--- CORS disabled                ---")

    if features.SWAGGER:
        print("--- Swagger enabled              ---")
        Swagger(app, template=swagger_template)
    else:
        print("--- Swagger disabled             ---")

    if features.INSERT_DEFAULT_DATA:
        print("--- Inserting default data       ---")
        create_initial_admin(
            app,
            app.config["INITIAL_ADMIN_USERNAME"],
            app.config["INITIAL_ADMIN_PASSWORD"],
        )
    else:
        print("--- Default data insertion disabled ---")

    if features.INSERT_MOCK_DATA:
        print("--- Inserting mock data          ---")
        insert_mock_data(app)
    else:
        print("--- Mock data insertion disabled ---")

    register_routes(app)


def configure(app: Flask) -> None:
    """Configure the application based on environment variables."""

    load_dotenv()  # parse .env file if it exists

    # Get environment variables
    env = os.getenv("FLASK_ENV")
    initial_admin_username = os.getenv("INITIAL_ADMIN_USERNAME")
    initial_admin_password = os.getenv("INITIAL_ADMIN_PASSWORD")
    db_database = os.getenv("DB_DATABASE")
    db_user = os.getenv("DB_USER")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_password = os.getenv("DB_PASSWORD")
    jwt_secret = os.getenv("JWT_SECRET")

    # Check if all environment variables are set
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

    # Check if the environment is valid
    all_env = set(item.value for item in Environment)
    if env not in all_env:
        raise Exception(
            f"Invalid environment. Please use one of the following: {all_env}"
        )

    app.config["APP_START_TIME"] = (
        datetime.now()
    )  # Record the start time of the application

    app.config["ENV"] = Environment(env)
    app.config["FEATURES"] = get_features(app.config["ENV"])

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
    )

    app.config["JWT_SECRET"] = jwt_secret
    app.config["INITIAL_ADMIN_USERNAME"] = initial_admin_username
    app.config["INITIAL_ADMIN_PASSWORD"] = initial_admin_password

    app.config["MAX_CONTENT_LENGTH"] = 20971520


def register_routes(app: Flask) -> None:
    """Register all routes for the application."""

    register_error_handlers(app)
    register_auth_middleware(app)

    app.register_blueprint(general_routes)
    app.register_blueprint(users_routes)
    app.register_blueprint(auth_routes)
    app.register_blueprint(employees_routes)
    app.register_blueprint(persons_routes)
    app.register_blueprint(groups_routes)
    app.register_blueprint(locations_routes)
    app.register_blueprint(pre_orders_routes)
    app.register_blueprint(daily_orders_routes)
    app.register_blueprint(old_orders_routes)


startup()
