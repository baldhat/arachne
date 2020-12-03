from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
import sys

from qtpy import QtGui

from widgets.console import Console
from widgets.render import Renderer
from widgets.stats import StatsWidget


class Window(QtWidgets.QMainWindow):
    def __init__(self, connector):
        self.connector = connector
        self.app = QApplication(sys.argv)
        super().__init__()

        #### <GUI> ####
        self.setGeometry(100, 100, 3600, 2000)
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

        self.renderer = Renderer(self)
        grid_layout.addWidget(self.renderer, 1, 1)

        self.isAlive = True

        #### </GUI> ####

        self.show()

    def tick(self):
        if self.connector.has_connection():
            self.connector.checkForData()
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

