from enum import Enum
from flask import Flask, has_request_context, request
from flask.logging import default_handler
from loki_logger_handler.loki_logger_handler import LokiLoggerHandler
import logging

# Use the logger like this:
# app.logger.info("This is a test message")
# app.logger.warning("This is a warning message")
# app.logger.error("This is an error message")
# app.logger.debug("This is a debug message")
# app.logger.critical("This is a critical message")
#
# You can get access to app from anywhere using:
# from flask import current_app as app


class LoggingMethod(Enum):
    # Define the logging method
    LOKI = "loki"
    CONSOLE = "console"


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)


def init_logger(app: Flask, method: LoggingMethod, loki_url: str = "") -> None:
    """Initialize the logger with the given Flask app."""

    formatter = RequestFormatter(
        "[%(asctime)s] %(remote_addr)s requested %(url)s\n"
        "%(levelname)s in %(module)s: %(message)s"
    )
    default_handler.setFormatter(formatter)

    if method == LoggingMethod.CONSOLE:
        return

    if method == LoggingMethod.LOKI:
        custom_handler = LokiLoggerHandler(
            url=loki_url,
            labels={"service": "flask_api", "environment": "production"},
            label_keys={},
            timeout=10,
            additional_headers={"X-Scope-OrgId": "sep"},
            enable_self_errors=True,
        )
        custom_handler.setLevel(logging.INFO)

        app.logger.addHandler(custom_handler)
