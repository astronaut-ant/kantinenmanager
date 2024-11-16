from marshmallow import ValidationError
from src.models.user import User, UserGroup
from src.services.users_service import UsersService
from flask import Blueprint, make_response, jsonify, abort, request
from marshmallow.validate import Length
from flasgger import Schema, fields, swag_from

# Routes sind die Verbindung zur Außenwelt und verantwortlich für die Verarbeitung von HTTP-Requests.
# Eine Route bekommt einen Request vom Nutzer (Frontend), extrahiert die enthaltenen Daten, gibt
# sie an den Service weiter und dann das entsprechende Ergebnis in einem Response Objekt zurück.
#
# Hier verwenden wir hauptsächlich Flask:
# https://flask.palletsprojects.com/en/stable/
#
# Flasgger dient der Dokumentation unserer API, ähnlich wie JavaDoc
# Unsere API Dokumentation: http://localhost:4200/apidocs/.
# Flasgger Doku: https://github.com/flasgger/flasgger

# Blueprints kommen aus Flask: https://flask.palletsprojects.com/en/stable/blueprints/
# Damit können wir unsere Anwendung "modularisieren".
users_routes = Blueprint("users_routes", __name__)


# Bei jedem GET Request (siehe HTTP) auf /api/users wird die get_users Funktion aufgerufen
@users_routes.get("/api/users")
def get_users():
    """Get all users
    Get a list of all users
    ---
    tags:
      - users
    definitions:
      User:
        type: object
        properties:
          id:
            type: integer
          username:
            type: string
          user_group:
            type: string
            enum:
              - verwaltung
              - standortleitung
              - gruppenleitung
              - kuechenpersonal
    responses:
      200:
        description: Returns a list of all users
        schema:
          type: array
          items:
            $ref: '#/definitions/User'
    """
    # Der docstring --^ ist wie wir Flasgger über die Parameter und Rückgabewerte
    # dieses Endpunkts informieren. Die Informationen werden extrahiert und
    # graphisch auf http://localhost:4200/apidocs/ angezeigt.
    # Achtung: Im Kommentar wird YAML verwendet, was **2** Leerzeichen als Einrückung verwendet.

    users = (
        UsersService.get_users()
    )  # Hier bekommen wir vom Service eine Liste aller Nutzer

    # Diese wird in eine Liste an Dicts umgewandelt, aber ohne das Passwort
    users_dict = [
        {"id": user.id, "username": user.username, "user_group": user.user_group.value}
        for user in users
    ]

    # Die dicts brauchen wir, denn daraus können wir JSON erzeugen.
    # Mit jsonify wird automatisch ein Response Object erstellt.
    return jsonify(users_dict)


# Das folgende kommt aus Marshmallow. https://marshmallow.readthedocs.io/en/stable/#
# Mit Marshmallow kann man Objekte serialisieren, deserialisieren und validieren, was eine Menge if Statements ersparen sollte.
# Das Schema gibt an, wie die Daten aussehen sollen, zusammen mit gewissen Einschränkungen. Diese Schemas können wir auch für
# Flasgger verwenden, um zu definieren, wie die Eingabedaten (BODY, QUERY) auszusehen haben.
class UsersPostBody(Schema):
    """
    Schema for the POST /users endpoint
    """

    username = fields.Str(required=True, validate=Length(min=1, max=50))
    password = fields.Str(required=True, validate=Length(min=8, max=150))
    user_group = fields.Enum(UserGroup, required=True)

    # Die beiden folgenden Funktionen müssen genauso heißen und werden
    # von Flasgger aufgerufen.

    def swag_validation_function(self, data, main_def):
        # data sind quasi die rohen Daten, wie sie aus dem Request kommen.
        # Mit load (aus Marshmallow) werden die Daten deserialisiert, also in eine Python-Datenstruktur
        # gewandelt. Dabei werden obige Constrains validiert. Bei Verletzungen
        # wird ein Error geworfen. In diesem Fall wird die zweite Methode aufgerufen.
        self.load(data)

    def swag_validation_error_handler(self, err, data, main_def):
        # Im Fehlerfall wird die gesamte Anfrage mit `abort` vorzeitig unterbrochen.
        # (abort kommt aus Flask). Hier wird die Fehlermeldung mit einem 400
        # Status Code (-> Bad Request) zurückgesendet.
        abort(make_response(jsonify(err.messages), 400))


# Bei jedem POST Request auf /api/users wird die create_user Funktion aufgerufen.
# Flasgger reicht uns den BODY des Requests (Instanz obigen Schemas) als Argument in die Funktion
# und führt vorher die Validierung aus.
# Leider ist das ziemlich schlecht von Flasgger dokumentiert. Aber `swag=True` kommt von Flasgger.
@users_routes.post("/api/users", swag=True)
def create_user(body: UsersPostBody):
    """Create a new user
    Create a new user with the given username, password, and user group
    ---
    tags:
      - users
    responses:
      200:
        description: Returns the ID of the created user
        schema:
          type: object
          properties:
            id:
              type: integer
      400:
        description: Validation error
    """

    # Alternativ könnten wir über das `request` Objekt von Flask direkt auf den Request zugreifen
    # und manuell die Daten extrahieren.

    user = User(**body)
    id = UsersService.create_user(user)
    return jsonify({"id": id})
