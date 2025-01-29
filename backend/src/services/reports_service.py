from datetime import datetime, timedelta, date, time
import pytz
from typing import List, Optional, Union
from uuid import UUID
from enum import Enum
from flask import send_file, Response, make_response
import csv
from io import BytesIO, StringIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
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
from src.models.person import Person

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
        user_id: UUID,
        user_group: UserGroup,
        pdf_bool: bool = True,
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

                if ReportsService._check_user_access_to_location(
                    location_id, user_id, user_group
                ):
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
    def get_printed_invoice(
        filters: OrdersFilters,
        person_id: UUID,
        pdf_bool: bool = True,
    ) -> Union[Response, None]:
        """
        Get an invoice report #TODO filterd by date and location(s)
        :param filters: Filters for old orders
        :return: a pdf file with the report or None if no orders were found
        """

        if not person_id:
            raise ValueError("Keine Person-ID übergeben")

        orders: List[OldOrder] = []

        orders = OrdersRepository.get_old_orders_date(
            OrdersFilters(
                date_start=filters.date_start,
                date_end=filters.date_end,
                person_id=person_id,
            )
        )
        print(orders)
        if orders == []:
            return None

        if pdf_bool:
            return ReportsService._create_pdf_invoice(
                filters.date_start, filters.date_end, orders
            )
        else:
            return ReportsService._create_csv_report(
                filters=filters,
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
        csv_writer.writerow([date_str])

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

    def create_footer(canvas, doc):
        """
        Draws the Footer of the invoice.
        """
        canvas.saveState()
        width, height = A4

        canvas.setLineWidth(0.5)
        canvas.line(50, 70, width - 50, 70)

        canvas.setFont("Helvetica", 8)
        canvas.drawString(
            50, 60, "Rechnung zahlbar ohne Abzug innerhalb 30 Tagen ab Rechnungsdatum."
        )

        canvas.drawString(50, 35, "Stadt- und Kreissparkasse Leip")
        canvas.drawString(50, 25, "IBAN: DE12 8605 5592 1090 2270 31")
        canvas.drawString(50, 15, "BIC: WELADE8LXXX")

        page_number_text = f"Seite {doc.page}"
        canvas.drawRightString(width - 50, 15, page_number_text)

        canvas.restoreState()

    def create_footer_and_header(canvas, doc):
        """
        Draws the Header for the invoice.
        """
        canvas.saveState()
        width, height = A4

        canvas.setLineWidth(0.5)
        canvas.line(50, 70, width - 50, 70)

        canvas.setFont("Helvetica", 8)
        canvas.drawString(
            50, 60, "Rechnung zahlbar ohne Abzug innerhalb 30 Tagen ab Rechnungsdatum."
        )

        canvas.drawString(50, 35, "Stadt- und Kreissparkasse Leip")
        canvas.drawString(50, 25, "IBAN: DE12 8605 5592 1090 2270 31")
        canvas.drawString(50, 15, "BIC: WELADE8LXXX")

        page_number_text = f"Seite {doc.page}"
        canvas.drawRightString(width - 50, 15, page_number_text)

        header_data = [
            ["Leistungsnr./-art", "", "Zeitraum", "Preis", "Anzahl", "Gesamtpreis"]
        ]

        header_table = Table(header_data, colWidths=[75, 175, 100, 60, 35, 60])
        header_table.setStyle(
            TableStyle(
                [
                    ("LINEABOVE", (0, 0), (-1, 0), 0.7, colors.black),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.7, colors.black),
                    ("FONTNAME", (0, 0), (5, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (5, -1), 8),
                    ("BACKGROUND", (-1, -1), (-1, -1), colors.white),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                    ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                    ("ALIGN", (3, 0), (5, -1), "RIGHT"),
                    ("ALIGN", (1, 0), (2, -1), "LEFT"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        width, height = A4
        header_table.wrapOn(canvas, width, height)
        header_table.drawOn(canvas, 45, height - 70)

        canvas.restoreState()

    def _create_pdf_invoice(start, end, orders: List[OldOrder]) -> Response:
        """
        This function creates an invoice for the orders given in the array orders. The invoice is returned as a PDF File.
        """

        styles = getSampleStyleSheet()
        small_style = styles["Normal"]
        small_style.fontName = "Helvetica"
        small_style.fontSize = 6

        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        Name = orders[0].person.first_name + " " + orders[0].person.last_name

        header_data = [
            ["", "", "Sozial-Arbeiten-Wohnen Borna gGmbH"],
            ["", "", "Am Wilhelmsschacht 1"],
            ["", "", "04552 Borna"],
            ["", "", ""],
            ["", "", ""],
            [
                Paragraph(
                    "<u>Sozial Arbeiten - Am Wilhelmsschacht 1 - 04552 Borna</u>",
                    small_style,
                ),
                "",
                "Telefon: 03433/209790",
            ],
            ["", "", ""],
            ["", "", ""],
            [Name, "", "Verpflegung WfbM"],
            ["Platzhalter 1", "", "Am Wilhelmschacht 1"],
            ["Platzhalter 2", "", "04552 Borna"],
            ["", "", ""],
            ["", "", ""],
            ["", "", "Telefon: 03433/20979103"],
            ["", "", ""],
            ["", "", ""],
            ["", "", ""],
        ]
        tableHead = Table(
            header_data,
            colWidths=[203, 50, 200],  # Erste Spalte ist leer, dritte Spalte rechts
            hAlign="RIGHT",
        )
        tableHead.setStyle(
            TableStyle(
                [
                    (
                        "ALIGN",
                        (0, 0),
                        (2, -1),
                        "LEFT",
                    ),  # Text in der dritten Spalte rechtsbündig
                    ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),  # Fettschrift
                    ("FONTNAME", (2, 8), (2, 8), "Helvetica-Bold"),  # Fettschrift
                    ("FONTNAME", (2, 1), (2, 7), "Helvetica"),  # Normaler Text
                    ("FONTNAME", (2, 9), (2, -1), "Helvetica"),  # Normaler Text
                    ("FONTSIZE", (2, 0), (2, -1), 8),  # Schriftgröße 10
                    ("FONTSIZE", (0, 5), (0, 5), 7),  # Schriftgröße 6
                    ("FONTSIZE", (0, 8), (0, -1), 10),  # Schriftgröße 10
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        0,
                    ),  # Abstand oberhalb der Zellen reduzieren
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        0,
                    ),  # Abstand unterhalb der Zellen reduzieren
                ]
            )
        )
        elements.append(tableHead)

        data = [["Leistungsnr./-art", "", "Zeitraum", "Preis", "Anzahl", "Gesamtpreis"]]

        # The following Struture is used to create the main Table for the Invoice from the Array of Old Orders

        current_month = start.month
        main = 0
        mainstart = ""
        mainend = ""
        salad = 0
        saladstart = ""
        saladend = ""
        nothing = 0
        nothingstart = ""
        nothingend = ""
        orderarray = []
        gesamtpreis = 0

        for order in orders:
            date = order.date
            if date.month == current_month and orders.index(order) != len(orders) - 1:
                if order.nothing == True:
                    if nothing > 0:
                        nothing += 1
                        nothingend = date
                    else:
                        if main != 0:
                            orderarray.append(["main", mainstart, mainend, main])
                            main = 0
                        if salad != 0:
                            orderarray.append(["salad", saladstart, saladend, salad])
                            salad = 0
                        nothingstart = date
                        nothingend = date
                        nothing = 1
                else:
                    if order.salad_option == True:
                        if salad > 0:
                            salad += 1
                            saladend = date
                        else:
                            if nothing != 0:
                                orderarray.append(
                                    ["nothing", nothingstart, nothingend, nothing]
                                )
                                nothing = 0
                            saladstart = date
                            saladend = date
                            salad = 1
                    if order.main_dish != "":
                        if main > 0:
                            main += 1
                            mainend = date
                        else:
                            if nothing != 0:
                                orderarray.append(
                                    ["nothing", nothingstart, nothingend, nothing]
                                )
                                nothing = 0
                            mainstart = date
                            mainend = date
                            main = 1
                    else:
                        if main > 0:
                            orderarray.append(["main", mainstart, mainend, main])
                            main = 0
            else:
                if orders.index(order) == len(orders) - 1:
                    if order.nothing == True:
                        if nothing > 0:
                            nothing += 1
                            orderarray.append(["nothing", nothingstart, date, 1])
                            nothing = 0
                        else:
                            if main != 0:
                                orderarray.append(["main", mainstart, mainend, main])
                                main = 0
                            if salad != 0:
                                orderarray.append(
                                    ["salad", saladstart, saladend, salad]
                                )
                                salad = 0
                            orderarray.append(["nothing", date, date, 1])
                    else:
                        if order.salad_option == True:
                            if salad > 0:
                                salad += 1
                                orderarray.append(["salad", saladstart, date, salad])
                                salad = 0
                            else:
                                if nothing != 0:
                                    orderarray.append(
                                        ["nothing", nothingstart, nothingend, nothing]
                                    )
                                    nothing = 0
                                orderarray.append(["salad", date, date, 1])
                        if order.main_dish != "":
                            if main > 0:
                                main += 1
                                orderarray.append(["main", mainstart, date, main])
                                main = 0
                            else:
                                if nothing != 0:
                                    orderarray.append(
                                        ["nothing", nothingstart, nothingend, nothing]
                                    )
                                    nothing = 0
                                orderarray.append(["main", date, date, 1])
                        else:
                            if main > 0:
                                orderarray.append(["main", mainstart, mainend, main])
                                main = 0
                else:
                    if main != 0:
                        orderarray.append(["main", mainstart, mainend, main])
                        main = 0
                    if salad != 0:
                        orderarray.append(["salad", saladstart, saladend, salad])
                        salad = 0
                    if nothing != 0:
                        orderarray.append(
                            ["nothing", nothingstart, nothingend, nothing]
                        )
                        nothing = 0
                firstdayofmonth = orderarray[1][1]
                year = firstdayofmonth.year
                month = firstdayofmonth.month
                data.append(
                    [
                        "3001",
                        "Abzug Vorrauszahlung",
                        f"{month}.{year}",
                        "-70,00",
                        "1,00",
                        "-70,00",
                    ]
                )
                data.append(["", "Mittagessen", "", "", "", ""])
                gesamtpreis -= 70
                monatssumme = -70
                for time in orderarray:
                    start = time[1].strftime("%d.%m.%Y").replace(f"{year}", "")
                    end = time[2].strftime("%d.%m.%Y")
                    if time[0] == "main":
                        zwischenpreis = (time[3] * 41) / 10
                        gesamtpreis += zwischenpreis
                        monatssumme += zwischenpreis
                        data.append(
                            [
                                "3000",
                                "Mittagessen WfbM",
                                f"{start} - {end}",
                                "4,10",
                                f"{time[3]:.2f}".replace(".", ","),
                                f"{zwischenpreis:.2f}".replace(".", ","),
                            ]
                        )
                    if time[0] == "salad":
                        zwischenpreis = (time[3] * 15) / 10
                        gesamtpreis += zwischenpreis
                        monatssumme += zwischenpreis
                        data.append(
                            [
                                "3000",
                                "Mittagessen WfbM Salat",
                                f"{start} - {end}",
                                "1,50",
                                f"{time[3]:.2f}".replace(".", ","),
                                f"{zwischenpreis:.2f}".replace(".", ","),
                            ]
                        )
                    if time[0] == "nothing":
                        data.append(
                            [
                                "3000",
                                "Mittagessen WfbM Nichtesser",
                                f"{start} - {end}",
                                "0,00",
                                f"{time[3]:.2f}".replace(".", ","),
                                "0,00",
                            ]
                        )
                orderarray = []
                data.append(
                    [
                        "",
                        "",
                        "_______________________________________________________",
                        "",
                        "",
                        "",
                    ]
                )
                monate = [
                    "Januar",
                    "Februar",
                    "März",
                    "April",
                    "Mai",
                    "Juni",
                    "Juli",
                    "August",
                    "September",
                    "Oktober",
                    "November",
                    "Dezember",
                ]
                monatalsname = monate[current_month - 1]
                StringMonat = f"Summe {monatalsname} {year}"
                data.append(
                    [
                        "",
                        "",
                        StringMonat,
                        "",
                        "",
                        f"{monatssumme:.2f}".replace(".", ","),
                    ]
                )
                data.append(["", "", "", "", "", ""])
                current_month = current_month + 1
                if current_month == 13:
                    current_month = 1
                if orders.index(order) != len(orders) - 1:
                    if order.nothing == True:
                        nothing = 1
                        nothingstart = date
                        nothingend = date
                    else:
                        if order.salad_option == True:
                            salad = 1
                            saladstart = date
                            saladend = date
                        if order.main_dish != "":
                            main = 1
                            mainstart = date
                            mainend = date

        data.append(
            [
                "",
                "",
                "Rechnungsbetrag:",
                "",
                "",
                f"{gesamtpreis:.2f} €".replace(".", ","),
            ]
        )

        table = Table(data, colWidths=[75, 175, 100, 60, 35, 60])
        table.setStyle(
            TableStyle(
                [
                    ("LINEABOVE", (0, 0), (-1, 0), 0.7, colors.black),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.7, colors.black),
                    ("FONTNAME", (0, 0), (5, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (5, -1), 8),
                    ("BACKGROUND", (-1, -1), (-1, -1), colors.white),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                    ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                    ("ALIGN", (3, 0), (5, -1), "RIGHT"),
                    ("ALIGN", (1, 0), (2, -1), "LEFT"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("LINEABOVE", (0, -1), (-1, -1), 0.7, colors.black),
                    ("LINEBELOW", (2, -1), (-1, -1), 1, colors.black),
                    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                    ("TOPPADDING", (0, -1), (-1, -1), 2),
                ]
            )
        )
        elements.append(table)

        pdf.build(
            elements, onFirstPage=ReportsService.create_footer, onLaterPages=ReportsService.create_footer_and_header
        )
        buffer.seek(0)

        response = make_response(
            send_file(
                buffer,
                mimetype="application/pdf",
                as_attachment=True,
                download_name=f"Rechnung_{start}_bis_{end}_{Name}.pdf",
            )
        )
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"

        return response
