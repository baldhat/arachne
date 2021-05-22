from functools import partial
from PyQt5.QtWidgets import *
import time
from PyQt5.QtCore import Qt


class StancesWidget(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.connector = parent.connector
        self.movementService = parent.movementService

        self.mass_x = 0
        self.mass_y = 0
        self.mass_z = 50

        self.vertical = QVBoxLayout()
        self.stances = QHBoxLayout()
        self.walking = QHBoxLayout()

        neutral_button = QPushButton()
        neutral_button.clicked.connect(partial(self.set_neutral))
        neutral_button.setText("Neutral")
        self.stances.addWidget(neutral_button)

        high_button = QPushButton()
        high_button.clicked.connect(partial(self.set_high))
        high_button.setText("High")
        self.stances.addWidget(high_button)

        sit_button = QPushButton()
        sit_button.clicked.connect(partial(self.sit))
        sit_button.setText("Sit")
        self.stances.addWidget(sit_button)

        jump_button = QPushButton()
        jump_button.clicked.connect(partial(self.jump))
        jump_button.setText("Jump")
        self.stances.addWidget(jump_button)

        forward_button = QPushButton()
        forward_button.clicked.connect(partial(self.forward))
        forward_button.setText("Forward")
        self.walking.addWidget(forward_button)

        backward_button = QPushButton()
        backward_button.clicked.connect(partial(self.stop))
        backward_button.setText("STOP")
        self.walking.addWidget(backward_button)

        left_button = QPushButton()
        left_button.clicked.connect(partial(self.forward))
        left_button.setText("Left")
        self.walking.addWidget(left_button)

        right_button = QPushButton()
        right_button.clicked.connect(partial(self.forward))
        right_button.setText("Right")
        self.walking.addWidget(right_button)

        self.vertical.addLayout(self.stances)
        self.vertical.addLayout(self.walking)

        self.x_slider = QSlider(Qt.Horizontal)
        self.x_slider.setFocusPolicy(Qt.StrongFocus)
        self.x_slider.setTickPosition(QSlider.TicksBothSides)
        self.x_slider.setSingleStep(1)
        self.x_slider.setMaximum(150)
        self.x_slider.setMinimum(-150)
        self.x_slider.setValue(self.mass_x)
        self.x_slider.sliderMoved.connect(partial(self.shift_point_of_mass))
        self.vertical.addWidget(self.x_slider)

        self.y_slider = QSlider(Qt.Horizontal)
        self.y_slider.setFocusPolicy(Qt.StrongFocus)
        self.y_slider.setTickPosition(QSlider.TicksBothSides)
        self.y_slider.setSingleStep(1)
        self.y_slider.setMaximum(150)
        self.y_slider.setMinimum(-150)
        self.y_slider.setValue(self.mass_y)
        self.y_slider.sliderMoved.connect(partial(self.shift_point_of_mass))
        self.vertical.addWidget(self.y_slider)

        self.z_slider = QSlider(Qt.Horizontal)
        self.z_slider.setFocusPolicy(Qt.StrongFocus)
        self.z_slider.setTickPosition(QSlider.TicksBothSides)
        self.z_slider.setSingleStep(1)
        self.z_slider.setMaximum(300)
        self.z_slider.setMinimum(50)
        self.z_slider.setValue(self.mass_z)
        self.z_slider.sliderMoved.connect(partial(self.shift_point_of_mass))
        self.vertical.addWidget(self.z_slider)

        self.setLayout(self.vertical)

    def set_neutral(self):
        self.connector.writeInterpolatedMotion([0.5, 0.5, 0.5, 0.5, 0.8, 0.8, 0.8, 0.8, 0.03, 0.03, 0.03, 0.03])

    def set_high(self):
        self.connector.writeInterpolatedMotion([0.5, 0.5, 0.5, 0.5, 0.2, 0.2, 0.2, 0.2, 0.5, 0.5, 0.5, 0.5])

    def sit(self):
        self.connector.writeInterpolatedMotion([0.5, 0.5,0.5, 0.5, 1.0, 1.0, 1.0, 1.0, 0.05, 0.04, 0.03, 0.02])

    def jump(self):
        self.connector.write_coords([[0, 2, -1], [-2, 0, -1], [0, -2, -1], [2, 0, -1]], interpolate=True)
        time.sleep(1)
        self.connector.write_coords([[0, 2, -3], [-2, 0, -3], [0, -2, -3], [2, 0, -3]])

    def forward(self):
        self.movementService.forward()
        # self.movementService.nextMove()

    def stop(self):
        self.movementService.stop()

    def shift_point_of_mass(self, event):
        x = self.x_slider.value() * 0.01
        y = self.y_slider.value() * 0.01
        z = self.z_slider.value() * 0.01
        self.connector.shift_point_of_mass(x, y, z)


