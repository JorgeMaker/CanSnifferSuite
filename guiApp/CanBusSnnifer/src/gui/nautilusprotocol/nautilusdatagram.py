#!/usr/bin/env python
# -*- coding: utf-8 -*-
import struct
from binascii import unhexlify
from bitarray import bitarray
from bitarray.util import (ba2int, int2ba)
from src.gui.caninspector.canDatagram import CANDatagram


class NautilusDatagram(CANDatagram):
    GET_VALUE = 0
    BOOLEAN = 1
    CHAR = 2
    INT = 3
    FLOAT = 4

    ENABLE = 1
    DISABLE = 0

    TARGET_CMD = 100
    PH_RESISTANCE_CMD = 200
    MOTOR_STATUS_CMD = 101
    PWM_MODULATION_CMD = 201
    MODULATION_CENTER_CMD = 202

    ZERO_ANGLE_OFFSET_CMD = 203
    ELECTRICAL_OFFSET_CMD = 204
    SENSOR_ZERO_CMD = 102

    STATES_REPORT_CONFIG_CMD = 500
    TARGET_STATE = 501
    VOLTAGE_Q_STATE = 502
    VOLTAGE_D_STATE = 503
    CURRENT_Q_STATE = 504
    CURRENT_D_STATE = 505
    VELOCITY_STATE = 506
    ANGLE_STATE = 507

    VELOCITY_LIMIT_CMD = 206
    VOLTAGE_LIMIT_CMD = 207
    CURRENT_LIMIT_CMD = 208

    MOTOR_CONTROL_TYPE_CMD = 210
    TORQUE_CONTROL_TYPE_CMD = 211
    MOTION_DOWN_SAMPLE_CMD = 212

    VEL_PID_P_GAIN_CMD = 230
    VEL_PID_I_GAIN_CMD = 231
    VEL_PID_D_GAIN_CMD = 232
    VEL_PID_OUT_RAMP_CMD = 233
    VEL_PID_OUT_LIMIT_CMD = 234
    VEL_PID_LPF_CMD = 235

    ANGLE_PID_P_GAIN_CMD = 330
    ANGLE_PID_I_GAIN_CMD = 331
    ANGLE_PID_D_GAIN_CMD = 332
    ANGLE_PID_OUT_RAMP_CMD = 333
    ANGLE_PID_OUT_LIMIT_CMD = 334
    ANGLE_PID_LPF_CMD = 335

    CURRENT_D_PID_P_GAIN_CMD = 430
    CURRENT_D_PID_I_GAIN_CMD = 431
    CURRENT_D_PID_D_GAIN_CMD = 432
    CURRENT_D_PID_OUT_RAMP_CMD = 433
    CURRENT_D_PID_OUT_LIMIT_CMD = 434
    CURRENT_D_PID_LPF_CMD = 435

    CURRENT_Q_PID_P_GAIN_CMD = 530
    CURRENT_Q_PID_I_GAIN_CMD = 531
    CURRENT_QD_PID_D_GAIN_CMD = 532
    CURRENT_Q_PID_OUT_RAMP_CMD = 533
    CURRENT_Q_PID_OUT_LIMIT_CMD = 534
    CURRENT_Q_PID_LPF_CMD = 535

    def __init__(self, commandID=None, dataType=None, entity=None,
                 multicast=None, nodeID=None, textValue=None):
        super(NautilusDatagram, self).__init__(textValue=textValue)
        self.encodedMessageID = 32 * bitarray('0')

        self.nodeID = nodeID
        self.setNodeID(nodeID)
        self.commandID = commandID
        self.setCommandCode(commandID)
        self.entity = entity
        self.setEntity(entity)
        self.dataType = dataType
        self.setDataType(dataType)
        self.multicast = multicast
        self.setmulticast(multicast)

        self.data = None

        self.messageID = ba2int(self.encodedMessageID)
        self.extended = True

    @staticmethod
    def paseCanNautilusDataGram(datagram):

        messageID = datagram.messageID

        commandID = (messageID & ((0x1FF) << 20)) >> 20
        dataType = (messageID & ((0x3F) << 14)) >> 14
        entity = (messageID & ((0xF) << 10)) >> 10
        multicast = (messageID & (0x1 << 9)) >> 9
        nodeID = (messageID & 0x1FF)

        nautilusDatagram = NautilusDatagram(commandID, dataType, entity,
                                            multicast, nodeID)

        nautilusDatagram.data = datagram.data

        return nautilusDatagram

    def getFloatData(self):
        return struct.unpack('f', self.data)[0]

    def getIntData(self):
        return int.from_bytes(self.data, byteorder='little')

    def getCharData(self):
        pass

    def getBoolData(self):
        pass

    def printValues(self):
        print(
            'commandID ={} dataType={} entity={} multicast={} nodeID={} data={}'.format(
                self.commandID, self.dataType, self.entity, self.multicast,
                self.nodeID, self.getFloatData()))

    def setNodeID(self, nodeID):
        if nodeID is not None:
            if nodeID < 0 or nodeID >= 512:
                raise ValueError('NodeId has to be bigger than 0 '
                                 'and smaller than 512')
            self.encodedMessageID[23:32] = int2ba(nodeID, 9)

    def setCommandCode(self, cmdCodeID):
        if cmdCodeID is not None:
            if cmdCodeID < 0 or cmdCodeID >= 512:
                raise ValueError('Command ID has to be bigger than 0 '
                                 'and smaller than 512')
            self.encodedMessageID[3:12] = int2ba(cmdCodeID, 9)

    def setDataType(self, dataType):
        if dataType is not None:
            if dataType < 0 or dataType > 64:
                raise ValueError('Data Type ID has to be bigger than 0 '
                                 'and smaller than 64')
            self.encodedMessageID[12:18] = int2ba(dataType, 6)

    def setEntity(self, entity):
        if entity is not None:
            if entity < 0 or entity > 16:
                raise ValueError('Entity ID has to be bigger than 0 '
                                 'and smaller than 16')
            self.encodedMessageID[18:22] = int2ba(entity, 4)

    def setmulticast(self, multicast):
        if multicast is not None:
            if multicast < 0 or multicast > 1:
                raise ValueError('Multicast has to be  0 '
                                 'or 1')
            self.encodedMessageID[22:23] = int2ba(multicast, 1)

    def setGetData(self):
        self.dataType = int2ba(NautilusDatagram.GET_VALUE, 6)
        self.dlc = 0
        self.rtr = True

    def setBooleanData(self, value):
        if value == True:
            self.data = b'\01'
        else:
            self.data = b'\00'
        self.setDataType(NautilusDatagram.BOOLEAN)
        self.dlc = 1
        self.rtr = False

    def setCharData(self, value):
        self.data = value.encode()
        self.setDataType(NautilusDatagram.CHAR)
        self.dlc = 1
        self.rtr = False

    def setIntData(self, value):
        self.data = value.to_bytes(4, 'big')
        self.setDataType(NautilusDatagram.INT)
        self.dlc = 4
        self.rtr = False
        self.messageID = ba2int(self.encodedMessageID)

    def setFloatData(self, value):
        self.data = self.__float_to_hex(value)
        self.setDataType(NautilusDatagram.FLOAT)
        self.dlc = 4
        self.rtr = False
        self.messageID = ba2int(self.encodedMessageID)

    def __float_to_hex(self, f):
        obtained = hex(struct.unpack('<I', struct.pack('<f', f))[0])
        if obtained == '0x0':
            return b'0x0'
        else:
            value = unhexlify(obtained[2:])
            return value
