# ui.py
# Copyright (c) 2023  Delvian Valentine <delvian.valentine@gmail.com>

from PySide6.QtCore import QDate, QDir, QFile, QSettings
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QFileDialog, QHeaderView

from . import DATA, version

from . import pdf
from .models import InvoiceModel, PriceEditor, QtyEditor

ICONS = DATA / "icons"
UI = DATA / "ui"
HOME = QDir.homePath()

HOME = QDir.homePath()


def _set_business_logo(dialog, file_name):
    dialog.button_business_logo.setText("")
    dialog.button_business_logo.setIcon(QIcon(file_name))
    dialog.business_logo = file_name


def browse_business_logo(dialog):
    if file_name := QFileDialog.getOpenFileName(
        dialog, dir=HOME, filter="Images (*.png *.jpg *.jpeg)"
    )[0]:
        _set_business_logo(dialog, file_name)


def new_invoice(window):
    window.edit_customer_name.setText("")
    window.edit_customer_company.setText("")
    window.edit_customer_address.setText("")
    window.edit_customer_city.setText("")
    window.edit_customer_province.setText("")
    window.edit_customer_post_code.setText("")
    window.edit_customer_country.setText("")
    window.edit_customer_phone.setText("")
    window.edit_customer_email.setText("")

    today = QDate.currentDate()
    window.edit_invoice_num.setValue(1)
    window.edit_invoice_due_date.setDate(today)

    window.model_invoice.beginResetModel()
    window.model_invoice.items = [["", "", ""]]
    window.model_invoice.endResetModel()

    window.label_invoice_total.setText("0.00")


def save_invoice(ui_loader, window):
    if file_name := QFileDialog.getSaveFileName(
        window, dir=f"{HOME}/Invoice.pdf", filter="PDFs (*.pdf)"
    )[0]:
        try:
            pdf.save_invoice(window, file_name)
        except OSError as err:
            dialog = ui_loader.load(UI / "error.ui", window)
            dialog.label_error.setText("An error occurred while saving your invoice")
            dialog.label_description.setText(
                f"[Error #{err.errno}] {err.strerror}<br /><em>{err.filename}</em>"
            )
            dialog.exec()


def save_quote(ui_loader, window):
    if file_name := QFileDialog.getSaveFileName(
        window, dir=f"{HOME}/Quote.pdf", filter="PDFs (*.pdf)"
    )[0]:
        try:
            pdf.save_quote(window, file_name)
        except OSError as err:
            dialog = ui_loader.load(UI / "error.ui", window)
            dialog.label_error.setText("An error occurred while saving your quote")
            dialog.label_description.setText(
                f"[Error #{err.errno}] {err.strerror}<br /><em>{err.filename}</em>"
            )
            dialog.exec()


def show_about(ui_loader, window):
    dialog = ui_loader.load(UI / "about.ui", window)
    dialog.label_icon.setPixmap(QPixmap(ICONS / "icon.png"))
    dialog.label_version.setText(version())
    dialog.exec()


def show_business_details(ui_loader, window):
    dialog = ui_loader.load(UI / "business_details.ui", window)
    dialog.business_logo = None

    dialog.edit_business_name.setText(window.settings.value("business_name"))
    dialog.edit_business_address.setText(window.settings.value("business_address"))
    dialog.edit_business_city.setText(window.settings.value("business_city"))
    dialog.edit_business_province.setText(window.settings.value("business_province"))
    dialog.edit_business_post_code.setText(window.settings.value("business_post_code"))
    dialog.edit_business_country.setText(window.settings.value("business_country"))
    dialog.edit_business_phone.setText(window.settings.value("business_phone"))
    dialog.edit_business_email.setText(window.settings.value("business_email"))
    dialog.edit_business_website.setText(window.settings.value("business_website"))
    dialog.edit_business_reg_num.setText(window.settings.value("business_reg_num"))

    if (business_logo := window.settings.value("business_logo")) is not None:
        if QFile.exists(business_logo):
            _set_business_logo(dialog, business_logo)

    dialog.button_business_logo.clicked.connect(lambda: browse_business_logo(dialog))

    if dialog.exec():
        window.settings.setValue("business_name", dialog.edit_business_name.text())
        window.settings.setValue(
            "business_address", dialog.edit_business_address.text()
        )
        window.settings.setValue("business_city", dialog.edit_business_city.text())
        window.settings.setValue(
            "business_province", dialog.edit_business_province.text()
        )
        window.settings.setValue(
            "business_post_code", dialog.edit_business_post_code.text()
        )
        window.settings.setValue(
            "business_country", dialog.edit_business_country.text()
        )
        window.settings.setValue("business_phone", dialog.edit_business_phone.text())
        window.settings.setValue("business_email", dialog.edit_business_email.text())
        window.settings.setValue(
            "business_website", dialog.edit_business_website.text()
        )
        window.settings.setValue(
            "business_reg_num", dialog.edit_business_reg_num.text()
        )
        window.settings.setValue("business_logo", dialog.business_logo)


def update_invoice_total(window):
    total = 0.00

    for item in window.model_invoice.items[:-1]:
        total += item[1] * item[2]

    window.label_invoice_total.setText(f"{total:,.2f}")


def main():
    app = QApplication([])
    app.setApplicationName("Yocto Invoice")
    # app.setWindowIcon(QIcon(f"{ICONS}/icon.png"))

    ui_loader = QUiLoader()

    window = ui_loader.load(UI / "main.ui")
    window.settings = QSettings("Yocto", "Invoice")

    window.action_new.setIcon(QIcon(f"{ICONS}/new.svg"))
    window.action_save.setIcon(QIcon(f"{ICONS}/save.svg"))
    window.action_new.triggered.connect(lambda: new_invoice(window))
    window.action_save.triggered.connect(lambda: save_invoice(ui_loader, window))
    window.action_save_quote.triggered.connect(lambda: save_quote(ui_loader, window))
    window.action_business_details.triggered.connect(
        lambda: show_business_details(ui_loader, window)
    )
    window.action_about.triggered.connect(lambda: show_about(ui_loader, window))

    today = QDate.currentDate()
    window.edit_invoice_due_date.setDate(today)
    window.edit_invoice_due_date.setMinimumDate(today)

    window.model_invoice = InvoiceModel()
    window.model_invoice.dataChanged.connect(lambda: update_invoice_total(window))

    edit_qty = QtyEditor()
    edit_price = PriceEditor()

    window.table_invoice.setModel(window.model_invoice)
    window.table_invoice.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
    window.table_invoice.setItemDelegateForColumn(1, edit_qty)
    window.table_invoice.setItemDelegateForColumn(2, edit_price)

    window.show()

    if not window.settings.allKeys():
        window.action_business_details.trigger()

    app.exec()
