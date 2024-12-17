from uuid import UUID
from datetime import datetime, timedelta
from flask import Blueprint, jsonify
from flasgger import swag_from
from src.utils.auth_utils import login_required
from src.utils.error import ErrMsg, abort_with_err
from src.models.user import UserGroup
from src.repositories.orders_repository import OrdersRepository, OrdersFilters
from src.models.oldorder import OldOrder
from src.models.preorder import PreOrder
from src.models.dailyorder import DailyOrder

orders_cronjob_routes = Blueprint("orders_cronjob_routes", __name__)


@orders_cronjob_routes.get("/api/batch/pre-to-daily-to-old-order")
@login_required(groups=[UserGroup.kuechenpersonal], disabled=True)
@swag_from(
    {
        "tags": ["orders_cronjob"],
        "responses": {
            200: {
                "description": "Converts pre orders to daily orders and daily orders to old orders",
                "schema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"},
                    },
                },
            },
            404: {"description": "Bad request"},
        },
    }
)
def write_pre_to_daily_to_old_order():
    """
    Converts pre orders to daily orders and daily orders to old orders
    """

    orders_old: list[OldOrder] = []
    orders_new: list[PreOrder] = []
    today = datetime.today().date()

    daily_orders_to_move = OrdersRepository.get_all_daily_orders()

    for daily_order in daily_orders_to_move:
        old_order = OldOrder(
            person_id=daily_order.person_id,
            location_id=daily_order.location_id,
            nothing=daily_order.nothing,
            date=today,
            main_dish=daily_order.main_dish,
            salad_option=daily_order.salad_option,
            handed_out=daily_order.handed_out,
        )
        orders_old.append(old_order)

    if len(daily_orders_to_move) != len(orders_old):
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Fehler",
                description="Bestellungen konnten nicht von daily- zu old-order verschoben werden, Unterschiedliche Anzahl an Bestellungen.",
            )
        )
    try:
        OrdersRepository.create_bulk_orders(orders_old)
    except Exception as e:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Fehler",
                description="Bestellungen konnten nicht von daily- zu old-order verschoben werden.",
                details=str(e),
            )
        )
    try:
        OrdersRepository.bulk_delete_orders(daily_orders_to_move)
    except Exception as e:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Fehler",
                description="Bestellungen konnten nicht von daily- zu old-order verschoben werden.",
                details=str(e),
            )
        )

    pre_orders_to_move = OrdersRepository.get_pre_orders(OrdersFilters(date=today))
    for pre_order in pre_orders_to_move:
        daily_order = DailyOrder(
            person_id=pre_order.person_id,
            location_id=pre_order.location_id,
            nothing=pre_order.nothing,
            date=today,
            main_dish=pre_order.main_dish,
            salad_option=pre_order.salad_option,
            handed_out=False,
        )
        orders_new.append(daily_order)

    if len(pre_orders_to_move) != len(orders_new):
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Fehler",
                description="Bestellungen konnten nicht von pre zu daily-order verschoben werden, Unterschiedliche Anzahl an Bestellungen.",
                details=str(e),
            )
        )

    try:
        OrdersRepository.create_bulk_orders(orders_new)
    except Exception as e:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Fehler",
                description="Bestellungen konnten nicht von pre zu daily-order verschoben werden.",
                details=str(e),
            )
        )
    try:
        OrdersRepository.bulk_delete_orders(pre_orders_to_move)
    except Exception as e:
        abort_with_err(
            ErrMsg(
                status_code=404,
                title="Fehler",
                description="Bestellungen konnten nicht von pre zu daily-order verschoben werden.",
                details=str(e),
            )
        )

    return jsonify({"message": "Bestellungen erfolgreich verschoben."}), 200
