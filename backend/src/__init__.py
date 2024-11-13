from flask import Flask
from flasgger import Swagger
from flask_cors import CORS
from .database import init_db


app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

app.config["SQLALCHEMY_DATABASE_URI"] ="postgresql://postgres:miau@db:5432/postgres"
init_db(app)
