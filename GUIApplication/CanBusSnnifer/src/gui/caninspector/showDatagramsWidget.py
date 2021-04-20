#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from src.gui.caninspector.monitorDatagramsDisplay import MonitorDisplayWidget
from src.gui.caninspector.traceDatragramsDisplay import TraceDisplayWidget


class ShowDatagramsWidget(QtWidgets.QTabWidget):

    def __init__(self, parent=None):
        """Constructor for ToolsWidget"""
        super().__init__(parent)
        self.setObjectName("showDatagramsWidget")

        self.monitorTab = MonitorDisplayWidget()
        self.addTab(self.monitorTab, "Monitor")

        self.traceTab = TraceDisplayWidget()
        self.addTab(self.traceTab, "Trace")

        self.setCurrentIndex(0)

    def canMessageReceived(self, candatagram):
        self.traceTab.addNewDatagramToDisplay(candatagram)
        self.monitorTab.addNewDatagramToDisplay(candatagram)

    def clearTables(self):
        self.monitorTab.clearTable()
        self.traceTab.clearTable()

    def getStartTimeStamp(self, time):
        self.traceTab.setStartTimeStamp(time)
        self.monitorTab.setStartTimeStamp(time)

