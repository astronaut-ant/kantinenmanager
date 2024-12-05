"""Utility functions for handling errors.

Typical usage example:
    
    msg = ErrMsg(
                status_code=401,
                title="Anmeldung fehlgeschlagen",
                description="Nutzername oder Passwort falsch",
            )
    abort_with_err(msg)
"""

import time
from flask import abort, make_response, request, Flask
from werkzeug.exceptions import HTTPException
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
    @app.errorhandler(Exception)
    def handle_exception(e):
        return make_response(
            ErrMsg(
                status_code=500,
                title="Interner Serverfehler",
                description="Ein unerwarteter Fehler ist aufgetreten",
                details=str(e),
            ).to_dict(),
            500,
        )
