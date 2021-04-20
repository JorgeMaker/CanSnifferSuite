import logging
import threading

import serial
from PyQt5 import QtCore, QtWidgets
from cobs import cobs
from serial import SerialException
import logging

from src.gui.caninspector.canDatagram import CANDatagram


class CanSnifferDevice(QtCore.QThread):
    canBusBitRates = {'250.000': "12",
                      '500.000': "500",
                      '125.000': "125",
                      '100.000': "100",
                      '50.000': "050",
                      '20.000': "020",
                      '10.000': "010",
                      }
    canBusModes = {'NORMAL': 'NM',
                   'LOOP BACK':'LB',
                   'SILENT': 'SM',
                   'SILENT LOOP BACK': 'SL'
                   }

    datagramReceived = QtCore.pyqtSignal(CANDatagram)

    def __init__(self, serialPortName=None, *args, **kwargs):

        super(CanSnifferDevice, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()
        self.serialPortName = serialPortName
        self.bitrate = 500000
        self.serialPort = None
        self.isSnifing = False
        self.isConnected = False
        self.connectionStateListenerList = []

    def handle_received_data(self, data):
        try:
            datagram = CANDatagram.parseCANDatagram(data[:-1])
            self.datagramReceived.emit(datagram)
        except Exception as error:
            logging.error(error, exc_info=True)
            logging.error("data =" + str(data), exc_info=True)

    def run(self):
        while self.isSnifing:
            if self.isConnected:
                if self.serialPort is not None:
                    if self.serialPort.isOpen():
                        packet = self.serialPort.read_until(b'\x00')
                        try:
                            decodedCOBS = cobs.decode(packet[:-1])
                            self.handle_received_data(decodedCOBS)
                        except UnicodeDecodeError as error:
                            logging.exception(error)
                        except cobs.DecodeError as error:
                            logging.exception(error)

    def stop(self):
        self._stop_event.set()

    def startSniffing(self):
        self.isSnifing = True
        commandValue = "A".encode() + 'ON_'.encode()
        valueToSend = cobs.encode(commandValue)
        self.serialPort.write(valueToSend + b'\00')
        self.start()

    def stopSniffing(self):
        commandValue = "A".encode() + 'OFF'.encode()
        valueToSend = cobs.encode(commandValue)
        self.serialPort.write(valueToSend + b'\00')
        self.isSnifing = False

    def __initCommunications(self):
        self.serialPort = serial.Serial(self.serialPortName, self.bitrate)
        self.serialPort.reset_input_buffer()
        self.serialPort.reset_output_buffer()
        self.isConnected = True

    def __closeCommunication(self):
        # self.responseThread.stop()
        if not self.serialPort.isOpen():
            self.serialPort.close()

    def connectSerial(self):
        try:
            self.__initCommunications()
            self.isConnected = True
        except SerialException as serEx:
            logging.warning('Is not possible to open serial port')
            logging.warning('Port =' + self.serialPortName)
            msgBox = QtWidgets.QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Warning)
            msgBox.setText("Error while trying to open serial port")
            msgBox.setWindowTitle("CAN Inspector Tool")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msgBox.exec()
            return False
        else:
            self.isConnected = True
            for listener in self.connectionStateListenerList:
                listener.deviceConnected(True)
            return True

    def disconnectSerial(self):
        self.__closeCommunication()
        self.isConnected = False
        for listener in self.connectionStateListenerList:
            listener.deviceConnected(False)

    def addConnectionStateListener(self, listener):
        self.connectionStateListenerList.append(listener)

    def sendDatagram(self, datagran):
        valueToSend = cobs.encode('M'.encode() + datagran.serialize())
        self.serialPort.write(valueToSend + b'\00')

    def sendBitrateCommand(self, bitrateCode):
        commandValue = "S".encode() + str(self.canBusBitRates[bitrateCode]).encode()
        valueToSend = cobs.encode(commandValue)
        self.serialPort.write(valueToSend + b'\00')

    def sendModeCommand(self, modeCode):
        commandValue = "N".encode() + str(self.canBusModes[modeCode]).encode()
        valueToSend = cobs.encode(commandValue)
        self.serialPort.write(valueToSend + b'\00')

    def rebootDevice(self):
        commandValue = "R".encode()
        valueToSend = cobs.encode(commandValue)
        self.serialPort.write(valueToSend + b'\00')
