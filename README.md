<p align="center">
  <img  src="https://github.com/JorgeMaker/CanSnifferSuite/blob/main/docs/canbusdonglebanner.png?raw=true">
</p>


# CanSnifferSuite

Blue Pill CAN bus dongle is an USB to CAN Bus 2.0A/B adapter that acts as sniffer and traffic generator. This project is composed by three independent budling blocks that can be used   in combination or separately.

### Firmware: 
Is an application that runs on a STM32F103C8T6 and can be deployed on the [specifically designed PCB](https://github.com/JorgeMaker/CanSnifferSuite/tree/main/HardWare) for this project or on the popular and fairly affordable Blue Pill adding some extra HW also very cheap and easy to obtain and connect.

In this repository there are a couple of firmware. The first is for Blue Pill and is based on an interrupt driven layout design, the second in case that you prefer to use a STM32F40X family MCU uses the popular FreeRTOS for its implementation.

The [first implementation](https://github.com/JorgeMaker/CanSnifferSuite/tree/main/Firmware/BluePillCanSnniferEventDriven), the ISRs are responsible for receiving the basic elements of each of the two communication interfaces: the character and the datagram. Once received, they are stored in queues so that from the main function they are processed by applying a round robin algorithm.

<p align="center">
  <img  src="https://github.com/JorgeMaker/CanSnifferSuite/blob/main/docs/EventDrivenImplementation.jpg?raw=true">
</p>

The [second implementation](https://github.com/JorgeMaker/CanSnifferSuite/tree/main/Firmware/STM32F407VGT6CanSnniferFreeRTOS), tageted for STM32F40X uses FreeRTOS to acieve the desired funtionality. The characters and datagrams received by each communication interface are stored in a pair of queues that are managed by 4 tasks.

<p align="center">
  <img  src="https://github.com/JorgeMaker/CanSnifferSuite/blob/main/docs/FreeRTOSImplementation.jpg?raw=true">
</p>

Both solutions perform the same function and can be used interchangeably  with the GUI tool and Python library.

###  Hardware: 

To implement the [ HW part of the project](https://github.com/JorgeMaker/CanSnifferSuite/tree/main/HardWare), there are two possible alternatives with exactly the same functionality:

The first and the one the easiest reachable uses the popular very Blue Pill as MCU with an USB to TTL and a CAN bus transceiver. These three elements can be purchased online on shops like AliExpress, Banagood and others. Their combined cost does not exceed € 7, constituting a very affordable solution. There is an interconnection diagram available at the HW folder with [detailed instructions](https://github.com/JorgeMaker/CanSnifferSuite/blob/main/HardWare/InterconnectionsEasySolution.pdf).

The second alternative is to build custom PCB specific for this project to have a CAN bus dongle.  Geber files, and schematics are provided at the HW folder. 

<p align="center">
  <img  src="https://github.com/JorgeMaker/CanSnifferSuite/blob/main/docs/can_bus_dongle_picture.jpg?raw=true">
</p>

- Developed using the popular STM32F103C8T6
- Supports CAN2.0A and B, baud rates up to 500K
- 3 pins Hirose DF13 terminal: CANH, CANL, GND
- 120 Ohm termination via zero ohms resistor to enable/disable
- Tx an Rx LED indicators.
- GUI tool and Python library: 

###  GUI tool and Python lib: 

An application written in using PyQt/Python  has been developed. It allows communication with the Blue Pill CAN bus dongle to send commands and receive information on the traffic present on the CAN bus network acting as snnnifer and traffic generator.

<p align="center">
  <img  src="https://github.com/JorgeMaker/CanSnifferSuite/blob/main/docs/AnimatedScrenWideView.gif?raw=true">
</p>

The information on the traffic present on the network is parsed and sent to the application that displays it in two different formats. On the one hand, a table that lists each of the packets that have been received and, on the other, a table with the last packet received for each of the Id and the time elapsed between packets with the same ID.

It is also possible to use a Python library to write scripts that interacts with the CAN bus network as is shown in [this example](https://github.com/JorgeMaker/CanSnifferSuite/blob/main/GUIApplication/CanBusSnnifer/LibraryUsageDummyExample.py) 
