#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from PyQt5 import QtGui, QtWidgets, QtCore
from src.gui.caninspector.canDatagram import CANDatagram
from src.gui.sharedcomponets import GUIToolKit
class SendCANDatagramsWidget(QtWidgets.QGroupBox):

    stopLoopSignal = QtCore.pyqtSignal()

    def __init__(self, parent=None, sniffer=None):
        """Constructor for ToolsWidget"""
        super().__init__(parent)

        self.snifferDevice = sniffer

        self.repeatThread = CANMessengerDaemonSender()
        self.setObjectName("sendCANDatagramsWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.sendDatagramsWidget = QtWidgets.QWidget(self)
        self.sendDatagramsWidget.setObjectName("sendDatagramsWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.sendDatagramsWidget)
        self.gridLayout.setObjectName("gridLayout")

        self.messageLabel = QtWidgets.QLabel(self.sendDatagramsWidget)
        self.messageLabel.setObjectName("messageLabel")
        self.gridLayout.addWidget(self.messageLabel, 0, 0, 1, 1)
        self.messageLabel.setText("ID ")

        self.messageIDEdit = self.ByteEditLine(self.sendDatagramsWidget)
        self.messageIDEdit.setObjectName("messageIDEdit")
        self.messageIDEdit.setValidator(QtGui.QIntValidator())
        self.messageIDEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.messageIDEdit.setMaxLength(4)
        self.messageIDEdit.setText("0")
        self.messageIDEdit.setMinimumWidth(100)
        self.gridLayout.addWidget(self.messageIDEdit, 0, 1, 1, 2)

        self.byte0Label = QtWidgets.QLabel(self.sendDatagramsWidget)
        self.byte0Label.setObjectName("byte0Label")
        self.gridLayout.addWidget(self.byte0Label, 0, 4, 1, 1)

        self.byte4Label = QtWidgets.QLabel(self.sendDatagramsWidget)
        self.byte4Label.setObjectName("byte4Label")
        self.gridLayout.addWidget(self.byte4Label, 1, 4, 1, 1)

        self.spinBoxDLC = QtWidgets.QSpinBox(self.sendDatagramsWidget)
        self.spinBoxDLC.setObjectName("spinBoxDLC")
        self.spinBoxDLC.setValue(8)
        self.spinBoxDLC.valueChanged.connect(self.chabgedNumberOfDLC)
        self.gridLayout.addWidget(self.spinBoxDLC, 1, 1, 1, 2)

        self.spinBoxDLC.setAlignment(QtCore.Qt.AlignCenter)

        self.byte3Edit = self.ByteEditLine(self.sendDatagramsWidget)
        self.byte3Edit.setObjectName("byte3Edit")
        self.gridLayout.addWidget(self.byte3Edit, 0, 15, 1, 1)

        self.byte1Edit = self.ByteEditLine(self.sendDatagramsWidget)
        self.byte1Edit.setObjectName("byte1Edit")
        self.gridLayout.addWidget(self.byte1Edit, 0, 7, 1, 1)

        self.byte4Edit = self.ByteEditLine(self.sendDatagramsWidget)
        self.byte4Edit.setObjectName("byte4Edit")
        self.gridLayout.addWidget(self.byte4Edit, 1, 5, 1, 1)

        self.rtrCheckBox = QtWidgets.QCheckBox(self.sendDatagramsWidget)
        self.rtrCheckBox.setObjectName("rtrCheckBox")
        self.gridLayout.addWidget(self.rtrCheckBox, 1, 16, 1, 1)

        self.dlcLabel = QtWidgets.QLabel(self.sendDatagramsWidget)
        self.dlcLabel.setObjectName("dlcLabel")
        self.gridLayout.addWidget(self.dlcLabel, 1, 0, 1, 1)
        self.dlcLabel.setText("DLC")

        self.byte5Edit = self.ByteEditLine(self.sendDatagramsWidget)
        self.byte5Edit.setObjectName("byte5Edit")
        self.gridLayout.addWidget(self.byte5Edit, 1, 7, 1, 1)

        self.byte6Edit = self.ByteEditLine(self.sendDatagramsWidget)
        self.byte6Edit.setObjectName("byte7Edit")
        self.gridLayout.addWidget(self.byte6Edit, 1, 13, 1, 1)

        self.byte5Label = QtWidgets.QLabel(self.sendDatagramsWidget)
        self.byte5Label.setObjectName("byte5Label")
        self.gridLayout.addWidget(self.byte5Label, 1, 6, 1, 1)

        self.byte1Label = QtWidgets.QLabel(self.sendDatagramsWidget)
        self.byte1Label.setObjectName("byte1Label")
        self.gridLayout.addWidget(self.byte1Label, 0, 6, 1, 1)

        self.byte6Label = QtWidgets.QLabel(self.sendDatagramsWidget)
        self.byte6Label.setObjectName("byte6Label")
        self.gridLayout.addWidget(self.byte6Label, 1, 8, 1, 1)

        self.byte2Label = QtWidgets.QLabel(self.sendDatagramsWidget)
        self.byte2Label.setObjectName("byte2Label")
        self.gridLayout.addWidget(self.byte2Label, 0, 8, 1, 1)

        self.byte2Edit = self.ByteEditLine(self.sendDatagramsWidget)
        self.byte2Edit.setObjectName("byte2Edit")
        self.gridLayout.addWidget(self.byte2Edit, 0, 13, 1, 1)

        self.byte0Edit = self.ByteEditLine(self.sendDatagramsWidget)
        self.byte0Edit.setObjectName("byte0Edit")
        self.gridLayout.addWidget(self.byte0Edit, 0, 5, 1, 1)

        self.byte7Edit = self.ByteEditLine(self.sendDatagramsWidget)
        self.byte7Edit.setObjectName("byte7Edit")
        self.gridLayout.addWidget(self.byte7Edit, 1, 15, 1, 1)

        self.extendedCheckBox = QtWidgets.QCheckBox(self.sendDatagramsWidget)
        self.extendedCheckBox.setObjectName("extendedCheckBox")
        self.gridLayout.addWidget(self.extendedCheckBox, 0, 16, 1, 1)
        self.extendedCheckBox.stateChanged.connect(self.updateMessageEditMode)

        self.byte3Label = QtWidgets.QLabel(self.sendDatagramsWidget)
        self.byte3Label.setObjectName("byte3Label")
        self.gridLayout.addWidget(self.byte3Label, 0, 14, 1, 1)

        self.byte7Label = QtWidgets.QLabel(self.sendDatagramsWidget)
        self.byte7Label.setObjectName("byte7Label")
        self.gridLayout.addWidget(self.byte7Label, 1, 14, 1, 1)

        self.horizontalLayout_2.addWidget(self.sendDatagramsWidget)

        self.senControlWidget = QtWidgets.QWidget(self)
        self.senControlWidget.setObjectName("senControlWidget")

        self.gridLayout_2 = QtWidgets.QGridLayout(self.senControlWidget)
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.periodEdit = QtWidgets.QLineEdit(self.senControlWidget)
        self.periodEdit.setObjectName("periodEdit")
        self.periodEdit.setMinimumWidth(75)
        self.periodEdit.setText("100")
        self.periodEdit.setValidator(QtGui.QIntValidator())
        self.periodEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.periodEdit.setEnabled(False)
        self.gridLayout_2.addWidget(self.periodEdit, 0, 1, 1, 1)

        self.repeatCheckBox = QtWidgets.QCheckBox(self.senControlWidget)
        self.repeatCheckBox.setObjectName("repeatCheckBox")
        self.gridLayout_2.addWidget(self.repeatCheckBox, 0, 0, 1, 1)
        self.periodEdit.setEnabled(False)

        self.msLabel = QtWidgets.QLabel(self.senControlWidget)
        self.msLabel.setObjectName("msLabel")
        self.msLabel.setEnabled(False)
        self.gridLayout_2.addWidget(self.msLabel, 0, 2, 1, 1)

        self.sendStartStopButton = QtWidgets.QPushButton(self.senControlWidget)
        self.sendStartStopButton.setObjectName("sendStartStopButton")
        self.sendStartStopButton.setIcon(GUIToolKit.getIconByName("send"))
        self.sendStartStopButton.clicked.connect(self.sendStartStopAction)
        self.gridLayout_2.addWidget(self.sendStartStopButton, 1, 0, 1, 3)

        self.horizontalLayout_2.addWidget(self.senControlWidget)

        self.byte0Label.setText("Byte 0")
        self.byte4Label.setText("Byte 4")
        self.byte3Label.setText("Byte 3")
        self.byte7Label.setText("Byte 7")
        self.rtrCheckBox.setText("RTR")
        self.byte5Label.setText("Byte 5")
        self.byte1Label.setText("Byte 1")
        self.byte6Label.setText("Byte 6")
        self.byte2Label.setText("Byte 2")

        self.extendedCheckBox.setText("Extended")

        self.repeatCheckBox.setText("Repeat")
        self.msLabel.setText("ms")
        self.sendStartStopButton.setText("Send")

        self.repeatCheckBox.stateChanged.connect(self.reapetChecked)

        self.sendLoopActive = False

        self.setTitle("Send datagrams")

        self.dataByteLineEditList = [
            self.byte0Edit, self.byte1Edit, self.byte2Edit, self.byte3Edit,
            self.byte4Edit, self.byte5Edit, self.byte6Edit, self.byte7Edit,
        ]
        self.dataByteLabelList = [
            self.byte0Label, self.byte1Label, self.byte2Label, self.byte3Label,
            self.byte4Label, self.byte5Label, self.byte6Label, self.byte7Label,
        ]
        font = QtGui.QGuiApplication.font()
        font.setCapitalization(QtGui.QFont.AllUppercase)
        hexValidator = QtGui.QRegExpValidator(QtCore.QRegExp("(?:[0-9a-fA-F]{2},)*[0-9a-fA-F]{0,2}"))

        for edit in self.dataByteLineEditList:
            edit.setValidator(hexValidator)
            edit.setFont(font)
            edit.setAlignment(QtCore.Qt.AlignCenter)

        self.repeatThread.senDatagramSignal.connect(self.sendDatagram)
        self.rtrCheckBox.clicked.connect(self.rtrAction)
        self.setEnabled(False)

    def chabgedNumberOfDLC(self):
        if not self.rtrCheckBox.isChecked():
            dlc = self.spinBoxDLC.value()
            if dlc > 8:
                self.spinBoxDLC.setValue(8)
                dlc = 8
            if dlc >= 0:
                for count in range(0,dlc):
                    self.dataByteLineEditList[count].setEnabled(True)
                    if len(self.dataByteLineEditList[count].text()) == 0:
                        self.dataByteLineEditList[count].setText("00")
                    self.dataByteLabelList[count].setEnabled(True)
                for count in range(dlc, 8):
                    self.dataByteLineEditList[count].setEnabled(False)
                    self.dataByteLineEditList[count].setText("")
                    self.dataByteLabelList[count].setEnabled(False)


    def rtrAction(self):
        if self.rtrCheckBox.isChecked():
            for label in self.dataByteLabelList:
                label.setEnabled(False)
            for edit in self.dataByteLineEditList:
                edit.setEnabled(False)
        else:
            self.chabgedNumberOfDLC()


    def updateMessageEditMode(self):
        if self.extendedCheckBox.isChecked():
            self.messageIDEdit.setMaxLength(9)
        else:
            self.messageIDEdit.setMaxLength(4)

    def reapetChecked(self):
        if self.repeatCheckBox.isChecked():
            self.periodEdit.setEnabled(True)
            self.msLabel.setEnabled(True)
            self.sendStartStopButton.setText("Start")
            self.sendStartStopButton.setIcon(GUIToolKit.getIconByName("start"))
        else:
            self.periodEdit.setEnabled(False)
            self.msLabel.setEnabled(False)
            self.sendStartStopButton.setText("Send")
            self.sendStartStopButton.setIcon(GUIToolKit.getIconByName("send"))

    def setDatagramEditionEnable(self, flag):
        for edit in self.dataByteLineEditList:
            edit.setEnabled(flag)
        for label in self.dataByteLabelList:
            label.setEnabled(flag)
        self.periodEdit.setEnabled(flag)
        self.messageIDEdit.setEnabled(flag)
        self.repeatCheckBox.setEnabled(flag)
        self.extendedCheckBox.setEnabled(flag)
        self.dlcLabel.setEnabled(flag)
        self.spinBoxDLC.setEnabled(flag)
        self.msLabel.setEnabled(flag)
        self.rtrCheckBox.setEnabled(flag)
        self.messageLabel.setEnabled(flag)

    def sendDatagram(self, datagram):
        self.snifferDevice.sendDatagram(datagram)

    def startSendingLoop(self):
        datagram = self.grabDatagram()
        period = int(self.periodEdit.text())
        self.repeatThread.datagramm = datagram
        self.repeatThread.period = period
        self.stopLoopSignal.connect(self.repeatThread.stopLoopAction)
        self.repeatThread.activeMode = True
        self.repeatThread.start()

    def stopSendingLoop(self):
        self.stopLoopSignal.emit()
        self.repeatThread.activeMode = False

    def grabDatagram(self):
        datagran = CANDatagram()
        datagran.messageID = self.messageIDEdit.text()
        datagran.dlc = self.spinBoxDLC.value()
        datagran.extended = self.extendedCheckBox.isChecked()
        datagran.rtr = self.rtrCheckBox.isChecked()
        if not datagran.rtr:
            datagran.data = bytearray()
            for cursor in range(datagran.dlc):
                datagran.data = datagran.data + bytearray.fromhex(self.dataByteLineEditList[cursor].text())
        else:
            datagran.data = None
        return datagran

    def sendStartStopAction(self):
        if self.repeatCheckBox.isChecked():
            if self.sendLoopActive is True:
                # Pause
                self.sendLoopActive = False
                self.sendStartStopButton.setText("Start")
                self.sendStartStopButton.setIcon(
                    GUIToolKit.getIconByName("start"))
                self.setDatagramEditionEnable(True)
                self.stopSendingLoop()
            else:
                # Start
                self.sendLoopActive = True
                self.sendStartStopButton.setText("Stop")
                self.sendStartStopButton.setIcon(
                    GUIToolKit.getIconByName("stop"))
                self.setDatagramEditionEnable(False)
                self.startSendingLoop()
        else:
            # Send a single datagram
            datagram = self.grabDatagram()
            self.sendDatagram(datagram)

    def deviceConnected(self, deviceConnected):
        if deviceConnected:
            self.setEnabled(True)
        else:
            self.setEnabled(False)
            self.stopSendingLoop()

    class ByteEditLine(QtWidgets.QLineEdit):
        def __init__(self, parent=None, sniffer=None):
            """Constructor for ToolsWidget"""
            super().__init__(parent)
            self.setText(("00"))

        def focusOutEvent(self, event):
            super().focusOutEvent(event)
            if len(self.text()) == 1:
                self.setText(("0"+self.text().upper()))
                return
            if len(self.text()) == 0:
                self.setText(("00"))


class CANMessengerDaemonSender(QtCore.QThread):

    senDatagramSignal = QtCore.pyqtSignal(CANDatagram)

    def __init__(self, datagramm=None , senController=None,period=1000):
        super().__init__()
        self.activeMode = False
        self.sender = senController
        self.period = period
        self.datagramm = datagramm

    def run(self):
        """Long-running task."""
        while self.activeMode:
            time.sleep(self.period / 1000)
            self.senDatagramSignal.emit(self.datagramm)

    def stopLoopAction(self):
        self.activeMode = False