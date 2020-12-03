from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import *

from connection.connector import Connector
from connection.observer import TextObserver


class Console(QWidget, TextObserver):
    def __init__(self, parent):
        super().__init__(parent)

        self.connector: Connector = parent.connector
        self.connector.registerText(self)

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.lightGray)
        self.setPalette(p)

        inputLayout = QHBoxLayout()

        layout = QtWidgets.QVBoxLayout(self)

        self.input = QLineEdit(self)
        inputLayout.addWidget(self.input)
        self.consoleButton = QPushButton(self)
        self.consoleButton.setText("Enter")
        self.consoleButton.clicked.connect(
            lambda: self.issueCommand(self.input.text())
        )
        inputLayout.addWidget(self.consoleButton)
        layout.addLayout(inputLayout)

        self.output = QPlainTextEdit()
        layout.addWidget(self.output)

        self.setLayout(layout)

        self.input.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and source is self.input:
            if event.key() == 16777220:
                self.issueCommand(self.input.text())
                self.input.clear()
        return super(Console, self).eventFilter(source, event)

    def connectorCallback(self, text: str):
        self.output.appendPlainText(text)

    def issueCommand(self, cmd: str):
        if self.connector.has_connection():
            self.connector.writeCommand(cmd)
