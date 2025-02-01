"""Flask middleware to authenticate a user on each request"""

from flask import Flask, after_this_request, make_response, request, g

from src.utils.error import ErrMsg, abort_with_err
from src.utils.exceptions import UserBlockedError, UnauthenticatedException
from src.constants import (
    AUTHENTICATION_TOKEN_COOKIE_NAME,
    REFRESH_TOKEN_COOKIE_NAME,
    ROUTES_TO_NOT_OVERRIDE_AUTH_TOKENS,
)
from src.services.auth_service import AuthService
from src.utils.auth_utils import delete_token_cookies, set_token_cookies


def register_auth_middleware(app: Flask):
    """Register the authentication middleware

    The middleware is executed on each request before the route handler. It reads the
    authentication and refresh token from the request cookies, validates them, and
    sets new tokens in the response cookies if necessary.

    After validation the following data is stored in the global `g` object and can be
    accessed in the route handler:

    - user_authenticated: True if the user is authenticated, False otherwise
    - user_id: The user ID or None if the user is not authenticated
    - user_username: The username or None if the user is not authenticated
    - user_group: The user group or None if the user is not authenticated
    - user_first_name: The first name or None if the user is not authenticated
    - user_last_name: The last name or None if the user is not authenticated

    :param app: The Flask app
    """

    @app.before_request
    def auth_middleware():

        # This part is executed before each request

        route = request.path

        auth_token = request.cookies.get(AUTHENTICATION_TOKEN_COOKIE_NAME)
        refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)

        new_auth_token = None
        new_refresh_token = None

        try:
            user_info, new_auth_token, new_refresh_token = AuthService.authenticate(
                auth_token, refresh_token
            )

            g.user_authenticated = True

            g.user_id = user_info.get("id")
            g.user_username = user_info.get("username")
            g.user_group = user_info.get("group")
            g.user_first_name = user_info.get("first_name")
            g.user_last_name = user_info.get("last_name")
        except UnauthenticatedException as e:
            # User is not authenticated.
            # The user is still allowed to continue.
            # The route handler can decide if authentication is required.

            g.user_authenticated = False

            g.user_id = None
            g.user_username = None
            g.user_group = None
            g.user_first_name = None
            g.user_last_name = None
        except UserBlockedError as e:
            # User is blocked.

            resp = make_response()

            delete_token_cookies(resp)

            abort_with_err(
                ErrMsg(
                    status_code=403,
                    title="Account gesperrt",
                    description="Ihr Account wurde gesperrt. Bitte kontaktieren Sie eine:n Administrator:in.",
                    details=str(e),
                ),
                resp=resp,
            )

        if (
            new_auth_token
            and new_refresh_token
            and (route not in ROUTES_TO_NOT_OVERRIDE_AUTH_TOKENS)
        ):

            @after_this_request
            def set_cookies(response):

                # If new tokens were generated, set them in the response cookies.
                # We need access to the response object, so we use the after_this_request
                # decorator to execute this part after the route handler.

                set_token_cookies(response, new_auth_token, new_refresh_token)
                return response
