"""Utility functions to make life easier regarding authentication and authorization"""

import functools

from flask import Response, g, request
from src.utils.error import ErrMsg, abort_with_err
from src.services.auth_service import AuthService, UnauthenticatedException
from src.constants import (
    AUTHENTICATION_TOKEN_COOKIE_NAME,
    AUTHENTICATION_TOKEN_DURATION,
    HTTP_METHODS_TO_EXEMPT_ON_AUTH,
    REFRESH_TOKEN_COOKIE_NAME,
    REFRESH_TOKEN_DURATION,
)
from src.models.user import UserGroup


def set_token_cookies(resp: Response, new_auth_token: str, new_refresh_token: str):
    """Helper function to set authentication and refresh token cookies

    :param resp: The response object to set the cookies on
    :param new_auth_token: The new authentication token
    :param new_refresh_token: The new refresh token
    """

    resp.set_cookie(
        AUTHENTICATION_TOKEN_COOKIE_NAME,
        new_auth_token,
        max_age=round(AUTHENTICATION_TOKEN_DURATION.total_seconds()),
        httponly=True,
        # secure=True,  # TODO: Enable in production
        # samesite="Strict",  # TODO: Enable in production
    )

    resp.set_cookie(
        REFRESH_TOKEN_COOKIE_NAME,
        new_refresh_token,
        max_age=round(REFRESH_TOKEN_DURATION.total_seconds()),
        httponly=True,
        # secure=True,  # TODO: Enable in production
        # samesite="Strict",  # TODO: Enable in production
    )


def login_required(
    groups=[
        UserGroup.gruppenleitung,
        UserGroup.kuechenpersonal,
        UserGroup.standortleitung,
        UserGroup.verwaltung,
    ],
    disabled=False,
):
    """Decorator to require authentication for a route"""

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if request.method in HTTP_METHODS_TO_EXEMPT_ON_AUTH:
                # Skip authentication
                pass
            elif disabled:
                # Skip authentication
                print("WARNING: Authentication disabled")
                pass
            else:
                # Check authentication
                if g.user_authenticated is False:
                    abort_with_err(
                        ErrMsg(
                            status_code=401,
                            title="Nicht authentifiziert",
                            description="Sie müssen angemeldet sein, um diese Aktion auszuführen",
                        )
                    )

                # Check authorization
                if g.user_group not in groups:
                    abort_with_err(
                        ErrMsg(
                            status_code=403,
                            title="Nicht autorisiert",
                            description="Sie haben keine Berechtigung für diese Aktion",
                        )
                    )

            return func(*args, **kwargs)

        return wrapper

    return decorator
