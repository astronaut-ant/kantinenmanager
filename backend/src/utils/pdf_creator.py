from typing import List, Optional
from flask import send_file, Response, make_response
import qrcode
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    KeepTogether,
)

from src.models.person import Person  # noqa: F401
from src.models.employee import Employee
from src.models.group import Group
from src.models.oldorder import OldOrder
from src.models.dish_price import DishPrice  # noqa: F401

from src.repositories.orders_repository import OrdersFilters
from src.repositories.locations_repository import LocationsRepository
from src.repositories.persons_repository import PersonsRepository
from src.repositories.groups_repository import GroupsRepository
from src.repositories.dish_prices_repository import DishPricesRepository

from src.utils.exceptions import NotFoundError


FONT_NORMAL = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
FONT_SIZE_NORMAL = 8
FONT_SIZE_BIG = 10
FONT_SIZE_SMALL = 7

TELEFONKURZ = "Telefon: 03433/209790"
TELEFON = "Telefon: 03433/20979103"
FIRMENNAME = "Sozial-Arbeiten-Wohnen Borna gGmbH"
STRASSE = "Am Wilhelmsschacht 1"
PLZ = "04552 Borna"
FIRMENADRESSIERUNG = "Sozial Arbeiten - Am Wilhelmsschacht 1 - 04552 Borna"
ABTEILUNG = "Verpflegung WfbM"

BANK = "Stadt- und Kreissparkasse Leip"
IBAN = "IBAN: DE12 8605 5592 1090 2270 31"
BIC = "BIC: WELADE8LXXX"
MONATE = [
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

NUMMER_VORRAUSZAHLUNG = "3001"
NUMMER_HAUPTGERICHT = "3000"
NUMMER_SALAT = "3000"
NUMMER_NICHTESSER = "3000"


class PDFCreationUtils:

    ################################# QR-Code PDF #################################
    @staticmethod
    def create_qr_code_person(person: Person):
        # QR-Code generieren
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(person.id)
        qr.make(fit=True)
        img = qr.make_image(fill="black", back_color="white")

        # QR-Code-Bild in einem BytesIO-Objekt im Speicher speichern
        qr_buffer = BytesIO()
        img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        pdf_buffer = BytesIO()
        page_width, page_height = A4
        c = canvas.Canvas(pdf_buffer, pagesize=A4)

        # Position für den QR-Code
        qr_size = 150
        x_center = (page_width - qr_size) / 2
        y_position = (page_height / 2) + 180  # Position in der oberen Hälfte

        # BytesIO-Objekt in ein ImageReader-Objekt umwandeln, um das QR-Code-Bild in die Canvas einzubetten
        qr_image = ImageReader(qr_buffer)
        c.drawImage(qr_image, x_center, y_position, width=qr_size, height=qr_size)

        # Text unterhalb des QR-Codes hinzufügen
        text_y_position = y_position - 20
        c.setFont("Helvetica", 10)
        c.drawCentredString(
            page_width / 2,
            text_y_position,
            f"{person.first_name} {person.last_name}",
        )
        c.save()
        pdf_buffer.seek(0)

        response = make_response(
            send_file(
                pdf_buffer,
                mimetype="application/pdf",
                as_attachment=True,
                download_name=f"qr-code_{person.first_name}{person.last_name}.pdf",
            )
        )
        # Explicitly expose the Content-Disposition header for the frontend
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        return response
    
    @staticmethod
    def create_batch_qr_codes(employees: List[Employee], group: Optional[Group] = None):
        """Create a PDF with QR codes for a list of employees.

        :param employees: List of employee objects to create QR codes for
        :return: The PDF with QR codes as a Response object
        """

        pdf_buffer = BytesIO()
        _, page_height = A4
        c = canvas.Canvas(pdf_buffer, pagesize=A4)

        qr_size = 150
        horizontal_margin = 30
        vertical_margin = 50
        cols = 3
        x_start = horizontal_margin
        y_start = page_height - vertical_margin - qr_size

        x_position = x_start
        y_position = y_start

        for idx, employee in enumerate(employees):
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(employee.id)
            qr.make(fit=True)
            img = qr.make_image(fill="black", back_color="white")

            qr_buffer = BytesIO()
            img.save(qr_buffer, format="PNG")
            qr_buffer.seek(0)
            qr_image = ImageReader(qr_buffer)

            c.drawImage(qr_image, x_position, y_position, width=qr_size, height=qr_size)
            c.setFont("Helvetica", 10)
            c.drawCentredString(
                x_position + qr_size / 2,
                y_position - 12,
                f"{employee.first_name} {employee.last_name}",
            )

            x_position += qr_size + horizontal_margin

            if (idx + 1) % cols == 0:
                x_position = x_start
                y_position -= qr_size + 2 * vertical_margin

                if y_position < vertical_margin:
                    c.showPage()
                    y_position = y_start

        c.save()
        pdf_buffer.seek(0)

        if group:
            download_name = f"{group.group_name}_qr_codes.pdf"
        else:
            download_name = "batch_qr_codes.pdf"

        response = make_response(
            send_file(
                pdf_buffer,
                mimetype="application/pdf",
                as_attachment=True,
                download_name=download_name,
            )
        )
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        return response

    ################################# Reports PDF #################################

    @staticmethod
    def create_pdf_report(filters: OrdersFilters, date_location_counts: dict, all_loactions: bool = False) -> Response:

        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        date_str = PDFCreationUtils._get_date_string(filters)
        if not date_str:
            raise ValueError("Kein Datum übergeben")

        elements.append(Paragraph(f"Bestellübersicht für Zeitraum: {date_str}", styles["Heading1"]))
        elements.append(Spacer(1, 12))
        sorted_dates = sorted(date_location_counts.keys())

        for current_date in sorted_dates:
            date_formatted = current_date.strftime("%d.%m.%Y")
            elements.append(Paragraph(f"Datum: {date_formatted}", styles["Heading2"]))

            if all_loactions:
                counter_for_date = {}
                for location in date_location_counts[current_date]:
                    counter_for_date["rot"] = date_location_counts[current_date][location]["rot"]
                    counter_for_date["blau"] = date_location_counts[current_date][location]["blau"]
                    counter_for_date["salad_option"] = date_location_counts[current_date][location]["salad_option"]
                elements.append(Paragraph(f"Rot: {counter_for_date["rot"]}, Blau: {counter_for_date["blau"]}, Salat: {counter_for_date["salad_option"]}", styles["Heading3"]))
                
            elements.append(Spacer(1, 8))

            locations_for_date: dict = date_location_counts[current_date]
            
            for location, counts in locations_for_date.items():
                location_block = PDFCreationUtils._create_location_pdf_block(
                    location.location_name, counts, styles
                )
                elements.append(KeepTogether(location_block))
            
            elements.append(Spacer(1, 20))


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

    def _get_date_string(filters: OrdersFilters) -> str:

        if filters.date_start and filters.date_end:
            if filters.date_start.year == filters.date_end.year:
                date_range = f"{filters.date_start.strftime('%d.%m')}.–{filters.date_end.strftime('%d.%m.%Y')}"
            else:
                date_range = f"{filters.date_start.strftime('%d.%m.%Y')}.–{filters.date_end.strftime('%d.%m.%Y')}"
            return date_range
        elif filters.date:
            return f"{filters.date.strftime('%d.%m.%Y')}"
        else:
            return None

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

    ################################# Invoices Footer and Header #################################
    def _create_footer(canvas, doc):
        """
        Draws the Footer of the invoice.
        """
        canvas.saveState()
        width, height = A4

        canvas.setLineWidth(0.5)
        canvas.line(50, 70, width - 50, 70)

        canvas.setFont(FONT_NORMAL, FONT_SIZE_NORMAL)
        canvas.drawString(
            50, 60, "Rechnung zahlbar ohne Abzug innerhalb 30 Tagen ab Rechnungsdatum."
        )

        canvas.drawString(50, 35, BANK)
        canvas.drawString(50, 25, IBAN)
        canvas.drawString(50, 15, BIC)

        page_number_text = f"Seite {doc.page}"
        canvas.drawRightString(width - 50, 15, page_number_text)

        canvas.restoreState()

    def _create_footer_and_header(canvas, doc):
        """
        Draws the Header for the invoice.
        """
        canvas.saveState()
        width, height = A4

        canvas.setLineWidth(0.5)
        canvas.line(50, 70, width - 50, 70)

        canvas.setFont(FONT_NORMAL, FONT_SIZE_NORMAL)
        canvas.drawString(
            50, 60, "Rechnung zahlbar ohne Abzug innerhalb 30 Tagen ab Rechnungsdatum."
        )

        canvas.drawString(50, 35, BANK)
        canvas.drawString(50, 25, IBAN)
        canvas.drawString(50, 15, BIC)

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
                    ("FONTNAME", (0, 0), (5, -1), FONT_NORMAL),
                    ("FONTSIZE", (0, 0), (5, -1), FONT_SIZE_NORMAL),
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

    ################################# Invoice PDF Helper #################################
    @staticmethod
    def _sort_orders(orders: List[OldOrder], start, end) -> List[OldOrder]:
        """
        This function sorts the orders by months.
        """
        current_month = start.month
        current_year = start.year
        end_year = end.year
        end_month = end.month
        months = []

        while True:
            months.append([current_month, current_year])
            if current_month == end_month and current_year == end_year:
                break
            current_month += 1
            if current_month == 13:
                current_month = 1
                current_year += 1

        orderarray = []
        for month, year in months:
            montharray = []
            for order in orders:
                if order.date.month == month and order.date.year == year:
                    montharray.append(order)
            orderarray.append(montharray)

        return orderarray, months

    ################################# Person PDF Helper ##################################
    @staticmethod
    def _get_PDFHead(person, style) -> List:
        Name = person.first_name + " " + person.last_name
        if person.type == "employee":
            Gruppenname = person.group.group_name
            Locationname = person.group.location.location_name
        else:
            Gruppenname = "Gruppenleiter am Standort:"
            Locationname = person.location.location_name

        header_data = [
            ["", "", FIRMENNAME],
            ["", "", STRASSE],
            ["", "", PLZ],
            ["", "", ""],
            ["", "", ""],
            [
                Paragraph(
                    f"<u>{FIRMENADRESSIERUNG}</u>",
                    style,
                ),
                "",
                TELEFONKURZ,
            ],
            ["", "", ""],
            ["", "", ""],
            [Name, "", ABTEILUNG],
            [Gruppenname, "", STRASSE],
            [Locationname, "", PLZ],
            ["", "", ""],
            ["", "", ""],
            ["", "", TELEFON],
            ["", "", ""],
            ["", "", ""],
            ["", "", ""],
        ]
        tableHead = Table(
            header_data,
            colWidths=[203, 50, 200],
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
                    ),
                    ("FONTNAME", (2, 0), (2, -1), FONT_BOLD),
                    ("FONTNAME", (2, 8), (2, 8), FONT_BOLD),
                    ("FONTNAME", (2, 1), (2, 7), FONT_NORMAL),
                    ("FONTNAME", (2, 9), (2, -1), FONT_NORMAL),
                    ("FONTSIZE", (2, 0), (2, -1), FONT_SIZE_NORMAL),
                    ("FONTSIZE", (0, 5), (0, 5), FONT_SIZE_SMALL),
                    ("FONTSIZE", (0, 8), (0, -1), FONT_SIZE_BIG),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        0,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        0,
                    ),
                ]
            )
        )
        return tableHead

    ################################# Invoice PDF Person #################################

    @staticmethod
    def create_pdf_invoice_person(
        start, end, orders: List[OldOrder], personid
    ) -> Response:
        """
        This function creates an invoice for the orders given in the array orders. The invoice is returned as a PDF File.
        """

        styles = getSampleStyleSheet()
        small_style = styles["Normal"]
        small_style.fontName = FONT_NORMAL
        small_style.fontSize = 6

        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        person = PersonsRepository.get_person_by_id(personid)
        if not person:
            raise NotFoundError(
                f"Es wurde keine Person mit angegebener UUID {personid} gefunden"
            )
        else:
            elements.append(PDFCreationUtils._get_PDFHead(person, small_style))

        result = PDFCreationUtils._sort_orders(orders, start, end)
        orders_sorted_array = result[0]
        months = result[1]

        prices = DishPricesRepository.get_prices()
        payment = []
        payment.append(
            [
                datetime.strptime("01.01.1900", "%d.%m.%Y"),
                41,
                15,
                70,
            ]
        )
        if prices:
            prices.sort(key=lambda x: x.date)
            for price in prices:
                if (
                    price.date.year < end.year
                    or price.date.month <= end.month
                    and price.date.year <= end.year
                ):
                    payment.append(
                        [
                            price.date,
                            price.main_dish_price * 10,
                            price.salad_price * 10,
                            price.prepayment,
                        ]
                    )
        orderarray = []

        main = 0
        mainstart = ""
        mainend = ""
        salad = 0
        saladstart = ""
        saladend = ""
        nothing = 0
        nothingstart = ""
        nothingend = ""

        credit = 0

        data = [["Leistungsnr./-art", "", "Zeitraum", "Preis", "Anzahl", "Gesamtpreis"]]
        for month, year in months:
            index = months.index([month, year])
            for order in orders_sorted_array[index]:
                date = order.date
                if order.nothing is True:
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
                    if order.salad_option is True:
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
                    if order.main_dish is not None:
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
            month_payment = payment[0]
            for new_entry in payment:
                if (
                    new_entry[0].year < year
                    or new_entry[0].month <= month
                    and new_entry[0].year <= year
                ):
                    month_payment = new_entry
            mainprice = month_payment[1]
            saladprice = month_payment[2]
            prepayment = month_payment[3]
            if nothing != 0:
                orderarray.append(["nothing", nothingstart, nothingend, nothing])
                nothing = 0
            else:
                if main != 0:
                    orderarray.append(["main", mainstart, mainend, main])
                    main = 0
                if salad != 0:
                    orderarray.append(["salad", saladstart, saladend, salad])
                    salad = 0
            data.append(
                [
                    NUMMER_VORRAUSZAHLUNG,
                    "Abzug Vorrauszahlung",
                    f"{month}.{year}",
                    f"{prepayment:.2f}".replace(".", ","),
                    "1,00",
                    f"{prepayment:.2f}".replace(".", ","),
                ]
            )
            data.append(["", "Mittagessen", "", "", "", ""])
            credit -= prepayment
            monthly = -prepayment
            for type, start, end, count in orderarray:
                start = start.strftime("%d.%m.%Y").replace(f"{year}", "")
                end = end.strftime("%d.%m.%Y")
                if type == "main":
                    price = (count * mainprice) / 10
                    credit += price
                    monthly += price
                    data.append(
                        [
                            NUMMER_HAUPTGERICHT,
                            "Mittagessen WfbM",
                            f"{start} - {end}",
                            f"{mainprice/10:.2f}".replace(".", ","),
                            f"{count:.2f}".replace(".", ","),
                            f"{price:.2f}".replace(".", ","),
                        ]
                    )
                if type == "salad":
                    price = (count * (saladprice)) / 10
                    credit += price
                    monthly += price
                    data.append(
                        [
                            NUMMER_SALAT,
                            "Mittagessen WfbM Salat",
                            f"{start} - {end}",
                            f"{saladprice/10:.2f}".replace(".", ","),
                            f"{count:.2f}".replace(".", ","),
                            f"{price:.2f}".replace(".", ","),
                        ]
                    )
                if type == "nothing":
                    data.append(
                        [
                            NUMMER_NICHTESSER,
                            "Mittagessen WfbM Nichtesser",
                            f"{start} - {end}",
                            "0,00",
                            f"{count:.2f}".replace(".", ","),
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
            month_name = MONATE[month - 1]
            StringMonat = f"Summe {month_name} {year}"
            data.append(
                [
                    "",
                    "",
                    StringMonat,
                    "",
                    "",
                    f"{monthly:.2f}".replace(".", ","),
                ]
            )
            data.append(["", "", "", "", "", ""])

        data.append(
            [
                "",
                "",
                "Rechnungsbetrag:",
                "",
                "",
                f"{credit:.2f} €".replace(".", ","),
            ]
        )

        table = Table(data, colWidths=[75, 175, 100, 60, 35, 60])
        table.setStyle(
            TableStyle(
                [
                    ("LINEABOVE", (0, 0), (-1, 0), 0.7, colors.black),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.7, colors.black),
                    ("FONTNAME", (0, 0), (5, -1), FONT_NORMAL),
                    ("FONTSIZE", (0, 0), (5, -1), FONT_SIZE_NORMAL),
                    ("BACKGROUND", (-1, -1), (-1, -1), colors.white),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                    ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                    ("ALIGN", (3, 0), (5, -1), "RIGHT"),
                    ("ALIGN", (1, 0), (2, -1), "LEFT"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("LINEABOVE", (0, -1), (-1, -1), 0.7, colors.black),
                    ("LINEBELOW", (2, -1), (-1, -1), 1, colors.black),
                    ("FONTNAME", (0, -1), (-1, -1), FONT_BOLD),
                    ("TOPPADDING", (0, -1), (-1, -1), 2),
                ]
            )
        )
        elements.append(table)

        pdf.build(
            elements,
            onFirstPage=PDFCreationUtils._create_footer,
            onLaterPages=PDFCreationUtils._create_footer_and_header,
        )
        buffer.seek(0)

        response = make_response(
            send_file(
                buffer,
                mimetype="application/pdf",
                as_attachment=True,
                download_name=f"Rechnung_{start}_bis_{end}_{person.first_name}_{person.last_name}.pdf",
            )
        )
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"

        return response

    ############################ Group/Location PDF Header #################################

    @staticmethod
    def _create_PDFHead_g_l(obj, start_date, end_date):

        header_data = [
            [obj, "", ""],
            ["", "", ""],
            [
                "Abrechnung für den Zeitraum:",
                "",
                f"{start_date.strftime("%d.%m.%Y")} - {end_date.strftime("%d.%m.%Y")}",
            ],
            ["", "", ""],
        ]
        tableHead = Table(
            header_data,
            colWidths=[245, 5, 245],
        )
        tableHead.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (2, 2), (2, 2), "RIGHT"),
                    ("FONTNAME", (0, 0), (0, 0), FONT_BOLD),
                    ("FONTNAME", (1, 0), (-1, -1), FONT_NORMAL),
                    ("FONTSIZE", (0, 0), (-1, -1), FONT_SIZE_BIG),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        return tableHead

    ################################# Location Invoice PDF #################################

    def create_pdf_invoice_location(
        start_date, end_date, orders: List[OldOrder], locationid
    ) -> Response:
        location = LocationsRepository.get_location_by_id(locationid)
        if not location:
            raise NotFoundError(
                f"Es wurde kein Standort mit angegebener UUID: {locationid} gefunden"
            )

        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        elements.append(
            PDFCreationUtils._create_PDFHead_g_l(
                f"Standort: {location.location_name}", start_date, end_date
            )
        )

        data = [["Gruppe", "", "Hauptgericht Anzahl", "Salat Anzahl"]]

        result = PDFCreationUtils._sort_orders(orders, start_date, end_date)
        orders_sorted_array = result[0]
        months = result[1]

        allmain = 0
        allsalad = 0
        for month, year in months:
            index = months.index([month, year])
            monthly_main = 0
            monthly_salad = 0
            groups = []
            persons = []
            foodgroups = []
            foodusers = []
            for order in orders_sorted_array[index]:
                if order.date.month == month and order.date.year == year:
                    if order.person.type == "employee":
                        if order.person.group not in groups:
                            groups.append(order.person.group)
                            foodgroups.append([order.person.group, 0, 0])
                        if order.main_dish is not None:
                            foodgroups[groups.index(order.person.group)][1] += 1
                            monthly_main += 1
                        if order.salad_option is True:
                            foodgroups[groups.index(order.person.group)][2] += 1
                            monthly_salad += 1
                    else:
                        if order.person not in persons:
                            persons.append(order.person)
                            foodusers.append([order.person, 0, 0])
                        if order.main_dish is not None:
                            foodusers[persons.index(order.person)][1] += 1
                            monthly_main += 1
                        if order.salad_option is True:
                            foodusers[persons.index(order.person)][2] += 1
                            monthly_salad += 1
            allmain += monthly_main
            allsalad += monthly_salad
            groupsreplica = groups.copy()
            groups.sort(key=lambda x: x.group_name)
            personsreplica = persons.copy()
            persons.sort(key=lambda x: x.last_name)
            for user in persons:
                index = personsreplica.index(user)
                data.append(
                    [
                        f"Gruppenleiter: {user.last_name}, {user.first_name}",
                        "",
                        f"{foodusers[index][1]:.2f}".replace(".", ","),
                        f"{foodusers[index][2]:.2f}".replace(".", ","),
                    ]
                )
            for group in groups:
                index = groupsreplica.index(group)
                data.append(
                    [
                        f"Gruppe: {group.group_name}",
                        "",
                        f"{foodgroups[index][1]:.2f}".replace(".", ","),
                        f"{foodgroups[index][2]:.2f}".replace(".", ","),
                    ]
                )
            data.append(
                [
                    "",
                    "____________________________________________________________",
                    "",
                    "",
                ]
            )
            monatalsname = MONATE[month - 1]
            StringMonat = f"Summe {monatalsname} {year}"
            data.append(
                [
                    "",
                    StringMonat,
                    f"{monthly_main:.2f}".replace(".", ","),
                    f"{monthly_salad:.2f}".replace(".", ","),
                ]
            )
            data.append(["", "", "", ""])

        data.append(
            [
                "",
                "Gesamt:",
                f"{allmain:.2f}".replace(".", ","),
                f"{allsalad:.2f}".replace(".", ","),
            ]
        )

        table = Table(data, colWidths=[225, 100, 90, 90])  # Gesamt: 505
        table.setStyle(
            TableStyle(
                [
                    ("LINEABOVE", (0, 0), (-1, 0), 0.7, colors.black),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.7, colors.black),
                    ("FONTNAME", (0, 0), (3, 0), FONT_BOLD),
                    ("FONTNAME", (0, 1), (3, -1), FONT_NORMAL),
                    ("FONTSIZE", (0, 0), (3, -1), FONT_SIZE_NORMAL),
                    ("BACKGROUND", (-1, -1), (-1, -1), colors.white),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                    ("ALIGN", (0, 0), (0, -1), "LEFT"),
                    ("ALIGN", (2, 0), (3, -1), "RIGHT"),
                    ("ALIGN", (1, 0), (1, -1), "LEFT"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("LINEABOVE", (0, -1), (-1, -1), 0.7, colors.black),
                    ("LINEBELOW", (1, -1), (-1, -1), 1, colors.black),
                    ("FONTNAME", (0, -1), (-1, -1), FONT_NORMAL),
                    ("TOPPADDING", (0, -1), (-1, -1), 2),
                ]
            )
        )
        elements.append(table)

        pdf.build(elements)
        buffer.seek(0)

        response = make_response(
            send_file(
                buffer,
                mimetype="application/pdf",
                as_attachment=True,
                download_name=f"Rechnung_{start_date}_bis_{end_date}_{location.location_name}.pdf",
            )
        )
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"

        return response

    ################################# Group Invoice PDF #################################

    def create_pdf_invoice_group(
        start_date, end_date, orders: List[OldOrder], groupid
    ) -> Response:

        group = GroupsRepository.get_group_by_id(groupid)
        if not group:
            raise NotFoundError(
                f"Es wurde keine Gruppe mit angegebener UUID: {groupid} gefunden"
            )

        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        elements.append(
            PDFCreationUtils._create_PDFHead_g_l(
                f"Gruppe: {group.group_name}", start_date, end_date
            )
        )

        data = [["Mitarbeiter", "", "Hauptgericht Anzahl", "Salat Anzahl"]]

        result = PDFCreationUtils._sort_orders(orders, start_date, end_date)
        orders_sorted_array = result[0]
        months = result[1]

        allmain = 0
        allsalad = 0
        for month, year in months:
            index = months.index([month, year])
            monthly_main = 0
            monthly_salad = 0
            persons = []
            foodgroups = []
            for order in orders_sorted_array[index]:
                if order.date.month == month and order.date.year == year:
                    if order.person not in persons:
                        persons.append(order.person)
                        foodgroups.append([order.person, 0, 0])
                    if order.main_dish is not None:
                        foodgroups[persons.index(order.person)][1] += 1
                        monthly_main += 1
                    if order.salad_option is True:
                        foodgroups[persons.index(order.person)][2] += 1
                        monthly_salad += 1
            allmain += monthly_main
            allsalad += monthly_salad
            personsreplica = persons.copy()
            persons.sort(key=lambda x: x.first_name)
            for person in persons:
                index = personsreplica.index(person)
                data.append(
                    [
                        f"{person.first_name} {person.last_name}",
                        "",
                        f"{foodgroups[index][1]:.2f}".replace(".", ","),
                        f"{foodgroups[index][2]:.2f}".replace(".", ","),
                    ]
                )
            data.append(
                [
                    "",
                    "____________________________________________________________",
                    "",
                    "",
                ]
            )
            monatalsname = MONATE[month - 1]
            StringMonat = f"Summe {monatalsname} {year}"
            data.append(
                [
                    "",
                    StringMonat,
                    f"{monthly_main:.2f}".replace(".", ","),
                    f"{monthly_salad:.2f}".replace(".", ","),
                ]
            )
            data.append(["", "", "", ""])

        data.append(
            [
                "",
                "Gesamt:",
                f"{allmain:.2f}".replace(".", ","),
                f"{allsalad:.2f}".replace(".", ","),
            ]
        )

        table = Table(data, colWidths=[225, 100, 90, 90])  # Gesamt: 505
        table.setStyle(
            TableStyle(
                [
                    ("LINEABOVE", (0, 0), (-1, 0), 0.7, colors.black),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.7, colors.black),
                    ("FONTNAME", (0, 0), (3, 0), FONT_BOLD),
                    ("FONTNAME", (0, 1), (3, -1), FONT_NORMAL),
                    ("FONTSIZE", (0, 0), (3, -1), FONT_SIZE_NORMAL),
                    ("BACKGROUND", (-1, -1), (-1, -1), colors.white),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                    ("ALIGN", (0, 0), (0, -1), "LEFT"),
                    ("ALIGN", (2, 0), (3, -1), "RIGHT"),
                    ("ALIGN", (1, 0), (1, -1), "LEFT"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("LINEABOVE", (0, -1), (-1, -1), 0.7, colors.black),
                    ("LINEBELOW", (1, -1), (-1, -1), 1, colors.black),
                    ("FONTNAME", (0, -1), (-1, -1), FONT_BOLD),
                    ("TOPPADDING", (0, -1), (-1, -1), 2),
                ]
            )
        )
        elements.append(table)

        pdf.build(elements)
        buffer.seek(0)

        response = make_response(
            send_file(
                buffer,
                mimetype="application/pdf",
                as_attachment=True,
                download_name=f"Rechnung_{start_date}_bis_{end_date}_{group.group_name}.pdf",
            )
        )
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"

        return response
