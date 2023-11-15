# models.py
# Copyright (c) 2023  Delvian Valentine <delvian.valentine@gmail.com>

from PySide6.QtCore import Qt, QAbstractTableModel
from PySide6.QtWidgets import QDoubleSpinBox, QSpinBox, QStyledItemDelegate


class InvoiceModel(QAbstractTableModel):
    columns = ("Description", "Quantity", "Price")

    def __init__(self):
        super().__init__()
        self.items = [["", "", ""]]

    def data(self, index, role):
        row, column = index.row(), index.column()
        item = self.items[row][column]

        if role == Qt.DisplayRole:
            if column == 2 and isinstance(item, float):
                return f"{item:,.2f}"
            return item

        if role == Qt.EditRole:
            return item

    def setData(self, index, value, role):
        row, column = index.row(), index.column()
        num_items = len(self.items)
        parent = index.parent()

        if role == Qt.EditRole:
            self.items[row][column] = value

            if value and row == num_items - 1:
                self.items[row][1] = 1
                self.items[row][2] = 0.00
                self.insertRows(row, num_items, parent)

            if value == "" and row != num_items - 1:
                self.removeRows(row, 0, parent)

            self.dataChanged.emit(index, index)
            return True

    def insertRows(self, row, count, parent):
        self.beginInsertRows(parent, row, row)
        self.items.append(["", "", ""])
        self.endInsertRows()
        return True

    def removeRows(self, row, count, parent):
        self.beginRemoveRows(parent, row, row)
        del self.items[row]
        self.endRemoveRows()
        return True

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.columns[section]
            if orientation == Qt.Vertical:
                return section + 1

    def rowCount(self, parent):
        return len(self.items)

    def columnCount(self, parent):
        return len(self.columns)

    def flags(self, index):
        row, column = index.row(), index.column()

        if row == len(self.items) - 1 and (column == 1 or column == 2):
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable


class PriceEditor(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setFrame(False)
        editor.setMinimum(0.00)
        editor.setMaximum(999999.99)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        editor.setValue(value)

    def setModelData(self, editor, model, index):
        editor.interpretText()
        value = editor.value()
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class QtyEditor(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QSpinBox(parent)
        editor.setFrame(False)
        editor.setMinimum(1)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        editor.setValue(value)

    def setModelData(self, editor, model, index):
        editor.interpretText()
        value = editor.value()
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
