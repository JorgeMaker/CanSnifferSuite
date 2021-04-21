#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets

from src.gui.caninspector.canSnifferDevice import CanSnifferDevice
from src.gui.caninspector.sendCanDatagramsWidget import SendCANDatagramsWidget
from src.gui.caninspector.showDatagramsWidget import ShowDatagramsWidget
from src.gui.caninspector.controlSniffer import SnifferControlWidget
from src.gui.caninspector.tableControlWidget import TableControlWidget
from src.gui.sharedcomponets import GUIToolKit
from src.gui.sharedcomponets import WorkAreaTabWidget


class CandInspectorToolWidget(WorkAreaTabWidget):

    def __init__(self, parent=None,simpleFocConn=None):
        """Constructor for ToolsWidget"""
        super().__init__(parent)

        self.sniffer = CanSnifferDevice()
        self.setObjectName("CandInspectorToolWidget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("traceTabVerticalLayout")

        self.controlSnniferWidget = SnifferControlWidget(self, sniffer=self.sniffer)
        self.showDatagramsWidget = ShowDatagramsWidget(self)
        self.tableControlWidget = TableControlWidget(self, tablesWidget=self.showDatagramsWidget)
        self.datagramsSender = SendCANDatagramsWidget(self, sniffer=self.sniffer)


        self.verticalLayout.addWidget(self.controlSnniferWidget)
        self.verticalLayout.addWidget(self.showDatagramsWidget)
        self.verticalLayout.addWidget(self.tableControlWidget)
        self.verticalLayout.addWidget(self.datagramsSender)

        self.sniffer.datagramReceived.connect(self.showDatagramsWidget.canMessageReceived)
        self.controlSnniferWidget.clearButton.clicked.connect(self.showDatagramsWidget.clearTables)
        self.controlSnniferWidget.snniferStarts.connect(self.showDatagramsWidget.traceTab.setStartTimeStamp)
        self.controlSnniferWidget.snniferStarts.connect(self.showDatagramsWidget.monitorTab.setStartTimeStamp)

        self.sniffer.addConnectionStateListener(self.datagramsSender)

    def getTabIcon(self):
        return GUIToolKit.getIconByName("canbus")

    def getTabName(self):
        return "CAN"