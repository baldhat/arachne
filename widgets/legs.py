from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import *
from functools import partial


class LegWidget(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.connector = parent.connector

        self.leg_buttons = []
        self.layout = QVBoxLayout()
        self.legs = [QHBoxLayout() for _ in range(4)]
        self.texts = []
        for i, cell_layout in enumerate(self.legs):
            label = QLabel()
            label.setText("Leg " + str(i))
            cell_layout.addWidget(label)

            text_x = QLineEdit()
            text_y = QLineEdit()
            text_z = QLineEdit()

            self.texts.append(text_x)
            self.texts.append(text_y)
            self.texts.append(text_z)

            cell_layout.addWidget(text_x)
            cell_layout.addWidget(text_y)
            cell_layout.addWidget(text_z)

            leg_button = QPushButton()

            leg_button.clicked.connect(partial(self.compute_angles, i))
            leg_button.setText("Compute Angles")
            self.leg_buttons.append(leg_button)
            cell_layout.addWidget(leg_button)

            self.layout.addLayout(cell_layout, i)
        self.setLayout(self.layout)

    def compute_angles(self, i):
        x, y, z = float(self.texts[0 + i * 3].text()), \
                  float(self.texts[1 + i * 3].text()), \
                  float(self.texts[2 + i * 3].text())
        self.connector.write_leg_coords((x, y, z), i)

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and source in self.texts:
            if event.key() == 16777220:
                print("Enter in LegWidget")
                # i = self.texts.index(source)
                # self.connector.writeCommand(chr(97 + i) + str(self.texts[i].text()))
        return super(LegWidget, self).eventFilter(source, event)

    def setState(self, state: [float]):
        for i, s in enumerate(state):
            self.texts[i].setText(str(s))