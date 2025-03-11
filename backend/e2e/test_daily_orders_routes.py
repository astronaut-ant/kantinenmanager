""" ""End-to-End tests for the daily_orders routes."""

from .helper import *  # for fixtures # noqa: F403
from .helper import login  # noqa: F401


def describe_daily_orders():
    def describe_get_daily_orders_userscope():
        def it_returns_daily_orders():
            pass

        def it_returns_no_daily_orders_out_of_scope():
            pass

        def unauthorized():
            pass

    def describe_get_daily_orders_counted():
        def it_returns_daily_orders_counted():
            pass

        def it_returns_single_location_kuechenpersonal():
            pass

        def it_returns_all_locations_verwaltung():
            pass

        def unauthorized():
            pass

    def describe_get_daily_order_own():
        def it_returns_daily_order():
            pass

        def it_returns_no_daily_order_out_of_userscope():
            pass

        def it_returns_not_found():
            pass

        def unauthorized():
            pass

    def describe_get_daily_order_person():
        def it_returns_daily_order():
            pass

        def it_returns_no_daily_order_out_of_scope():
            pass

        def it_returns_no_daily_order_not_found():
            pass

        def unauthorized():
            pass

    def describe_get_daily_orders_group():
        def it_returns_daily_orders():
            pass

        def it_returns_no_daily_orders_out_of_scope():
            pass

        def it_returns_no_daily_orders_not_found():
            pass

        def unauthorized():
            pass

    def describe_put_daily_order():
        def it_updates_daily_order():
            pass

        def it_dosnt_update_out_of_userscope():
            pass

        def it_returns_bad_value_error_on_update():
            pass

        def unauthorized():
            pass
