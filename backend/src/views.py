from . import app
from flask import redirect, jsonify


@app.route("/")
def index():
    return redirect("/api/health", code=302)


@app.route("/api/health")
def health():
    """Endpoint to check the health of the API.
    Checks if the API is up and running.
    ---
    definitions:
      Health:
        type: object
        properties:
          health_status:
            type: string
    responses:
      200:
        description: Health status of the API
        schema:
          $ref: '#/definitions/Health'
        examples:
          health_status: OK
    """
    response_dict = {"health_status": "OK"}
    return jsonify(response_dict)
