"""Utility functions for handling errors.

Typical usage example:
    
    msg = ErrMsg(
                status_code=401,
                title="Anmeldung fehlgeschlagen",
                description="Nutzername oder Passwort falsch",
            )
    abort_with_err(msg)
"""

import sys
import time
import traceback
from flask import abort, make_response, request, Flask
import werkzeug
from werkzeug.http import HTTP_STATUS_CODES


class ErrMsg:
    """Error message that should be returned to the client.

    User facing information should be in German.

    :param status: Standardized status message describing the status code
    :param status_code: The HTTP status code
    :param title: Short title of the error (e.g. "Anmeldung fehlgeschlagen")
    :param description: Detailed description of the error
    :param url: The URL that was requested
    :param method: The HTTP method that was used by the request
    :param timestamp: The time when the object was created
    :param details: Additional details about the error
    """

    def __init__(
        self,
        status_code: int,
        title: str,
        description: str,
        **kwargs,
    ):
        """Initialize the error message.

        :param status_code: The HTTP status code
        :param title: Short title of the error (e.g. "Anmeldung fehlgeschlagen")
        :param description: Detailed description of the error
        :param details (optional): Additional details about the error that may be converted to JSON (str, int, dict, list, ...)
        """

        self.status = HTTP_STATUS_CODES[status_code] or "Unknown"
        self.status_code = status_code
        self.title = title
        self.description = description
        self.url = request.url
        self.method = request.method
        self.timestamp = time.time_ns()
        self.details = kwargs["details"] if "details" in kwargs else None

    def to_dict(self):
        """Return the error message as a dictionary."""

        return {
            "status": self.status,
            "status_code": self.status_code,
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "method": self.method,
            "timestamp": self.timestamp,
            "details": self.details,
        }


def abort_with_err(err: ErrMsg):
    """Immediately abort the request with an error message."""

    resp = make_response(err.to_dict(), err.status_code)

    abort(resp)


def register_error_handlers(app: Flask):
    """Register global error handlers for the Flask app."""

    @app.errorhandler(werkzeug.exceptions.BadRequest)
    def handle_bad_request(e):
        """Handle 400 Bad Request errors."""

        return make_response(
            ErrMsg(
                status_code=400,
                title="Ungültige Anfrage",
                description="Die Anfrage ist fehlerhaft",
                details=str(e),
            ).to_dict(),
            400,
        )

    @app.errorhandler(werkzeug.exceptions.Unauthorized)
    def handle_unauthorized(e):
        """Handle 401 Unauthorized errors."""

        return make_response(
            ErrMsg(
                status_code=401,
                title="Nicht autorisiert",
                description="Die Anfrage erfordert eine Authentifizierung",
                details=str(e),
            ).to_dict(),
            401,
        )

    @app.errorhandler(werkzeug.exceptions.Forbidden)
    def handle_forbidden(e):
        """Handle 403 Forbidden errors."""

        return make_response(
            ErrMsg(
                status_code=403,
                title="Zugriff verweigert",
                description="Sie haben keine Berechtigung für diese Aktion",
                details=str(e),
            ).to_dict(),
            403,
        )

    @app.errorhandler(werkzeug.exceptions.NotFound)
    def handle_not_found(e):
        """Handle 404 Not Found errors."""

        return make_response(
            ErrMsg(
                status_code=404,
                title="Nicht gefunden",
                description="Die angeforderte Ressource wurde nicht gefunden",
                details=str(e),
            ).to_dict(),
            404,
        )

    @app.errorhandler(werkzeug.exceptions.MethodNotAllowed)
    def handle_method_not_allowed(e):
        """Handle 405 Method Not Allowed errors."""

        return make_response(
            ErrMsg(
                status_code=405,
                title="Methode nicht erlaubt",
                description="Die angeforderte Methode ist nicht erlaubt",
                details=str(e),
            ).to_dict(),
            405,
        )

    @app.errorhandler(werkzeug.exceptions.InternalServerError)
    def handle_internal_server_error(e):
        """Handle 500 Internal Server Error errors."""

        sys.stderr.write(f"An internal server error occurred: {e}\n")

        return make_response(
            ErrMsg(
                status_code=500,
                title="Interner Serverfehler",
                description="Ein unerwarteter Fehler ist aufgetreten",
                details=str(e),
            ).to_dict(),
            500,
        )

    @app.errorhandler(Exception)
    def handle_exception(e):
        """Handle all exceptions that are not caught by other error handlers."""

        sys.stderr.write(f"An unhandled exception occurred: {e}\n")
        traceback.print_exc()

        return make_response(
            ErrMsg(
                status_code=500,
                title="Interner Serverfehler",
                description="Ein unerwarteter Fehler ist aufgetreten",
                details=str(e),
            ).to_dict(),
            500,
        )
