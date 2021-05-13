import multiprocessing
import serial
import time

from connection.observer import StateObserver, TextObserver, LegStateObserver
from kinematics import Kinematics


class Connector():

    def __init__(self, parent, com_port, baud_rate, max_tries=10):
        self.connected = False
        self.parent = parent
        self.kinematics = Kinematics()
        self.comport = com_port
        self.baud_rate = baud_rate
        self.ser = self.connect(com_port, baud_rate, max_tries)
        if self.ser is None:
            p = multiprocessing.Process(target=self.retryConnect)
            p.start()

        self.stateObservers: [StateObserver] = []
        self.textObservers: [TextObserver] = []
        self.legStateObservers: [LegStateObserver] = []

        self.requestState()

    def connect(self, comport, baudrate, max_tries):
        try:
            ser = serial.Serial(comport, baudrate)
        except:
            return None

        ser.write(b'5173')
        x = ''
        counter = 0
        while '5173' not in x:
            if counter >= max_tries:
                print("Error: Maximum tries to establish connection exceeded")
                return None
            if ser.inWaiting() > 0:
                x = ser.readline().decode('utf-8')
            time.sleep(0.1)
            counter += 1

        print("Connection established")
        self.connected = True
        return ser

    def retryConnect(self):
        while self.ser is None:
            time.sleep(5)
            self.ser = self.connect(self.comport, self.baud_rate, 10)
            self.requestState()

    def writeInterpolatedMotion(self, jointValues, duration=1000):
        if self.has_connection():
            valueStrings = [str(value) for value in jointValues]
            valueString = 'r' + ';'.join(valueStrings) + ';' + str(duration)
            self.ser.write(valueString.encode('utf-8'))

    def writeAngles(self, jointValues):
        if self.has_connection():
            valueStrings = [str(value) for value in jointValues]
            valueString = 'x' + ';'.join(valueStrings) + ";100"
            self.ser.write(valueString.encode('utf-8'))

    def shift_point_of_mass(self, x, y, z, duration=300):
        self.writeAngles(self.kinematics.shift_point_of_mass(x, y, z))

    def writeCommand(self, cmd: str):
        if self.has_connection():
            self.ser.write(cmd.encode('utf-8'))

    def write_coords(self, coords: tuple, interpolate=False, duration=None):
        angles = self.kinematics.inverse_kinematics(coords)
        if interpolate:
            if duration is not None:
                self.writeInterpolatedMotion(angles, duration)
            else:
                self.writeInterpolatedMotion(angles)
        else:
            self.writeAngles(angles)
        self.parent.single_tick()

    def write_leg_coords(self, coords: tuple, leg):
        angles = self.kinematics.inverse_leg(coords, leg)
        self.writeAngles(angles)

    def checkForData(self):
        try:
            bytesToRead = self.ser.inWaiting()
            if bytesToRead > 0:
                readString = self.ser.readline().decode("utf-8")
                if readString.startswith("t"):
                    self.notifyText(readString[1:])
                else:
                    currentState = [float(x) for x in readString.split(';')[0:-1]]
                    self.notifyState(currentState)
                    self.notifyLegState(self.kinematics.forward(currentState))
                return True
            else:
                return False
        except serial.SerialException:
            self.connected = False
            p = multiprocessing.Process(target=self.retryConnect)
            p.start()
            return False

    def requestState(self):
        if self.has_connection():
            self.ser.write(b's  ')

    def has_connection(self):
        return self.connected

    def registerLegState(self, observer: LegStateObserver):
        self.legStateObservers.append(observer)

    def unregisterLegStateObserver(self, observer: LegStateObserver):
        self.legStateObservers.remove(observer)

    def registerState(self, observer: StateObserver):
        self.stateObservers.append(observer)

    def unregisterState(self, observer: StateObserver):
        self.stateObservers.remove(observer)

    def registerText(self, observer: TextObserver):
        self.textObservers.append(observer)

    def unregisterText(self, observer: TextObserver):
        self.textObservers.remove(observer)

    def notifyState(self, values):
        [x.connectorCallback(values) for x in self.stateObservers]

    def notifyText(self, value):
        [x.connectorCallback(value) for x in self.textObservers]

    def notifyLegState(self, values):
        [x.connectorCallback(values) for x in self.legStateObservers]

    def set_kinematics(self, kinematics):
        self.kinematics = kinematics
