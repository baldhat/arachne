from connection.observer import LegStateObserver
from direction import Direction
from time import time

d = 0.4    # step distance
sh = -0.8  # step height
wsh = -1   # weight shift height
bh = -1.5  # body height

forward_moves = [
    [ # x + d, y - d
        [-0.4375 + d, 3.0625 - d, bh],
        [-3.0625 + d, 0.4375 - d, wsh],
        [0.875 + d, -2.625 - d, bh],
        [1.75, -1.75, sh]
    ],
    [ # x + d, y - d
        [-0.4375 + d, 3.0625 - d, bh],
        [-3.0625 + d, 0.4375 - d, bh],
        [0.875 + d, -2.625 - d, bh],
        [3.5, 0, bh]
    ],
    [ # x - d, y + d
        [-0.875 - d, 2.625 + d, bh],
        [-3.5, 0, bh],
        [0.4375 - d, -3.0625 + d, bh],
        [3.0625 - d, -0.4375 + d, wsh]
    ],
    [ # x - d, y + d
        [-0.875 - d, 2.625 + d, bh],
        [-3.5, 0, sh],
        [0.4375 - d, -3.0625 + d, bh],
        [3.0625 - d, -0.4375 + d, wsh]
    ],
    [ # x - d, y + d
        [-0.875 - d, 2.625 + d, bh],
        [-1.75, 1.75, bh],
        [0.4375 - d, -3.0625 + d, bh],
        [3.0625 - d, -0.4375 + d, bh]
    ],
    [ # x + d, y - d
        [-1.3125 + d, 2.1875 - d, wsh],
        [-2.1875 + d, 1.3125 - d, bh],
        [0, -3.5, bh],
        [2.625 + d, -0.875 - d, bh]
    ],
    [ # x + d, y - d
        [-1.3125 + d, 2.1875 - d, wsh],
        [-2.1875 + d, 1.3125 - d, bh],
        [0, -3.5, sh],
        [2.625 + d, -0.875 - d, bh]
    ],
    [ # x + d, y - d
        [-1.3125 + d, 2.1875 - d, bh],
        [-2.1875 + d, 1.3125 - d, bh],
        [1.75, -1.75, bh],
        [2.625 + d, -0.875 - d, bh]
    ],
    [ # x - d, y + d
        [-1.75, 1.75, bh],
        [-2.625 - d, 0.875 + d, bh],
        [1.3125 - d, -2.1875 + d, wsh],
        [2.1875 - d, -1.3125 + d, bh]
    ],
    [ # x - d, y + d
        [-1.75, 1.75, sh],
        [-2.625 - d, 0.875 + d, bh],
        [1.3125 - d, -2.1875 + d, wsh],
        [2.1875 - d, -1.3125 + d, bh]
    ],
    [ # x - d, y + d
        [0, 3.5, 0],
        [-2.625 - d, 0.875 + d, bh],
        [1.3125 - d, -2.1875 + d, bh],
        [2.1875 - d, -1.3125 + d, bh]
    ],
    [ # x + d, y - d
        [-0.4375 + d, 3.0625 - d, bh],
        [-3.0625 + d, 0.4375 - d, wsh],
        [0.875 + d, -2.625 - d, -bh],
        [1.75, -1.75, bh]
    ],
]


class MovementService(LegStateObserver):
    def __init__(self, connector):
        self.connector = connector

        self.direction = Direction.STOP
        self.nextMoveTimestamp = None
        self.moveDuration = 0.2

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
