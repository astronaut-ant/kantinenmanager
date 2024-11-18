"""Define constants used throughout the application.

Reason: Avoid circular imports by defining constants in a separate module.
"""

from datetime import timedelta


AUTHENTICATION_TOKEN_DURATION = timedelta(minutes=10)
AUTHENTICATION_TOKEN_COOKIE_NAME = "auth_token"

REFRESH_TOKEN_DURATION = timedelta(days=1)  # TODO: Set to 1 year in production
REFRESH_TOKEN_COOKIE_NAME = "refresh_token"
