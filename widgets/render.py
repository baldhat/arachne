
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from matplotlib.backends.qt_compat import QtWidgets, is_pyqt5
from matplotlib.figure import Figure
import matplotlib
import numpy as np

import warnings
import matplotlib.cbook
from connection.observer import StateObserver
from kinematics import Kinematics

warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)

if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import FigureCanvas


class Renderer(QWidget, StateObserver):
    def __init__(self, parent):
        super().__init__()

        self.kinematics = Kinematics()
        self.connector = parent.connector
        self.connector.registerState(self)

        layout = QtWidgets.QVBoxLayout(self)

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.darkGray)
        self.setPalette(p)

        self.dynamic_canvas = FigureCanvas(Figure())
        self.dynamic_canvas.figure.patch.set_facecolor('#7d7e80')
        matplotlib.rc('lines', linewidth=4, color='r')

        layout.addWidget(self.dynamic_canvas)

        self.ax = self.dynamic_canvas.figure.add_subplot(111, projection='3d')

    def _update_canvas(self):
        self.update()
        self.ax.figure.canvas.draw()

    def connectorCallback(self, values: [float]):
        points = self.kinematics.forward(values)

        self.ax.clear()

        axis = np.array(points).T
        xs = axis[0]
        ys = axis[1]
        zs = axis[2]

        self.ax.scatter(xs, ys, zs, color='b')

        self.ax.plot(xs[0:5], ys[0:5], zs[0:5], color='r')  # Leg 1
        self.ax.plot([xs[5], xs[0], xs[9]],  # Connect Leg 2 and 3 to base
                     [ys[5], ys[0], ys[9]],
                     [zs[5], zs[0], zs[9]], color='r')
        self.ax.plot([xs[13], xs[0]],  # Connect Leg 4 to base
                     [ys[13], ys[0]],
                     [zs[13], zs[0]], color='r')
        self.ax.plot(xs[5:9], ys[5:9], zs[5:9], color='r')  # Leg 2
        self.ax.plot(xs[9:13], ys[9:13], zs[9:13], color='r')  # Leg 3
        self.ax.plot(xs[13:17], ys[13:17], zs[13:17], color='r')  # Leg 4

        self.ax.set_position([0, 0, 1, 1])
        self.ax.set_facecolor("#7d7e80")
        self.ax.dist = 5
        self.ax._axis3don = False

        self.ax.set_ylim(-4, 4)
        self.ax.set_xlim(-4, 4)
        self.ax.set_zlim(-4, 4)
        self.ax.set_facecolor((0.3, 0.3, 0.3))