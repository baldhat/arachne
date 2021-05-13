from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *

from connection.observer import StateObserver
from widgets.angles import AnglesWidget
from widgets.legs import LegWidget
from widgets.stances import StancesWidget


class StatsWidget(QWidget, StateObserver):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.connector = self.parent.connector
        self.connector.registerState(self)
        self.movementService = parent.movementService

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.lightGray)
        self.setPalette(p)

        layout = QtWidgets.QVBoxLayout(self)

        self.title = QLabel()
        self.title.setText("Stats: ")
        self.titleFont = QFont()
        self.titleFont.setPointSize(15)
        self.title.setFont(self.titleFont)
        layout.addWidget(self.title)

        self.angles = AnglesWidget(self)
        layout.addWidget(self.angles)

        self.legs = LegWidget(self)
        layout.addWidget(self.legs)

        self.stances = StancesWidget(self)
        layout.addWidget(self.stances)

        layout.addStretch()
        self.setLayout(layout)

    def connectorCallback(self, values: [float]):
        self.angles.setState(values)