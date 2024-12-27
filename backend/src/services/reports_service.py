from datetime import datetime, timedelta, date, time
import pytz
from typing import List, Optional, Union
from uuid import UUID
from enum import Enum
from flask import send_file, Response, make_response
import csv
from io import BytesIO, StringIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak,
    KeepTogether,
)

from src.repositories.orders_repository import OrdersRepository, OrdersFilters
from src.repositories.locations_repository import LocationsRepository
from src.repositories.users_repository import UsersRepository

from src.models.maindish import MainDish
from src.models.user import UserGroup
from src.models.preorder import PreOrder
from src.models.dailyorder import DailyOrder
from src.models.oldorder import OldOrder

from src.schemas.reports_schemas import CountOrdersObject, CountOrdersSchema

from src.utils.exceptions import AccessDeniedError, LocationDoesNotExist


class OrderType(Enum):
    OLD_ORDER = OldOrder
    PRE_ORDER = PreOrder
    DAILY_ORDER = DailyOrder


ORDER_TYPE_GETTER = {
    "OLD_ORDER": OrdersRepository.get_old_orders,
    "PRE_ORDER": OrdersRepository.get_pre_orders,
    "DAILY_ORDER": OrdersRepository.get_all_daily_orders,
}


class ReportsService:

    @staticmethod
    def get_printed_report(
        filters: OrdersFilters,
        location_ids: Optional[List[UUID]],
        pdf_bool: bool,
        user_id: UUID,
        user_group: UserGroup,
    ) -> Union[Response, None]:
        """
        Get a preorders report filterd by date and location(s)
        :param filters: Filters for old orders
        :return: a pdf file with the report or None if no orders were found
        """

        if not location_ids:
            raise ValueError("Keine Standort-ID übergeben")

        try:
            order_types_with_dates = ReportsService._get_order_details(
                filters.date, filters.date_start, filters.date_end
            )
        except ValueError as err:
            raise ValueError(str(err))

        if not order_types_with_dates:
            raise ValueError("Keine Bestellungen für dieses Datum gefunden")

        orders: List[PreOrder | DailyOrder | OldOrder] = []

        for order_type, date_start, date_end in order_types_with_dates:

            for location_id in location_ids:

                if ReportsService._check_user_access_to_location:
                    orders.extend(
                        ORDER_TYPE_GETTER[order_type](
                            OrdersFilters(
                                date_start=date_start,
                                date_end=date_end,
                                location_id=location_id,
                            )
                        )
                    )

                else:
                    raise AccessDeniedError(
                        f"Nutzer:in hat keine Berechtigung für Standort {location_id}."
                    )

        location_counts = ReportsService._count_location_orders(orders)

        if pdf_bool:
            return ReportsService._create_pdf_report(
                filters=filters, location_counts=location_counts
            )
        else:
            return ReportsService._create_csv_report(
                filters=filters, location_counts=location_counts
            )

    @staticmethod
    def get_daily_orders_count(
        user_group: UserGroup, user_id: UUID
    ) -> List[CountOrdersSchema]:

        if user_group == UserGroup.kuechenpersonal:
            user = UsersRepository.get_user_by_id(user_id)
            daily_orders = OrdersRepository.get_all_daily_orders(
                OrdersFilters(location_id=user.location_id)
            )
        elif user_group == UserGroup.verwaltung:
            daily_orders = OrdersRepository.get_all_daily_orders()
        else:
            raise AccessDeniedError(
                f"Zugriff verweigert. Nutzer:in {user_id} hat keine Berechtigung."
            )

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

    def _get_order_details(
        single_date: Optional[date],
        date_start: Optional[date],
        date_end: Optional[date],
    ) -> List[dict]:

        timezone = pytz.timezone("Europe/Berlin")
        today = datetime.now(timezone).date()
        current_time = datetime.now(timezone).time()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        before_yesterday = yesterday - timedelta(days=1)

        order_types = []

        print(single_date, date_start, date_end)

        if single_date:

            if (single_date == today and current_time <= time(8, 0)) or (
                single_date > today
            ):
                order_types.append(("PRE_ORDER", single_date, single_date))

            elif (single_date == today and current_time > time(8, 0)) or (
                single_date == yesterday and current_time < time(8, 0)
            ):
                order_types.append(("DAILY_ORDER", single_date, single_date))

            else:
                order_types.append(("OLD_ORDER", single_date, single_date))

        elif date_start and date_end and (date_start <= date_end):

            if date_end < yesterday:
                order_types.append(("OLD_ORDER", date_start, date_end))

            if today < date_start:
                order_types.append(("PRE_ORDER", date_start, date_end))

            if date_start <= today <= date_end:
                if current_time < time(8, 0):
                    order_types.append(("PRE_ORDER", date_start, today))
                else:
                    order_types.append(("PRE_ORDER", date_start, tomorrow))
                    order_types.append(("DAILY_ORDER", today, today))

            if date_start <= yesterday <= date_end:
                if current_time < time(8, 0):
                    order_types.append(("DAILY_ORDER", yesterday, yesterday))
                    order_types.append(("OLD_ORDER", before_yesterday, date_end))
                else:
                    order_types.append(("OLD_ORDER", yesterday, date_end))

        else:
            raise ValueError(
                "Kein valides Datum. Übergebe entweder ein Datum oder ein valides Start- und ein Enddatum."
            )

        return order_types

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

    def _count_location_orders(
        orders: Union[List[PreOrder], List[DailyOrder], List[OldOrder]]
    ) -> dict:

        location_counts = {}

        for order in orders:
            if order.nothing:
                continue

            location = LocationsRepository.get_location_by_id(order.location_id)
            if not location:
                raise LocationDoesNotExist("Standort nicht gefunden")

            if location not in location_counts:
                location_counts[location] = {
                    "rot": 0,
                    "blau": 0,
                    "salad_option": 0,
                }

            if order.main_dish == MainDish.rot:
                location_counts[location]["rot"] += 1
            elif order.main_dish == MainDish.blau:
                location_counts[location]["blau"] += 1
            if order.salad_option:
                location_counts[location]["salad_option"] += 1

        return location_counts

    def _create_pdf_report(filters: OrdersFilters, location_counts: dict) -> Response:

        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        date_str = ReportsService._get_date_string(filters)
        if not date_str:
            raise ValueError("Kein Datum übergeben")

        elements.append(Paragraph(f"Datum: {date_str}", styles["Heading2"]))
        elements.append(Spacer(1, 12))

        for location, counts in location_counts.items():
            location_block = ReportsService._create_location_pdf_block(
                location.location_name, counts, styles
            )
            elements.append(KeepTogether(location_block))

        pdf.build(elements)
        buffer.seek(0)

        response = make_response(
            send_file(
                buffer,
                mimetype="application/pdf",
                as_attachment=True,
                download_name=f"Report_{date_str}.pdf",
            )
        )
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"

        return response

    def _create_location_pdf_block(location_name, counts, styles):
        location_block = []
        location_block.append(Paragraph(location_name, styles["Heading3"]))
        location_block.append(Spacer(1, 8))

        data = [
            ["Gericht", "Anzahl"],
            ["Rot", counts["rot"]],
            ["Blau", counts["blau"]],
            ["Salat", counts["salad_option"]],
        ]

        table = Table(data, colWidths=[150, 100])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

        location_block.append(table)
        location_block.append(Spacer(1, 20))

        return location_block

    def _create_csv_report(filters: OrdersFilters, location_counts: dict) -> Response:

        buffer = StringIO()
        csv_writer = csv.writer(buffer)

        date_str = ReportsService._get_date_string(filters)
        csv_writer.writerow([f"Datum: {filters.date_start} bis {filters.date_end}"])

        for location, counts in location_counts.items():
            ReportsService._write_location_csv(
                csv_writer, location.location_name, counts
            )

        buffer.seek(0)
        csv_content = buffer.getvalue().encode("utf-8")

        response = make_response(
            send_file(
                BytesIO(csv_content),
                mimetype="text/csv",
                as_attachment=True,
                download_name=f"Report_{date_str}.csv",
            )
        )

        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"

        return response

    def _write_location_csv(csv_writer, location_name, counts):
        csv_writer.writerow([])
        csv_writer.writerow([location_name])
        csv_writer.writerow(["Gericht", "Anzahl"])
        csv_writer.writerow(["Rot", counts["rot"]])
        csv_writer.writerow(["Blau", counts["blau"]])
        csv_writer.writerow(["Salad", counts["salad_option"]])

    def _get_date_string(filters: OrdersFilters) -> str:

        if filters.date_start and filters.date_end:
            if filters.date_start.year == filters.date_end.year:
                date_range = f"{filters.date_start.strftime('%d.%m')}–{filters.date_end.strftime('%d.%m.%Y')}"
            else:
                date_range = f"{filters.date_start.strftime('%d.%m.%Y')}–{filters.date_end.strftime('%d.%m.%Y')}"
            return date_range
        elif filters.date:
            return f"{filters.date.strftime('%d.%m.%Y')}"
        else:
            return None
