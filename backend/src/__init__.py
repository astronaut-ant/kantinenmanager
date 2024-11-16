from flask import Flask
from flasgger import Swagger
from flask_cors import CORS
from .database import init_db
from .routes.users_routes import users_routes
from .routes.auth_routes import auth_routes


app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:miau@db:5432/postgres"
init_db(app)

app.register_blueprint(users_routes)
app.register_blueprint(auth_routes)
