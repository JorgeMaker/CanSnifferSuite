#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets
from src.gui.caninspector.canSnifferDevice import CanSnifferDevice
from src.gui.caninspector.sendCanDatagramsWidget import SendCANDatagramsWidget
from src.gui.caninspector.showDatagramsWidget import ShowDatagramsWidget
from src.gui.caninspector.controlSniffer import SnifferControlWidget
from src.gui.caninspector.tableControlWidget import TableControlWidget

class UserInteractionMainWindow(object):

    """This class creates athe main window for the application  """
    def setupUi(self, main_window):

        main_window.setObjectName("CandInspectorToolWidget")
        main_window.resize(1050, 900)
        main_window.setWindowTitle("Nauthilus CAN Bus Snnifer")

        self.centralwidget = QtWidgets.QWidget(main_window)
        self.centralwidget.setObjectName("centralwidget")

        self.sniffer = CanSnifferDevice()

        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")

        self.controlSnniferWidget = SnifferControlWidget(self.centralwidget, sniffer=self.sniffer)
        self.showDatagramsWidget = ShowDatagramsWidget(self.centralwidget)
        self.tableControlWidget = TableControlWidget(self.centralwidget, tablesWidget=self.showDatagramsWidget)
        self.datagramsSender = SendCANDatagramsWidget(self.centralwidget, sniffer=self.sniffer)


        self.sniffer.datagramReceived.connect(self.showDatagramsWidget.canMessageReceived)
        self.controlSnniferWidget.clearButton.clicked.connect(self.showDatagramsWidget.clearTables)
        self.controlSnniferWidget.snniferStarts.connect(self.showDatagramsWidget.traceTab.setStartTimeStamp)
        self.controlSnniferWidget.snniferStarts.connect(self.showDatagramsWidget.monitorTab.setStartTimeStamp)

        self.sniffer.addConnectionStateListener(self.datagramsSender)

        self.verticalLayout.addWidget(self.controlSnniferWidget)
        self.verticalLayout.addWidget(self.showDatagramsWidget)
        self.verticalLayout.addWidget(self.tableControlWidget)
        self.verticalLayout.addWidget(self.datagramsSender)

        main_window.setCentralWidget(self.centralwidget)

        # Add layout de to the main window
        self.horizontalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("traceTabVerticalLayout")

        # Add status bar to the main window
        self.statusbar = QtWidgets.QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)

        # Add central Widget to the main window
        main_window.setCentralWidget(self.centralwidget)

