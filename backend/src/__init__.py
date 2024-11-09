from flask import Flask
from flasgger import Swagger
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)
