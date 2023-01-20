#!/usr/bin/env python
# -*- coding: utf-8 -*-
import struct

class CANDatagram:
    def __init__(self, textValue=None):
        self.textValue = textValue
        self.data = None
        self.messageID = None
        self.extended = False
        self.rtr = False
        self.data = None
        self.dlc = 0

    @staticmethod
    def parseCANDatagram(serialezedDatagram):
        datagram = CANDatagram()
        datagram.textValue = serialezedDatagram
        index = 0
        if serialezedDatagram is not None:
            if serialezedDatagram[:1].decode().isupper():
                datagram.extended = True
                # is Extended
                if serialezedDatagram[:1].decode() == 'T':
                    datagram.rtr = False
                    index += 1
                    datagram.messageID = int(serialezedDatagram[index:index+9].decode())
                    index += 9
                    datagram.dlc = int(serialezedDatagram[index:index+1].decode())
                    index += 1

                    datagram.data = serialezedDatagram[index:index+datagram.dlc]

                elif serialezedDatagram[:1].decode() == 'R':
                    datagram.rtr = True
                    index += 1
                    datagram.messageID = int(serialezedDatagram[index:index + 9].decode())
                    index += 9
                    datagram.dlc = int(serialezedDatagram[index:index + 1].decode())
            else:
                # is Standard
                if serialezedDatagram[:1].decode() == 't':
                    datagram.rtr = False
                    index += 1
                    datagram.messageID = int(serialezedDatagram[index:index+4].decode())
                    index += 4
                    datagram.dlc = int(serialezedDatagram[index:index+1].decode())
                    index += 1

                    datagram.data = serialezedDatagram[index:index+datagram.dlc]

                elif serialezedDatagram[:1].decode() == 'r':
                    datagram.rtr = True
                    index += 1
                    datagram.messageID = int(serialezedDatagram[index:index + 4].decode())
                    index += 4
                    datagram.dlc = int(serialezedDatagram[index:index + 1].decode())
        return datagram

    def __repr__(self):
        toStringValue = ''
        if self.extended:
            if self.rtr:
                toStringValue = toStringValue + "R"
            else:
                toStringValue = toStringValue + "T"
            toStringValue = toStringValue+ str(self.messageID).zfill(9)
            toStringValue = toStringValue + str(self.dlc)
            if self.data is not None:
                toStringValue = toStringValue + self.dataToString()

        else:
            if self.rtr:
                toStringValue = toStringValue + "r"
            else:
                toStringValue = toStringValue + "t"
            toStringValue = toStringValue + str(self.messageID).zfill(4)
            toStringValue = toStringValue + str(self.dlc)
            if self.data is not None:
                toStringValue = toStringValue + self.dataToString()

        return toStringValue

    def dataToString(self, displayFlag="HEX"):
        if displayFlag == "HEX":
            stringRepresentation = ""
            listOfBytes = list(self.data)
            for byte in listOfBytes:
                convertedValue = str(hex(byte)[2:]).upper()
                if len(convertedValue) < 2:
                    convertedValue = '0' + convertedValue
                stringRepresentation = stringRepresentation + "  " + convertedValue
            return stringRepresentation

        elif displayFlag == "ASCII":
            stringRepresentation = ""
            for cursor in range(0, len(self.data)+1):
                try:
                    stringRepresentation = stringRepresentation + self.data[cursor:cursor+1].decode()
                except UnicodeDecodeError as error:
                    stringRepresentation = stringRepresentation + " .. "
            return stringRepresentation

        elif displayFlag == "BINARY":
            stringRepresentation = ""
            listOfBytes = list(self.data)
            for byte in listOfBytes:
                byeString = str(bin(byte)[2:])
                while(len(byeString)<8):
                    byeString = '0'+ byeString
                stringRepresentation = stringRepresentation + "  " + byeString
            return stringRepresentation

        elif displayFlag == "DEC":
            stringRepresentation = str(int.from_bytes(self.data, byteorder="little"))
            return stringRepresentation
        elif displayFlag == "FLOAT":
            if len(self.data) is 4:
                unpacked = struct.unpack('f', self.data)
                stringRepresentation = str(round(unpacked[0], 4))
                return stringRepresentation
            else:
                return "-Is not a Float-"
    def getDatagramTypeCode(self):
        if self.extended:
            if self.rtr:
                return 'R'
            else:
                return 'T'
        else:
            if self.rtr:
                return 'r'
            else:
                return 't'

    def serialize(self):
        serializedvalue = bytearray()
        if self.rtr:
            if self.extended:
                serializedvalue = serializedvalue + 'R'.encode()
                serializedvalue = serializedvalue + self.getSerializedID()
            else:
                serializedvalue = serializedvalue + 'r'.encode()
                serializedvalue = serializedvalue + self.getSerializedID()

            serializedvalue = serializedvalue+ str(self.dlc).encode()

        else:
            if self.extended:
                serializedvalue = serializedvalue + 'T'.encode()
                serializedvalue = serializedvalue + self.getSerializedID()
            else:
                serializedvalue = serializedvalue + 't'.encode()
                serializedvalue = serializedvalue + self.getSerializedID()
            serializedvalue = serializedvalue + str(self.dlc).encode()
            if self.data != None:
                serializedvalue = serializedvalue + self.data

        return serializedvalue

    def getSerializedID(self):
        if self.extended:
            return str(self.messageID).zfill(9).encode()
        else:
            return str(self.messageID).zfill(4).encode()
