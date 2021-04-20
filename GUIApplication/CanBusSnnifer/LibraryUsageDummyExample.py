from src.gui.caninspector.canDatagram import CANDatagram
from src.gui.caninspector.canSnifferDevice import CanSnifferDevice
import time
if __name__ == '__main__':
    portName = "/dev/tty.usbserial-14140"

    datagram1 = CANDatagram()
    datagram1.dlc = 2
    datagram1.messageID = 1111
    datagram1.rtr = False
    datagram1.extended = False
    datagram1.data = b'\01\02'

    snniffer =CanSnifferDevice(portName)
    snniffer.connectSerial()
    snniffer.rebootDevice()

    while True:
        snniffer.sendDatagram(datagram1)
        time.sleep(1/1000)
