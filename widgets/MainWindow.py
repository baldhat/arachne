from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
import sys
from connection.connector import Connector

from qtpy import QtGui

from movement_service import MovementService
from widgets.console import Console
from widgets.render import Renderer
from widgets.stats import StatsWidget


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        self.app = QApplication(sys.argv)
        super().__init__()
        self.connector = Connector(self, 'COM8', 115200)
        self.renderer = Renderer(self)
        self.movementService = MovementService(self.connector)

        self.isAlive = True

        #### <GUI> ####
        self.setGeometry(-1920, 60, 1920, 1020)
        self.setWindowTitle('ARACHNE')

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.darkGray)
        self.setPalette(p)

        self.setCentralWidget(QWidget())

        grid_layout = QGridLayout()
        grid_layout.setColumnStretch(0, 2)
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setRowStretch(0, 1)
        grid_layout.setRowStretch(1, 1)
        self.centralWidget().setLayout(grid_layout)

        self.consoleInput = Console(self)
        grid_layout.addWidget(self.consoleInput, 0, 0, 2, 1)

        self.stats = StatsWidget(self)
        grid_layout.addWidget(self.stats, 0, 1)

        grid_layout.addWidget(self.renderer, 1, 1)

        self.show()

    def tick(self):
        while self.isAlive:
            if self.connector.has_connection():
                self.connector.checkForData()
            # if self.movementService.hasMove():
            #     self.movementService.nextMove()
            self.update()
            self.app.processEvents()

    def single_tick(self):
        if self.connector.has_connection():
            while self.connector.checkForData():
                pass
        self.update()
        self.app.processEvents()

    def update(self) -> None:
        super().update()
        self.renderer._update_canvas()
        if self.connector.has_connection():
            pass

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.isAlive = False
        self.app.quit()
        super().closeEvent(a0)

