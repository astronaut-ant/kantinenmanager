from enum import Enum
from flask import Flask
from loki_logger_handler.loki_logger_handler import LokiLoggerHandler
import logging


class LoggingMethod(Enum):
    # Define the logging method
    LOKI = "loki"
    CONSOLE = "console"


def init_logger(app: Flask, method: LoggingMethod, loki_url: str = "") -> None:
    """Initialize the logger with the given Flask app."""

    if method == LoggingMethod.CONSOLE:
        return

    custom_handler = LokiLoggerHandler(
        url=loki_url,
        labels={"backend": "flask"},
        label_keys={},
        timeout=10,
        additional_headers={"X-Scope-OrgId": "sep"},
    )
    custom_handler.setLevel(logging.INFO)

    app.logger.addHandler(custom_handler)
