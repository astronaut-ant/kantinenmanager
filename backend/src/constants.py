"""Define constants used throughout the application.

Reason: Avoid circular imports by defining constants in a separate module.
"""

from datetime import timedelta
import string


AUTHENTICATION_TOKEN_DURATION = timedelta(minutes=10)
AUTHENTICATION_TOKEN_COOKIE_NAME = "auth_token"

AUTHENTICATION_TOKEN_AUDIENCE = "grp16-backend"
"""This value will be set in the 'aud' field of the authentication token"""

REFRESH_TOKEN_DURATION = timedelta(days=365)
REFRESH_TOKEN_COOKIE_NAME = "refresh_token"
REFRESH_TOKEN_LENGTH = 64

HTTP_METHODS_TO_EXEMPT_ON_AUTH = ["OPTIONS"]
"""List of HTTP methods that do not require authentication

CORS preflight requests use OPTIONS and are exempt from authentication.
"""

ROUTES_TO_NOT_OVERRIDE_AUTH_TOKENS = ["/api/login", "/api/logout"]
"""List of routes where the authentication middleware should not override tokens"""


GEN_PASSWORD_ALPHABET = string.ascii_letters + string.digits + "#$%&*?@_"
"""Alphabet used to generate passwords"""

GEN_PASSWORD_LENGTH = 12
"""Length of generated passwords"""
