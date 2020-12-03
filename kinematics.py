import numpy as np
from math import cos, sin, pi


class Kinematics:
    mins = [
        120, 135, 140, 170,
        168, 4, 176, 4,
        1, 180, 3, 177
    ]

    maxs = [
        10, 25, 30, 60,
        0, 172, 6, 172,
        178, 3, 180, 0
    ]

    minReal = [
        -85, -85, -85, -85,
        -85, -85, -85, -85,
        -130, -130, -130, -130
    ]

    maxReal = [
        85, 85, 85, 85,
        85, 85, 85, 85,
        30, 30, 30, 30
    ]

    def __init__(self):
        pass

    def dhToMatrix(self, d, theta, r, alpha):
        return np.array([
            [cos(theta), -sin(theta) * cos(alpha), sin(theta) * sin(alpha), r * cos(theta)],
            [sin(theta), cos(theta) * cos(alpha), -cos(theta) * sin(alpha), r * sin(theta)],
            [0,          sin(alpha),               cos(alpha),              d],
            [0, 0, 0, 1]
        ])

    def relToReal(self, vals):
        for i, val in enumerate(vals):
            vals[i] = val * (self.maxReal[i] - self.minReal[i]) + self.minReal[i]
        return vals

    def realToRel(self, vals):
        for i, val in enumerate(vals):
            vals[i] = round((val - self.minReal[i]) / (self.maxReal[i] - self.minReal[i]), 2)
        return vals

    def relToAbs(self, i, rel):
        return rel * (self.maxs[i] - self.mins[i]) + self.mins[i]

    def absToRel(self, i, abso):
        return round((abso - self.mins[i]) / (self.maxs[i] - self.mins[i]), 2)

    def toRad(self, vals):
        return np.array([x * 0.0174533 for x in vals])

    def forward(self, relJointAngles):
        realAngles = self.relToReal(relJointAngles)
        radAngles = self.toRad(realAngles)

        rotOff1 = pi/2
        t11 = self.dhToMatrix(0, radAngles[0] + rotOff1, 0.5, pi / 2)
        t12 = self.dhToMatrix(0, radAngles[4], 1.35, 0)
        t13 = self.dhToMatrix(0, radAngles[8], 2.07, 0)

        j10 = np.array([0, 0.2, 0])
        j11 = j10 + [t11[0, 3], t11[1,3], t11[2,3]]
        j12 = j10 + [(t11@t12)[0,3], (t11@t12)[1,3], (t11@t12)[2,3]]
        j13 = j10 + [(t11@t12@t13)[0,3], (t11@t12@t13)[1,3], (t11@t12@t13)[2,3]]

        rotOff2 = pi
        t21 = self.dhToMatrix(0, radAngles[1] + rotOff2, 0.5, pi / 2)
        t22 = self.dhToMatrix(0, radAngles[5], 1.35, 0)
        t23 = self.dhToMatrix(0, radAngles[9], 2.07, 0)

        j20 = np.array([-0.2, 0, 0])
        j21 = j20 + [t21[0, 3], t21[1, 3], t21[2, 3]]
        j22 = j20 + [(t21 @ t22)[0, 3], (t21 @ t22)[1, 3], (t21 @ t22)[2, 3]]
        j23 = j20 + [(t21 @ t22 @ t23)[0, 3], (t21 @ t22 @ t23)[1, 3], (t21 @ t22 @ t23)[2, 3]]

        rotOff2 = - pi / 2
        t31 = self.dhToMatrix(0, radAngles[2] + rotOff2, 0.5, pi / 2)
        t32 = self.dhToMatrix(0, radAngles[6], 1.35, 0)
        t33 = self.dhToMatrix(0, radAngles[10], 2.07, 0)

        j30 = np.array([0, -0.2, 0])
        j31 = j30 + [t31[0, 3], t31[1, 3], t31[2, 3]]
        j32 = j30 + [(t31 @ t32)[0, 3], (t31 @ t32)[1, 3], (t31 @ t32)[2, 3]]
        j33 = j30 + [(t31 @ t32 @ t33)[0, 3], (t31 @ t32 @ t33)[1, 3], (t31 @ t32 @ t33)[2, 3]]

        rotOff2 = 0
        t41 = self.dhToMatrix(0, radAngles[3] + rotOff2, 0.5, pi / 2)
        t42 = self.dhToMatrix(0, radAngles[7], 1.35, 0)
        t43 = self.dhToMatrix(0, radAngles[11], 2.07, 0)

        j40 = np.array([0.2, 0, 0])
        j41 = j40 + [t41[0, 3], t41[1, 3], t21[2, 3]]
        j42 = j40 + [(t41 @ t42)[0, 3], (t41 @ t42)[1, 3], (t41 @ t42)[2, 3]]
        j43 = j40 + [(t41 @ t42 @ t43)[0, 3], (t41 @ t42 @ t43)[1, 3], (t41 @ t42 @ t43)[2, 3]]

        return [[0, 0, 0],
                j10, j11, j12, j13,
                j20, j21, j22, j23,
                j30, j31, j32, j33,
                j40, j41, j42, j43
        ]

