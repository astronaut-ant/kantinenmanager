from datetime import datetime, timedelta, time, date
import pytz
from typing import List, Union, Dict
from uuid import UUID
from flask import Response

from src.repositories.orders_repository import OrdersRepository, OrdersFilters
from src.repositories.locations_repository import LocationsRepository
from src.repositories.users_repository import UsersRepository

from src.models.maindish import MainDish
from src.models.user import UserGroup
from src.models.preorder import PreOrder
from src.models.dailyorder import DailyOrder
from src.models.oldorder import OldOrder

from src.schemas.reports_schemas import CountOrdersObject, CountOrdersSchema
from src.utils.exceptions import AccessDeniedError, NotFoundError, BadValueError
from src.utils.pdf_creator import PDFCreationUtils
from src.utils.error import ErrMsg, abort_with_err


class ReportsService:

    @staticmethod
    def get_daily_orders_count(
        user_group: UserGroup, user_id: UUID
    ) -> List[CountOrdersSchema]:
        """Function for daily_orders_routes"""

        if user_group == UserGroup.kuechenpersonal:
            user = UsersRepository.get_user_by_id(user_id)
            daily_orders = OrdersRepository.get_all_daily_orders(
                OrdersFilters(location_id=user.location_id)
            )
        elif user_group == UserGroup.verwaltung:
            daily_orders = OrdersRepository.get_all_daily_orders()
        else:
            raise AccessDeniedError(f"Nutzer:in {user_id}")

        location_counts = ReportsService._count_location_orders(daily_orders)

        orders = [
            CountOrdersObject(
                location_id=location.id,
                rot=counts["rot"],
                blau=counts["blau"],
                salad_option=counts["salad_option"],
            )
            for location, counts in location_counts.items()
        ]

        return CountOrdersSchema(many=True).dump(orders)

    ################################# Reports Service #################################

    @staticmethod
    def get_location_report(
        filters: OrdersFilters,
        user_id: UUID,
        user_group: UserGroup,
    ) -> Union[Response, None]:
        """
        Create a orders report filterd by date and location
        :param filters: Filters for date_start, date_end and location_id
        :return: a pdf file with the report or None if no orders were found
        """
        if filters.location_id:
            if (
                not filters.location_id
                or not filters.date_start
                or not filters.date_end
            ):
                raise ValueError("Keine Standort-ID oder Datum übergeben")

            orders = ReportsService._get_reports_orders_by_location(
                fil=filters, user_id=user_id, user_group=user_group
            )
        else:
            if not filters.date_start or not filters.date_end:
                raise ValueError("Keine Standort-ID oder Datum übergeben")

            orders = ReportsService._get_reports_orders_by_location(
                fil=filters, user_id=user_id, user_group=user_group
            )

        date_location_counts: Dict[dict] = (
            ReportsService._count_location_orders_by_date(orders)
        )

        return PDFCreationUtils.create_pdf_report(
            filters=filters, date_location_counts=date_location_counts
        )

    def _get_reports_orders_by_location(
        fil: OrdersFilters,
        user_id: UUID,
        user_group: UserGroup,
    ) -> List[PreOrder | DailyOrder | OldOrder]:

        orders: List[PreOrder | DailyOrder | OldOrder] = []

        if fil.date_start and fil.date_end and (fil.date_start <= fil.date_end):
            if ReportsService._check_user_access_to_location(
                fil.location_id, user_id, user_group
            ):
                orders.extend(
                    OrdersRepository.get_pre_orders(
                        fil, user_group=user_group, user_id=user_id
                    )
                )
                orders.extend(OrdersRepository.get_all_daily_orders(fil))
                orders.extend(OrdersRepository.get_old_orders(fil))
            else:
                raise AccessDeniedError(f"Nutzer:in {user_id}")
        else:
            raise ValueError("Kein valides Start- und/oder Enddatum.")
        return orders

    def _check_user_access_to_location(
        location_id: UUID, user_id: UUID, user_group: UserGroup
    ) -> bool:

        if user_group == UserGroup.verwaltung:
            return True
        elif user_group == UserGroup.standortleitung:
            location = LocationsRepository.get_location_by_id(location_id)
            return user_id == location.user_id_location_leader
        elif user_group == UserGroup.kuechenpersonal:
            user = UsersRepository.get_user_by_id(user_id)
            return user.location_id == location_id
        else:
            return False

    def _count_location_orders_by_date(
        orders: Union[List[PreOrder], List[DailyOrder], List[OldOrder]],
    ) -> Dict:

        date_location_counts = {}

        for order in orders:
            if order.nothing:
                continue

            location = LocationsRepository.get_location_by_id(order.location_id)
            if not location:
                raise NotFoundError(f"Standort mit ID {order.location_id}")

            order_date = order.date
            if isinstance(order_date, datetime):
                order_date = order_date.date()

            if order_date not in date_location_counts:
                date_location_counts[order_date] = {}

            if location not in date_location_counts[order_date]:
                date_location_counts[order_date][location] = {
                    "rot": 0,
                    "blau": 0,
                    "salad_option": 0,
                }

            if order.main_dish == MainDish.rot:
                date_location_counts[order_date][location]["rot"] += 1
            elif order.main_dish == MainDish.blau:
                date_location_counts[order_date][location]["blau"] += 1
            if order.salad_option:
                date_location_counts[order_date][location]["salad_option"] += 1

        return date_location_counts

    ################################# Invoices Services #################################

    @staticmethod
    def get_printed_invoice(
        filters: OrdersFilters,
    ) -> Union[Response]:
        """
        Get an invoice report filterd by date and location
        :param filters: Filters for old orders
        :return: a pdf file with the report or None if no orders were found
        """

        if (
            (filters.person_id and filters.location_id)
            or (filters.person_id and filters.group_id)
            or (filters.location_id and filters.group_id)
        ):
            raise BadValueError(
                "Nur eine UUID von Standort, Gruppe ODER Person kann verwendet werden"
            )

        orders: List[OldOrder] = OrdersRepository.get_old_orders(filters)

        if filters.person_id:
            return PDFCreationUtils.create_pdf_invoice_person(
                filters.date_start, filters.date_end, orders, filters.person_id
            )
        elif filters.location_id:
            return PDFCreationUtils.create_pdf_invoice_location(
                filters.date_start, filters.date_end, orders, filters.location_id
            )
        elif filters.group_id:
            return PDFCreationUtils.create_pdf_invoice_group(
                filters.date_start, filters.date_end, orders, filters.group_id
            )
        else:
            raise BadValueError(
                "Keine Standort-ID, Gruppen-ID oder Personen-ID übergeben"
            )
