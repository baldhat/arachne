from MainWindow import Window
from connection.connector import Connector


if __name__ == '__main__':
    connector = Connector('COM8', 115200)

    app = Window(connector)

    while app.isAlive:
        app.tick()


