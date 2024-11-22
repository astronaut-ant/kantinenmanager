from flask import Flask
from flasgger import Swagger
from flask_cors import CORS

from .middlewares.auth_middleware import register_auth_middleware
from .database import init_db
from .routes.users_routes import users_routes
from .routes.auth_routes import auth_routes
from dotenv import load_dotenv
import os

load_dotenv()

environment = os.getenv("FLASK_ENV")
is_production = environment != "development"

db_database = os.getenv("DB_DATABASE")
db_user = os.getenv("DB_USER")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_password = os.getenv("DB_PASSWORD")

jwt_secret = os.getenv("JWT_SECRET")

if (
    not environment
    or not db_database
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
CORS(app)  # disable in production
swagger = Swagger(app)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
)

app.config["JWT_SECRET"] = jwt_secret

init_db(app)

register_auth_middleware(app)

app.register_blueprint(users_routes)
app.register_blueprint(auth_routes)
