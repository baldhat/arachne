from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import *


class AnglesWidget(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.connector = parent.connector

        self.layout = QGridLayout()
        self.angles = [QHBoxLayout() for i in range(12)]
        self.texts = []
        for i, cell_layout in enumerate(self.angles):
            label = QLabel()
            label.setText(chr(97 + i))
            cell_layout.addWidget(label)
            text = QLineEdit()
            text.installEventFilter(self)
            text.setText("0")
            self.texts.append(text)
            cell_layout.addWidget(text)
            self.layout.addLayout(cell_layout,  int(i / 4), i % 4)
        self.setLayout(self.layout)

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and source in self.texts:
            if event.key() == 16777220:
                i = self.texts.index(source)
                self.connector.writeCommand(chr(97 + i) + str(self.texts[i].text()))
        return super(AnglesWidget, self).eventFilter(source, event)

    def setState(self, state: [float]):
        for i, s in enumerate(state):
            self.texts[i].setText(str(s))