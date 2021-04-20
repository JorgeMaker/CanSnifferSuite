#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from src.gui.sharedcomponets import GUIToolKit
from src.gui.sharedcomponets import ShowdatagramsViewTable


class TraceDisplayWidget(QtWidgets.QTabWidget):

    def __init__(self, parent=None):
        """Constructor for ToolsWidget"""
        super().__init__(parent)
        self.setObjectName("traceTab")
        self.startTime = None
        self.traceTabVerticalLayout = QtWidgets.QVBoxLayout(self)
        self.traceTabVerticalLayout.setObjectName("traceTabVerticalLayou")
        self.traceTable = ShowdatagramsViewTable(self)
        self.traceTableModel = TraceTableModel(self.startTime)
        self.traceTable.setModel(self.traceTableModel)
        self.traceTabVerticalLayout.addWidget(self.traceTable)

    def addNewDatagramToDisplay(self, datagram):
        self.traceTable.model().addDatagram(datagram)

    def clearTable(self):
        self.traceTableModel = TraceTableModel(self.startTime)
        self.traceTable.setModel(self.traceTableModel)

    def setStartTimeStamp(self,time):
        self.traceTableModel.startTime = int(time)

class TraceTableModel(QtCore.QAbstractTableModel):
    def __init__(self, startimeSource):
        super(TraceTableModel, self).__init__()
        self.startTime = startimeSource
        self.datagramsTimedList = []
        self.columNames = ("Time (ms)", "Type", "ID", "DLC", "Data")
        self.displayFlag = "HEX"

    def data(self, index, role=None):
        if role == Qt.DisplayRole:
            timestamp = self.datagramsTimedList[index.row()][0]
            datagram = self.datagramsTimedList[index.row()][1]

            if index.column() == 0:
                return str(timestamp)
            elif index.column() == 2:
                return str(datagram.messageID)
            elif index.column() == 3:
                return str(datagram.dlc)
            elif index.column() == 4:
                if datagram.data == None:
                    return ""
                else:
                    return str(datagram.dataToString(displayFlag=self.displayFlag))
        if role == Qt.DecorationRole:
            datagram = self.datagramsTimedList[index.row()][1]
            if index.column() == 1:
                if datagram.getDatagramTypeCode() == "R":
                    return GUIToolKit.getIconByName("reddot")
                elif datagram.getDatagramTypeCode() == "r":
                    return GUIToolKit.getIconByName("bluedot")
                elif datagram.getDatagramTypeCode() == "T":
                    return GUIToolKit.getIconByName("orangedot")
                elif datagram.getDatagramTypeCode() == "t":
                    return GUIToolKit.getIconByName("greendot")
        if role == Qt.TextAlignmentRole:
            if index.column() == 3:
                return Qt.AlignVCenter + Qt.AlignCenter
            if index.column() == 2:
                return Qt.AlignVCenter + Qt.AlignRight

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.datagramsTimedList)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.columNames)

    def headerData(self, section, orientation, role=None):
        # section is the qIndex of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.columNames[section])
    def updateAll(self):
        self.dataChanged.emit(self.index(0, 0),self.index(self.rowCount(), self.columnCount()))

    def addDatagram(self, datagram):
        newRow = len(self.datagramsTimedList)
        self.beginInsertRows(QtCore.QModelIndex(), newRow, newRow)

        currentTime =  self.current_milli_time()
        timeStamp = currentTime - self.startTime

        self.datagramsTimedList.append((timeStamp, datagram))
        self.endInsertRows()

    def current_milli_time(self):
        return int(round(time.time() * 1000))