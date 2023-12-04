# pdf.py
# Copyright (c) 2023  Delvian Valentine <delvian.valentine@gmail.com>

from PySide6.QtCore import Qt, QDate, QFile, QTemporaryFile
from PySide6.QtGui import QImage

from reportlab.lib.colors import black
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.pdfbase.pdfmetrics import registerFont, registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from . import DATA

FONTS = DATA / "fonts"


def _business_contact_details(window):
    address = window.settings.value("business_address")
    city = window.settings.value("business_city")
    province = window.settings.value("business_province")
    post_code = window.settings.value("business_post_code")
    country = window.settings.value("business_country")
    phone = window.settings.value("business_phone")
    email = window.settings.value("business_email")
    website = window.settings.value("business_website")
    reg_num = window.settings.value("business_reg_num")

    contact_details = []
    if address:
        contact_details.append(address)
    if city and province:
        contact_details.append(f"{city}, {province}")
    else:
        if city:
            contact_details.append(city)
        if province:
            contact_details.append(province)
    if post_code and country:
        contact_details.append(f"{post_code}, {country}")
    else:
        if post_code:
            contact_details.append(post_code)
        if country:
            contact_details.append(country)
    if phone:
        contact_details.append(phone)
    if email:
        contact_details.append(email)
    if website:
        contact_details.append(website)
    if reg_num:
        contact_details.append(f"Reg. number: {reg_num}")

    return "<br />".join(contact_details)


def _business_logo(window):
    window.temp_file = QTemporaryFile()
    window.temp_file.open()
    temp_file = f"{window.temp_file.fileName()}.png"

    logo = QImage(window.settings.value("business_logo")).scaledToHeight(
        128, Qt.SmoothTransformation
    )
    logo.save(temp_file)

    return temp_file, logo.width() / 2, logo.height() / 2


def _customer_contact_details(window):
    name = window.edit_customer_name.text()
    company = window.edit_customer_company.text()
    address = window.edit_customer_address.text()
    city = window.edit_customer_city.text()
    province = window.edit_customer_province.text()
    post_code = window.edit_customer_post_code.text()
    country = window.edit_customer_country.text()
    phone = window.edit_customer_phone.text()
    email = window.edit_customer_email.text()

    contact_details = []
    if name:
        contact_details.append(f"<b>{name}</b>")
    if company:
        contact_details.append(company)
    if address:
        contact_details.append(address)
    if city and province:
        contact_details.append(f"{city}, {province}")
    else:
        if city:
            contact_details.append(city)
        if province:
            contact_details.append(province)
    if post_code and country:
        contact_details.append(f"{post_code}, {country}")
    else:
        if post_code:
            contact_details.append(post_code)
        if country:
            contact_details.append(country)
    if phone:
        contact_details.append(phone)
    if email:
        contact_details.append(email)

    return "<br />".join(contact_details)


def _invoice_total(model_invoice):
    total = 0.00

    for item in model_invoice.items[:-1]:
        total += item[1] * item[2]

    return total


def save_pdf(window, file_name, doc_type="invoice"):
    spacer = Spacer(0, inch / 3)

    business_logo = None
    if (logo := window.settings.value("business_logo")) is not None:
        if QFile.exists(logo):
            business_logo = Image(*_business_logo(window))

    business_name = Paragraph(window.settings.value("business_name"), style_h2)
    business_contact_details = Paragraph(
        _business_contact_details(window), style_normal
    )
    customer_contact_details = Paragraph(
        _customer_contact_details(window), style_normal
    )
    invoice_num = window.edit_invoice_num.value()
    invoice_date = QDate.currentDate().toString("yyyy/MM/dd")
    invoice_due_date = window.edit_invoice_due_date.date().toString("yyyy/MM/dd")

    style_business_details = TableStyle(
        [
            ("SPAN", (0, 0), (0, 1)),
            ("VALIGN", (0, 0), (1, 1), "TOP"),
            ("ALIGN", (0, 0), (0, 0), "RIGHT"),
        ]
    )
    table_business_details = Table(
        [(business_logo, business_name), ("", business_contact_details)],
        style=style_business_details,
    )

    style_billing_details_invoice = TableStyle(
        [
            ("FONT", (0, 0), (-1, -1), "Vera"),
            ("FONT", (0, 0), (0, 0), "VeraBd"),
            ("FONT", (1, 0), (1, 2), "VeraBd"),
            ("ALIGN", (1, 0), (1, 2), "RIGHT"),
            ("SPAN", (0, 1), (0, 5)),
            ("VALIGN", (0, 1), (0, 1), "TOP"),
        ]
    )
    style_billing_details_quote = TableStyle(
        [
            ("FONT", (0, 0), (-1, -1), "Vera"),
            ("FONT", (0, 0), (0, 0), "VeraBd"),
            ("FONT", (1, 0), (1, 1), "VeraBd"),
            ("ALIGN", (1, 0), (1, 1), "RIGHT"),
            ("SPAN", (0, 1), (0, 5)),
            ("VALIGN", (0, 1), (0, 1), "TOP"),
        ]
    )
    table_billing_details_invoice = Table(
        [
            ("BILL TO", "#", invoice_num),
            (customer_contact_details, "Date", invoice_date),
            ("", "Due Date", invoice_due_date),
            ("", "", ""),
            ("", "", ""),
            ("", "", ""),
        ],
        colWidths=(100 * mm, 25 * mm, 25 * mm),
        style=style_billing_details_invoice,
    )
    table_billing_details_quote = Table(
        [
            ("BILL TO", "#", invoice_num),
            (customer_contact_details, "Date", invoice_date),
            ("", "", ""),
            ("", "", ""),
            ("", "", ""),
            ("", "", ""),
        ],
        colWidths=(100 * mm, 25 * mm, 25 * mm),
        style=style_billing_details_quote,
    )
    if doc_type == "invoice":
        table_billing_details = table_billing_details_invoice
    else:
        table_billing_details = table_billing_details_quote

    items = [("Description", "Quantity", "Price")]
    for item in window.model_invoice.items[:-1]:
        items.append((item[0], item[1], f"{item[2]:,.2f}"))
    items.append(("", "Total", f"{_invoice_total(window.model_invoice):,.2f}"))
    style_items = TableStyle(
        [
            ("FONT", (0, 0), (-1, -1), "Vera"),
            ("FONT", (0, 0), (2, 0), "VeraBd"),
            ("FONT", (1, -1), (2, -1), "VeraBd"),
            ("ALIGN", (0, 0), (2, 0), "CENTER"),
            ("ALIGN", (1, 1), (2, -1), "RIGHT"),
            ("BOX", (0, 0), (-1, -2), 1, black),
            ("BOX", (1, -1), (-1, -1), 1, black),
            ("INNERGRID", (0, 0), (-1, -1), 0.1, black),
            ("LINEBELOW", (0, 0), (2, 0), 1, black),
            ("LINEBELOW", (0, "splitlast"), (2, "splitlast"), 1, black),
        ]
    )
    table_items = Table(
        items, colWidths=(100 * mm, 25 * mm, 30 * mm), style=style_items, repeatRows=1
    )

    story = [
        table_business_details,
        Spacer(0, inch / 2),
        Paragraph(doc_type.upper(), style_title),
        spacer,
        table_billing_details,
        spacer,
        table_items,
    ]

    doc = SimpleDocTemplate(file_name, title=doc_type.title(), author="Yocto Invoice")

    try:
        doc.build(story)
    except OSError as err:
        print(err)
        raise


def save_quote(window, file_name):
    save_pdf(window, file_name, "quote")


registerFont(TTFont("Vera", FONTS / "Vera.ttf"))
registerFont(TTFont("VeraBd", FONTS / "VeraBd.ttf"))
registerFont(TTFont("VeraIt", FONTS / "VeraIt.ttf"))
registerFont(TTFont("VeraBI", FONTS / "VeraBI.ttf"))
registerFontFamily(
    "Vera", normal="Vera", bold="VeraBd", italic="VeraIt", boldItalic="VeraBI"
)

style_normal = ParagraphStyle("Normal", fontName="Vera", fontSize=10, leading=12)
style_title = ParagraphStyle(
    "Title",
    fontName="VeraBd",
    fontSize=18,
    leading=22,
    alignment=TA_CENTER,
    spaceAfter=6,
)
style_h2 = ParagraphStyle(
    "Heading2", fontName="VeraBd", fontSize=14, leading=18, spaceBefore=12, spaceAfter=6
)
