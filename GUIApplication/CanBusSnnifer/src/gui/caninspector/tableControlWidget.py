#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore
from src.gui.sharedcomponets import GUIToolKit


class TableControlWidget(QtWidgets.QGroupBox):
    def __init__(self, parent=None, tablesWidget= None):
        """Constructor for ToolsWidget"""
        super().__init__(parent)
        self.setObjectName("tableConrrolWidget")
        self.setTitle("Tables vizualization control")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.standardDataLabelImege = QtWidgets.QLabel(self)
        pixmap = GUIToolKit.getIconByName("greendot").pixmap((QtCore.QSize(16, 16)))
        self.standardDataLabelImege.setPixmap(pixmap)
        self.horizontalLayout.addWidget(self.standardDataLabelImege)

        self.standardDataLabel = QtWidgets.QLabel(self)
        self.standardDataLabel.setObjectName("standardDataLabel")
        self.standardDataLabel.setText("Standard data")
        self.horizontalLayout.addWidget(self.standardDataLabel)


        self.extndedDataLabelImege = QtWidgets.QLabel(self)
        pixmap = GUIToolKit.getIconByName("orangedot").pixmap((QtCore.QSize(16, 16)))
        self.extndedDataLabelImege.setPixmap(pixmap)
        self.horizontalLayout.addWidget(self.extndedDataLabelImege)

        self.extndedDataLabel = QtWidgets.QLabel(self)
        self.extndedDataLabel.setObjectName("standardDataLabel")
        self.extndedDataLabel.setText("Extended data")
        self.horizontalLayout.addWidget(self.extndedDataLabel)

        self.standardRTLabelImage = QtWidgets.QLabel(self)
        pixmap = GUIToolKit.getIconByName("bluedot").pixmap((QtCore.QSize(16, 16)))
        self.standardRTLabelImage.setPixmap(pixmap)
        self.horizontalLayout.addWidget(self.standardRTLabelImage)

        self.standardRTRLabel = QtWidgets.QLabel(self)
        self.standardRTRLabel.setObjectName("standardRTRCheckBox")
        self.standardRTRLabel.setText("Standard RTR")
        self.horizontalLayout.addWidget(self.standardRTRLabel)

        self.extendedRTRLabelImege = QtWidgets.QLabel(self)
        pixmap = GUIToolKit.getIconByName("reddot").pixmap((QtCore.QSize(16, 16)))
        self.extendedRTRLabelImege.setPixmap(pixmap)
        self.horizontalLayout.addWidget(self.extendedRTRLabelImege)

        self.extendedRTRLabel = QtWidgets.QLabel(self)
        self.extendedRTRLabel.setObjectName("standardRTRCheckBox")
        self.extendedRTRLabel.setText("Extended RTR")
        self.horizontalLayout.addWidget(self.extendedRTRLabel)

        spacerItem = QtWidgets.QSpacerItem(40, 20,
                                           QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.label = QtWidgets.QLabel(self)
        self.label.setObjectName("label")
        self.label.setText("Display mode")
        self.horizontalLayout.addWidget(self.label)

        self.displayModeComboBox = QtWidgets.QComboBox(self)
        self.displayModeComboBox.setObjectName("displayModeComboBox")
        self.displayModeComboBox.addItem("Hexadecimal")
        self.displayModeComboBox.addItem("ASCII")
        self.displayModeComboBox.addItem("Binary")
        self.displayModeComboBox.currentTextChanged.connect(
            self.displayModeAction)
        self.horizontalLayout.addWidget(self.displayModeComboBox)

        self.tablesWidget = tablesWidget

    def displayModeAction(self):
        selected = self.displayModeComboBox.currentText()
        if selected == "Hexadecimal":
            self.tablesWidget.monitorTab.monitorTableModel.displayFlag = "HEX"
            self.tablesWidget.traceTab.traceTableModel.displayFlag = "HEX"
            self.tablesWidget.traceTab.traceTableModel.updateAll()
            self.tablesWidget.monitorTab.monitorTableModel.updateAll()
            self.tablesWidget.traceTab.traceTable.update()
            return

        elif selected == "ASCII":
            self.tablesWidget.monitorTab.monitorTableModel.displayFlag = "ASCII"
            self.tablesWidget.traceTab.traceTableModel.displayFlag = "ASCII"
            self.tablesWidget.traceTab.traceTableModel.updateAll()
            self.tablesWidget.monitorTab.monitorTableModel.updateAll()

            return
        elif selected == "Binary":
            self.tablesWidget.monitorTab.monitorTableModel.displayFlag = "BINARY"
            self.tablesWidget.traceTab.traceTableModel.displayFlag = "BINARY"
            self.tablesWidget.traceTab.traceTableModel.updateAll()
            self.tablesWidget.monitorTab.monitorTableModel.updateAll()
