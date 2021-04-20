#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This module contains ans script to start the SimpleFOC ConfigTool, a GIU
    application ta monitor, tune and configure BLDC motor controllers based on
    SimpleFOC library.
"""

import logging
import sys
from PyQt5 import QtWidgets

from src.gui.mainWindow import UserInteractionMainWindow

if __name__ == "__main__":

    # logging.basicConfig(filename='NauthilusCanBusSnnifer.log', filemode='w',
    #                     format='%(name)s - %(levelname)s - %(message)s')
    # try:
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    userInteractionMainWindow = UserInteractionMainWindow()
    userInteractionMainWindow.setupUi(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())
    # except Exception as exception:
    #     logging.error(exception, exc_info=True)
