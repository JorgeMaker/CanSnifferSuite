#!/usr/bin/env python
# -*- coding: utf-8 -*-
from threading import Thread
import math
import serial
from cobs import cobs
from serial import SerialException
import logging
import time
from src.gui.caninspector.canDatagram import CANDatagram
from src.gui.nautilusprotocol.nautilusdatagram import NautilusDatagram


class CLICanSnifferDevice(Thread):

    canBusBitRates = {'250.000': "250",
                      '1000.000': "1000",
                      '500.000': "500",
                      '125.000': "125",
                      '100.000': "100",
                      '50.000': "050",
                      '20.000': "020",
                      '10.000': "010",
                      }

    canBusModes = {'NORMAL': 'NM',
                   'LOOP BACK': 'LB',
                   'SILENT': 'SM',
                   'SILENT LOOP BACK': 'SL'
                   }

    def __init__(self, port, baud_rate):
        Thread.__init__(self)
        self.ser = serial.Serial(port,baud_rate)
        self.running = True

    def run(self):
        while self.running:
            if self.ser.in_waiting > 0:
                self.ser.flushInput()
                self.receiveDatagram()

    def startSniffing(self):
        time.sleep(0.1)
        commandValue = "A".encode() + 'ON_'.encode()
        valueToSend = cobs.encode(commandValue)
        self.ser.write(valueToSend + b'\00')
        self.start()

    def stop(self):
        self.running = False

    def stopSniffing(self):
        commandValue = "A".encode() + 'OFF'.encode()
        valueToSend = cobs.encode(commandValue)
        self.ser.write(valueToSend + b'\00')

    def __initCommunications(self):
        # ver como poner el bitrate
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

    def disconnectSerial(self):
        self.__closeCommunication()

    def __closeCommunication(self):
        if not self.ser.isOpen():
            self.ser.close()

    def rebootDevice(self):
        commandValue = "R".encode()
        valueToSend = cobs.encode(commandValue)
        self.ser.write(valueToSend + b'\00')

    def sendRawCommand(self, commandSrt):
        commandValue = commandSrt.encode()
        valueToSend = cobs.encode(commandValue)
        self.ser.write(valueToSend + b'\00')

    def sendBitrateCommand(self, bitrateCode):
        commandValue = "S".encode() + str(
            self.canBusBitRates[bitrateCode]).encode()
        valueToSend = cobs.encode(commandValue)
        self.ser.write(valueToSend + b'\00')

    def sendModeCommand(self, modeCode):
        commandValue = "N".encode() + str(self.canBusModes[modeCode]).encode()
        valueToSend = cobs.encode(commandValue)
        self.ser.write(valueToSend + b'\00')

    def connectSerial(self):
        try:
            self.__initCommunications()
        except SerialException as serEx:
            logging.warning('Is not possible to open serial port')

    def sendDatagram(self, datagran):
        valueToSend = cobs.encode('M'.encode() + datagran.serialize())
        self.ser.write(valueToSend + b'\00')

    def receiveDatagram(self):
        if self.ser.isOpen():
            packet = self.ser.read_until(b'\x00')
            if(len(packet)>4):
                decodedCOBS = cobs.decode(packet[:-1])
                datagram = CANDatagram.parseCANDatagram(decodedCOBS[:-1])
                self.printDatagran(datagram)

    def sendFilterCommand(self, bank, type, messageID):
        commandValue = "F".encode()
        if type in ("S", "E"):
            commandValue = commandValue + type.encode()
        else:
            raise Exception('Invalid type [{}] arguments only '
                            'E o S accepted'.format(type))
        if bank in range(13):
            commandValue = commandValue + str(bank).zfill(2).encode()
        else:
            raise Exception('Invalid bank [{}] argument only '
                            'between 0 and 13 is accepted'.format(type))
        if type == "S" and messageID <= 2 ** 11:
            commandValue = commandValue + str(messageID).zfill(4).encode()
        else:
            raise Exception('Invalid messageID {}] argument only '
                            'lower than 2^11 accepted'.format(messageID))
        if type == "E" and messageID <= 2 ** 29:
            commandValue = commandValue + str(messageID).zfill(9).encode()
        else:
            raise Exception('Invalid bank [{}] argument only '
                            'lower than 2^29 accepted'.format(messageID))
        valueToSend = cobs.encode(commandValue)
        self.ser.write(valueToSend + b'\00')

    def printDatagran(self,datagram):
        print(datagram)

def pintNautulusDatagram(datagram):
    nautilusDatagram = NautilusDatagram.paseCanNautilusDataGram(datagram)
    nautilusDatagram.printValues()
    #print(datagram)
