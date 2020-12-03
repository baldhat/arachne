import multiprocessing
import serial
import time

from connection.observer import StateObserver, TextObserver


class Connector():

    def __init__(self, com_port, baud_rate, max_tries=10):
        self.connected = False
        self.comport = com_port
        self.baud_rate = baud_rate
        self.ser = self.connect(com_port, baud_rate, max_tries)
        self.stateObservers: [StateObserver] = []
        self.textObservers: [TextObserver] = []
        self.requestState()

    def connect(self, comport, baudrate, max_tries):
        try:
            ser = serial.Serial(comport, baudrate)
        except:
            p = multiprocessing.Process(target=self.retryConnect)
            p.start()
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
        time.sleep(5)
        self.ser = self.connect(self.comport, self.baud_rate, 10)
        self.requestState()

    def writeInterpolatedMotion(self, jointValues, duration=1000):
        if self.has_connection():
            valueStrings = [str(value) for value in jointValues]
            valueString = 'r' + ';'.join(valueStrings) + ';' + str(duration)
            self.ser.write(valueString.encode('utf-8'))

    def writePosition(self, jointValues):
        if self.has_connection():
            valueStrings = [str(value) for value in jointValues]
            valueString = 'z' + ';'.join(valueStrings)
            self.ser.write(valueString.encode('utf-8'))

    def writeCommand(self, cmd: str):
        if self.has_connection():
            self.ser.write(cmd.encode('utf-8'))

    def checkForData(self):
        try:
            bytesToRead = self.ser.inWaiting()
            if bytesToRead > 0:
                readString = self.ser.readline().decode("utf-8")
                if readString.startswith("t"):
                    print("Message: " + readString[1:], end="")
                    self.notifyText(readString[1:])
                else:
                    currentState = [float(x) for x in readString.split(';')[0:-1]]
                    print("State: ", end="")
                    print(currentState)
                    self.notifyState(currentState)
        except serial.SerialException:
            self.connected = False
            p = multiprocessing.Process(target=self.retryConnect)
            p.start()

    def requestState(self):
        if self.has_connection():
            self.ser.write(b's  ')

    def has_connection(self):
        return self.connected

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