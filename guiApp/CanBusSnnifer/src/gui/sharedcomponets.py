#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import Qt
import serial.tools.list_ports

class GUIToolKit(object):
    """ This class is used to provide icons for the rest of the application
        hiding the location of the resources
    """
    RED_COLOR = (255, 92, 92)
    GREEN_COLOR = (57, 217, 138)
    BLUE_COLOR = (91, 141, 236)
    ORANGE_COLOR = (253, 172, 66)

    @staticmethod
    def getIconByName(icoName):

        file_index = {
            "add": "add.png",
            "delete": "delete.png",
            "statistics": "statistics.png",
            "reddot": "reddot.png",
            "greendot": "greendot.png",
            "bluedot": "bluedot.png",
            "orangedot": "orangedot.png",
            "purpledot": "purpledot.png",
            "canbus": "canbus.png",
            "reboot": "reboot.png",
            "send": "send.png",
            "zoomall": "zoomall.png",
            "connect": "connect.png",
            "continue": "continue.png",
            "alert": "alert.png",
            "open": "open.png",
            "save": "save.png",
            "stop": "stop.png",
            "restart": "continue.png",
            "start": "start.png",
            "motor": "motor.png",
            "pause": "pause.png",
            "logtofile": "logfile.png",
            "canbusgreen": "canbusgreen.png",
            "disconnect": "disconnect.png",
            "configure": "configure.png"
        }
        currentDir = os.path.dirname(__file__)
        icon_path = os.path.join(currentDir, "resources", file_index[icoName])
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal,
                      QtGui.QIcon.Off)
        return icon


class ConfigQLineEdit(QtWidgets.QLineEdit):
    return_key = 16777220
    updateValue = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        """Constructor for ToolsWidget"""
        super().__init__(parent)

    def keyPressEvent(self, event):
        if event.key() == self.return_key:
            self.updateValue.emit()
        else:
            super().keyPressEvent(event)

class WorkAreaTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        """Constructor for ToolsWidget"""
        super().__init__(parent)

    def getTabIcon(self):
        raise NotImplemented

    def getTabName(self):
        raise NotImplemented

class ShowdatagramsViewTable(QtWidgets.QTableView):
    def __init__(self, parent=None):
        """Constructor for ToolsWidget"""
        super().__init__(parent)
        self.setItemDelegate(self.IconDelegate(self))
        self.formatTableView()

    def formatTableView(self):
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setDragDropOverwriteMode(False)
        self.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setTextElideMode(Qt.ElideRight)
        self.setSortingEnabled(False)
        self.horizontalHeader().setDefaultAlignment(
            Qt.AlignHCenter | Qt.AlignVCenter |
            Qt.AlignCenter)
        self.horizontalHeader().setHighlightSections(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setDefaultSectionSize(20)

    class IconDelegate(QtWidgets.QStyledItemDelegate):
        def initStyleOption(self, option, index):
            super(ShowdatagramsViewTable.IconDelegate, self).initStyleOption(option, index)
            if option.features & QtWidgets.QStyleOptionViewItem.HasDecoration:
                s = option.decorationSize
                s.setWidth(option.rect.width())
                option.decorationSize = s

class SerialPortComboBox(QtWidgets.QComboBox):
    def __init__(self, parent=None, snifer=None):
        """Constructor for ToolsWidget"""
        super().__init__(parent)
        self.addItems(self.getAvailableSerialPortNames())

    def getAvailableSerialPortNames(self):
        portNames = []
        for port in serial.tools.list_ports.comports():
            if port[2] != 'n/a':
                portNames.append(port[0])

        return portNames

    def showPopup(self):
        selectedItem = self.currentText()
        super().clear()
        availableSerialPortNames = self.getAvailableSerialPortNames()
        self.addItems(availableSerialPortNames)
        if selectedItem in availableSerialPortNames:
            self.setCurrentText(selectedItem)
        super().showPopup()