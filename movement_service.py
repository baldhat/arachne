from connection.observer import LegStateObserver
from direction import Direction
from time import time

forward_moves = [
    [
        [-0.4375, 3.0625, -1.5],
        [-3.0625, 0.4375, -1.5],
        [0.875, -2.625, -1.5],
        [1.75, -1.75, 0]
    ],
    [
        [-0.4375, 3.0625, -1.5],
        [-3.0625, 0.4375, -1.5],
        [0.875, -2.625, -1.5],
        [3.5, 0, -1.5]
    ],
    [
        [-0.875, 2.625, -1.5],
        [-3.5, 0, -1.5],
        [0.4375, -3.0625, -1.5],
        [3.0625, -0.4375, -1.5]
    ],
    [
        [-0.875, 2.625, -1.5],
        [-3.5, 0, 0],
        [0.4375, -3.0625, -1.5],
        [3.0625, -0.4375, -1.5]
    ],
    [
        [-0.875, 2.625, -1.5],
        [-1.75, 1.75, -1.5],
        [0.4375, -3.0625, -1.5],
        [3.0625, -0.4375, -1.5]
    ],
    [
        [-1.3125, 2.1875, -1.5],
        [-2.1875, 1.3125, -1.5],
        [0, -3.5, -1.5],
        [2.625, -0.875, -1.5]
    ],
    [
        [-1.3125, 2.1875, -1.5],
        [-2.1875, 1.3125, -1.5],
        [0, -3.5, 0],
        [2.625, -0.875, -1.5]
    ],
    [
        [-1.3125, 2.1875, -1.5],
        [-2.1875, 1.3125, -1.5],
        [1.75, -1.75, -1.5],
        [2.625, -0.875, -1.5]
    ],
    [
        [-1.75, 1.75, -1.5],
        [-2.625, 0.875, -1.5],
        [1.3125, -2.1875, -1.5],
        [2.1875, -1.3125, -1.5]
    ],
    [
        [-1.75, 1.75, 0],
        [-2.625, 0.875, -1.5],
        [1.3125, -2.1875, -1.5],
        [2.1875, -1.3125, -1.5]
    ],
    [
        [0, 3.5, 0],
        [-2.625, 0.875, -1.5],
        [1.3125, -2.1875, -1.5],
        [2.1875, -1.3125, -1.5]
    ],
    [
        [-0.4375, 3.0625, -1.5],
        [-3.0625, 0.4375, -1.5],
        [0.875, -2.625, -1.5],
        [1.75, -1.75, -1.5]
    ],
]


class MovementService(LegStateObserver):
    def __init__(self, connector):
        self.connector = connector

        self.direction = Direction.STOP
        self.nextMoveTimestamp = None
        self.moveDuration = 0.3

        self.state = []
        self.next_move_index = 0

        self.connector.registerLegState(self)

    def forward(self):
        self.direction = Direction.FORWARD
        self.nextMoveTimestamp = time()

    def nextMove(self):
        if self.direction == Direction.FORWARD:
            self.connector.write_coords(self.nextForwardMove(), interpolate=True, duration=self.moveDuration * 1000)
            self.nextMoveTimestamp = time() + self.moveDuration

    def nextForwardMove(self):
        next_move = [[y * 0.93 for y in x] for x in forward_moves[self.next_move_index]]
        self.next_move_index = (self.next_move_index + 1) % len(forward_moves)
        return next_move

    def hasMove(self):
        return self.direction != Direction.STOP \
               and self.nextMoveTimestamp is not None \
               and time() >= self.nextMoveTimestamp

    def connectorCallback(self, values: [float]):
        self.state = [values[4], values[8], values[12], values[16]]

    def stop(self):
        self.direction = Direction.STOP
