from . import app
from flask import redirect


@app.route("/")
def index():
    return redirect("/health", code=302)


@app.route("/health")
def health():
    """Example endpoint returning OK if the service is healthy.
    This is an example of a health check endpoint.
    ---
    responses:
      200:
        description: OK
    """
    return "OK"
