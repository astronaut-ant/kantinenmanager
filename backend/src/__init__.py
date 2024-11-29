from flask import Flask
from flasgger import Swagger
from flask_cors import CORS

from .middlewares.auth_middleware import register_auth_middleware
from .database import create_initial_admin, init_db
from .routes.users_routes import users_routes
from .routes.auth_routes import auth_routes
from .routes.employees_routes import employees_routes
from dotenv import load_dotenv
import os

load_dotenv()

environment = os.getenv("FLASK_ENV")
is_production = environment != "development"

initial_admin_username = os.getenv("INITIAL_ADMIN_USERNAME")
initial_admin_password = os.getenv("INITIAL_ADMIN_PASSWORD")

db_database = os.getenv("DB_DATABASE")
db_user = os.getenv("DB_USER")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_password = os.getenv("DB_PASSWORD")

jwt_secret = os.getenv("JWT_SECRET")

if (
    not environment
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

app = Flask(__name__)
CORS(
    app,
    resources={r"/api/*": {"origins": "http://localhost:3000"}},
    supports_credentials=True,
)
swagger = Swagger(app)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
)

app.config["JWT_SECRET"] = jwt_secret
app.config["MAX_CONTENT_LENGTH"] = 20971520

init_db(app)
create_initial_admin(app, initial_admin_username, initial_admin_password)

register_auth_middleware(app)

app.register_blueprint(users_routes)
app.register_blueprint(auth_routes)
app.register_blueprint(employees_routes)
