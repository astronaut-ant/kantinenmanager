from typing import List
from flask import send_file, Response, make_response
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
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
from src.repositories.orders_repository import OrdersFilters
from src.models.oldorder import OldOrder


class PDFCreationUtils:

    ################################# QR-Code PDF #################################
    @staticmethod
    def create_qr_code(person: Person):
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
        qr_size = 200
        x_center = (page_width - qr_size) / 2
        y_position = (page_height / 2) + 180  # Position in der oberen Hälfte

        # BytesIO-Objekt in ein ImageReader-Objekt umwandeln, um das QR-Code-Bild in die Canvas einzubetten
        qr_image = ImageReader(qr_buffer)
        c.drawImage(qr_image, x_center, y_position, width=qr_size, height=qr_size)

        # Text unterhalb des QR-Codes hinzufügen
        text_y_position = y_position - 20
        c.setFont("Helvetica", 12)
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

    ################################# Reports PDF #################################

    @staticmethod
    def create_pdf_report(filters: OrdersFilters, location_counts: dict) -> Response:

        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        date_str = PDFCreationUtils._get_date_string(filters)
        if not date_str:
            raise ValueError("Kein Datum übergeben")

        elements.append(Paragraph(f"Datum: {date_str}", styles["Heading2"]))
        elements.append(Spacer(1, 12))

        for location, counts in location_counts.items():
            location_block = PDFCreationUtils._create_location_pdf_block(
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

    def _create_footer_and_header(canvas, doc):
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

    ################################# Invoice PDF Person #################################

    @staticmethod
    def create_pdf_invoice_person(start, end, orders: List[OldOrder]) -> Response:
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
        current_year = start.year
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
                data.append(
                    [
                        "3001",
                        "Abzug Vorrauszahlung",
                        f"{current_month}.{current_year}",
                        "-70,00",
                        "1,00",
                        "-70,00",
                    ]
                )
                data.append(["", "Mittagessen", "", "", "", ""])
                gesamtpreis -= 70
                monatssumme = -70
                for time in orderarray:
                    start = time[1].strftime("%d.%m.%Y").replace(f"{current_year}", "")
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
                StringMonat = f"Summe {monatalsname} {current_year}"
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
                    current_year += 1
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
                download_name=f"Rechnung_{start}_bis_{end}_{Name}.pdf",
            )
        )
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"

        return response

    ################################# Location Invoice PDF #################################
    def create_pdf_invoice_location():
        pass

    ################################# Group Invoice PDF #################################
    def create_pdf_invoice_group():
        pass
