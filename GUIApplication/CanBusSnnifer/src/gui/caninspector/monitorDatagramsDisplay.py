#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt

from src.gui.sharedcomponets import GUIToolKit
from src.gui.sharedcomponets import ShowdatagramsViewTable


class MonitorDisplayWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        """Constructor for ToolsWidget"""
        super().__init__(parent)

        self.startTime = None
        self.setObjectName("monitorTab")
        self.monitorTabVerticalLayout = QtWidgets.QVBoxLayout(self)
        self.monitorTabVerticalLayout.setObjectName("monitorTabVerticalLayou")
        self.monitorTable = ShowdatagramsViewTable(self)

        self.monitorTableModel = MonitorTableModel(self.startTime)
        self.monitorTable.setModel(self.monitorTableModel)
        self.monitorTabVerticalLayout.addWidget(self.monitorTable)

    def addNewDatagramToDisplay(self,candatagram):
        self.monitorTable.model().addDatagram(candatagram)

    def clearTable(self):
        self.monitorTableModel = MonitorTableModel(self.startTime)
        self.monitorTable.setModel(self.monitorTableModel)

    def setStartTimeStamp(self,time):
        self.monitorTable.model().startTime = int(time)

class MonitorTableModel(QtCore.QAbstractTableModel):
    def __init__(self, startimeSource):
        super(MonitorTableModel, self).__init__()
        self.startTime = startimeSource
        self.hashedDatagrams = {}
        self.columNames = ("Period", "Count", "Type", "Id", "Data")
        self.displayFlag = "HEX"
        self.datagramCounter =0

    def data(self, qIndex, role=None):
        # qIndex is the qIndex of the column/row.
        keyList = list(self.hashedDatagrams.keys())
        if role == Qt.DisplayRole:
            period = self.hashedDatagrams[keyList[qIndex.row()]][0]
            count = self.hashedDatagrams[keyList[qIndex.row()]][1]
            datagram = self.hashedDatagrams[keyList[qIndex.row()]][2]
            if qIndex.column() == 0:
                return str(period)
            elif qIndex.column() == 1:
                return str(count)
            elif qIndex.column() == 3:
                return str(datagram.messageID)
            elif qIndex.column() == 4:
                if datagram.data == None:
                    return ""
                else:
                    return str(datagram.dataToString(displayFlag=self.displayFlag))
        if role == Qt.DecorationRole:
            datagram = self.hashedDatagrams[keyList[qIndex.row()]][2]
            if qIndex.column() == 2:
                if datagram.getDatagramTypeCode() == "R":
                    return GUIToolKit.getIconByName("reddot")
                elif datagram.getDatagramTypeCode() == "r":
                    return GUIToolKit.getIconByName("bluedot")
                elif datagram.getDatagramTypeCode() == "T":
                    return GUIToolKit.getIconByName("orangedot")
                elif datagram.getDatagramTypeCode() == "t":
                    return GUIToolKit.getIconByName("greendot")
        if role == Qt.TextAlignmentRole:
            if qIndex.column() == 1:
                return Qt.AlignVCenter + Qt.AlignCenter
            if qIndex.column() == 3:
                return Qt.AlignVCenter + Qt.AlignRight
    def updateAll(self):
        self.dataChanged.emit(self.index(0, 0),self.index(self.rowCount(), self.columnCount()))

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.hashedDatagrams)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.columNames)

    def headerData(self, section, orientation, role=None):
        # section is the qIndex of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.columNames[section])

    def addDatagram(self, datagram):
        if datagram.messageID in self.hashedDatagrams:
            self.datagramCounter +=1
            count = self.hashedDatagrams[datagram.messageID][1]
            lastArrival = self.hashedDatagrams[datagram.messageID][3]
            currentTime = self.current_milli_time()
            currentPeriod = currentTime - lastArrival
            self.hashedDatagrams.update({datagram.messageID: (currentPeriod, count +1 , datagram,currentTime)})
            row = list(self.hashedDatagrams.keys()).index(datagram.messageID)
            self.dataChanged.emit(self.index(0, row), self.index(4, row))
        else:
            # add entry
            newRow = len(self.hashedDatagrams)
            self.beginInsertRows(QtCore.QModelIndex(), newRow, newRow)
            currentTime = self.current_milli_time()
            initialPeriod = currentTime - self.startTime
            self.hashedDatagrams.update({datagram.messageID:(initialPeriod, 0, datagram, currentTime)})
            self.endInsertRows()

    def current_milli_time(self):
        return int(round(time.time() * 1000))