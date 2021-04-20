#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from PyQt5 import QtWidgets, QtCore
from src.gui.sharedcomponets import GUIToolKit
from src.gui.sharedcomponets import SerialPortComboBox


class SnifferControlWidget(QtWidgets.QWidget):

    snniferStarts = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, sniffer=None):
        """Constructor for ToolsWidget"""
        super().__init__(parent)

        self.setObjectName("sniffercontrlwidget")
        self.sniffer = sniffer

        self.gridLayout = QtWidgets.QGridLayout(self)

        self.gridLayout.setObjectName("horizontalLayout")

        self.serialPortLabel = QtWidgets.QLabel(self)
        self.serialPortLabel.setObjectName("serialPortLabel")
        self.gridLayout.addWidget(self.serialPortLabel, 1, 0, 1, 1)

        self.serialPortComboBox = SerialPortComboBox(self)
        self.serialPortComboBox.setEditable(False)

        self.serialPortComboBox.setObjectName("serialPortComboBox")
        self.serialPortComboBox.setMinimumWidth(150)
        self.gridLayout.addWidget(self.serialPortComboBox, 1, 2, 1, 1)

        self.canbitrateLabel = QtWidgets.QLabel(self)
        self.canbitrateLabel.setObjectName("sepeedBusLabel")
        self.gridLayout.addWidget(self.canbitrateLabel, 2, 0, 1, 1)

        self.busSpeedComboBox = QtWidgets.QComboBox(self)
        self.busSpeedComboBox.setObjectName("busSpeedComboBox")
        self.busSpeedComboBox.addItems(self.sniffer.canBusBitRates.keys())

        self.busSpeedComboBox.setMinimumWidth(120)
        self.gridLayout.addWidget(self.busSpeedComboBox, 2, 2, 1, 1)

        self.modeLabel = QtWidgets.QLabel(self)
        self.modeLabel.setObjectName("modeLabel")
        self.gridLayout.addWidget(self.modeLabel, 1, 3, 1, 1)

        self.modeComboBox = QtWidgets.QComboBox(self)
        self.modeComboBox.setObjectName("modeComboBox")
        self.modeComboBox.addItems(self.sniffer.canBusModes.keys())

        self.modeComboBox.setMinimumWidth(120)
        self.gridLayout.addWidget(self.modeComboBox, 1, 4, 1, 1)

        self.connectDisconnectButton = QtWidgets.QPushButton(self)
        self.connectDisconnectButton.setObjectName("connectDisconnectButton")
        self.connectDisconnectButton.clicked.connect(
            self.connectDisconnectSnnifer)
        self.connectDisconnectButton.setMinimumWidth(120)
        self.connectDisconnectButton.setIcon(
            GUIToolKit.getIconByName("connect"))
        self.gridLayout.addWidget(self.connectDisconnectButton, 1, 6, 1, 1)

        self.startStopButton = QtWidgets.QPushButton(self)
        self.startStopButton.setIcon(GUIToolKit.getIconByName("start"))
        self.startStopButton.setObjectName("startStopButton")
        self.startStopButton.clicked.connect(self.startStopSnifer)
        self.startStopButton.setMinimumWidth(120)
        self.startStopButton.setEnabled(False)
        self.gridLayout.addWidget(self.startStopButton, 2, 6, 1, 1)

        self.clearButton = QtWidgets.QPushButton(self)
        self.clearButton.setObjectName("clearButton")
        self.clearButton.setMinimumWidth(120)
        self.clearButton.setIcon(GUIToolKit.getIconByName("delete"))
        self.gridLayout.addWidget(self.clearButton, 1, 7, 1, 1)

        self.rebootButton = QtWidgets.QPushButton(self)
        self.rebootButton.setObjectName("rebootButton")
        self.rebootButton.setIcon(GUIToolKit.getIconByName("reboot"))
        self.rebootButton.setMinimumWidth(120)
        self.gridLayout.addWidget(self.rebootButton, 2, 7, 1, 1)

        spacerItem = QtWidgets.QSpacerItem(40, 20,
                                           QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 5, 1, 1)

        spacerItem = QtWidgets.QSpacerItem(40, 20,
                                           QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Minimum)

        # self.statuslineEdit = QtWidgets.QLineEdit(self)
        # self.statuslineEdit.setObjectName("statuslineEdit")
        # self.statuslineEdit.setEnabled(False)

        self.gridLayout.addItem(spacerItem, 2, 3, 1, 3)





        self.serialPortLabel.setText("Serial Port")
        self.canbitrateLabel.setText("CAN Bit rate")
        self.modeLabel.setText("Mode")
        self.connectDisconnectButton.setText("Serial connect")
        self.startStopButton.setText("Start")
        self.clearButton.setText("Clear tables")
        self.rebootButton.setText("Reboot sniffer")

        self.rebootButton.setEnabled(False)
        self.clearButton.setEnabled(False)

        self.modeLabel.setEnabled(False)
        self.canbitrateLabel.setEnabled(False)
        self.busSpeedComboBox.setEnabled(False)
        self.modeComboBox.setEnabled(False)

        self.modeComboBox.currentTextChanged.connect(self.sendModeCommand)
        self.busSpeedComboBox.currentTextChanged.connect(self.sendBitrateCommand)

        self.rebootButton.clicked.connect(self.rebbotAction)

    def rebbotAction(self):
        self.sniffer.rebootDevice()


    def connectDisconnectSnnifer(self):
        if self.sniffer.isConnected:
            # Diconnect Serial Action
            self.sniffer.disconnectSerial()

            self.connectDisconnectButton.setIcon(
                GUIToolKit.getIconByName("connect"))
            self.connectDisconnectButton.setText("Serial connect")
            self.startStopButton.setEnabled(False)
            self.serialPortComboBox.setEnabled(True)
            self.rebootButton.setEnabled(False)
            self.modeLabel.setEnabled(False)
            self.canbitrateLabel.setEnabled(False)
            self.busSpeedComboBox.setEnabled(False)
            self.modeComboBox.setEnabled(False)

        else:
            # Connect Serial Action
            self.sniffer.serialPortName = self.serialPortComboBox.currentText()
            self.sniffer.connectSerial()
            self.connectDisconnectButton.setIcon(
                GUIToolKit.getIconByName("disconnect"))
            self.connectDisconnectButton.setText("Serial disconnect")
            self.startStopButton.setEnabled(True)
            self.startStopButton.setIcon(GUIToolKit.getIconByName("start"))
            self.startStopButton.setText("Start")
            self.serialPortComboBox.setEnabled(False)
            self.sniffer.isSnifing = False

            self.modeLabel.setEnabled(True)
            self.canbitrateLabel.setEnabled(True)
            self.busSpeedComboBox.setEnabled(True)
            self.modeComboBox.setEnabled(True)
            self.rebootButton.setEnabled(True)

    def startStopSnifer(self):
        if self.sniffer.isSnifing:
            # Stop Action
            self.startStopButton.setText("Start")
            self.startStopButton.setIcon(GUIToolKit.getIconByName("start"))
            self.clearButton.setEnabled(True)
            self.canbitrateLabel.setEnabled(True)
            self.modeLabel.setEnabled(True)
            self.modeComboBox.setEnabled(True)
            self.busSpeedComboBox.setEnabled(True)
            self.stopSnifing()

        else:
            # Start Action
            self.startStopButton.setText("Stop")
            self.startStopButton.setIcon(GUIToolKit.getIconByName("stop"))
            self.snniferStarts.emit(str(self.current_milli_time()))
            self.clearButton.setEnabled(False)
            self.canbitrateLabel.setEnabled(False)
            self.modeLabel.setEnabled(False)
            self.modeComboBox.setEnabled(False)
            self.busSpeedComboBox.setEnabled(False)
            self.statrtSnifing()



    def current_milli_time(self):
        return int(round(time.time() * 1000))

    def statrtSnifing(self):
        self.sendModeCommand()
        time.sleep(0.1)
        self.sendBitrateCommand()
        time.sleep(0.1)
        self.sniffer.startSniffing()

    def stopSnifing(self):
        self.sniffer.stopSniffing()


    def sendModeCommand(self):
        self.sniffer.sendModeCommand(self.modeComboBox.currentText())

    def sendBitrateCommand(self):
        self.sniffer.sendBitrateCommand(self.busSpeedComboBox.currentText())
