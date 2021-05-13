import numpy as np
from math import cos, sin, pi, atan, sqrt, acos


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
        self.last_angles = []
        self.last_positions = []

    def dhToMatrix(self, d, theta, r, alpha):
        return np.array([
            [cos(theta), -sin(theta) * cos(alpha), sin(theta) * sin(alpha), r * cos(theta)],
            [sin(theta), cos(theta) * cos(alpha), -cos(theta) * sin(alpha), r * sin(theta)],
            [0,          sin(alpha),               cos(alpha),                 d          ],
            [0,            0,                       0,                         1          ]
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

    def realToRad(self, vals):
        return np.array([x * 0.0174533 for x in vals])

    def radToRel(self, vals):
        return self.realToRel(np.array([x / 0.0174533 for x in vals]))

    def neutral_pos_endpoints(self):
        endpoints = self.forward([0.5, 0.5, 0.5, 0.5, 0.8, 0.8, 0.8, 0.8, 0.03, 0.03, 0.03, 0.03])
        return [endpoints[4], endpoints[8], endpoints[12], endpoints[16]]

    def shift_point_of_mass(self, x, y, z):
        endpoints = self.neutral_pos_endpoints()
        leg1_pos = [endpoints[0][0] - x, endpoints[0][1] - y, -z]
        leg2_pos = [endpoints[1][0] - x, endpoints[1][1] - y, -z]
        leg3_pos = [endpoints[2][0] - x, endpoints[2][1] - y, -z]
        leg4_pos = [endpoints[3][0] - x, endpoints[3][1] - y, -z]

        return self.inverse_kinematics([leg1_pos, leg2_pos, leg3_pos, leg4_pos])

    def inverse_kinematics(self, leg_endpoints):
        leg1_pos = leg_endpoints[0]
        leg2_pos = leg_endpoints[1]
        leg3_pos = leg_endpoints[2]
        leg4_pos = leg_endpoints[3]

        # Offset by the starting point of the leg
        leg1_pos_rel = leg1_pos - self.last_positions[1]
        leg2_pos_rel = leg2_pos - self.last_positions[5]
        leg3_pos_rel = leg3_pos - self.last_positions[9]
        leg4_pos_rel = leg4_pos - self.last_positions[13]

        leg1_theta1 = atan(- leg1_pos_rel[0] / leg1_pos_rel[1])
        leg2_theta1 = atan(- leg2_pos_rel[1] / - leg2_pos_rel[0])
        leg3_theta1 = atan(leg3_pos_rel[0] / - leg3_pos_rel[1])
        leg4_theta1 = atan(leg4_pos_rel[1] / leg4_pos_rel[0])

        # Offset by the starting point of the arm / end of shoulder
        leg1_arm_offset = np.array([ cos(leg1_theta1 + pi/2) * 0.5, sin(leg1_theta1 + pi/2) * 0.5, 0]) + self.last_positions[1]

        leg1_p = sqrt((leg1_pos[0] - leg1_arm_offset[0])**2 + (leg1_pos[1] - leg1_arm_offset[1])**2)
        leg1_L = sqrt(leg1_p**2 + leg1_pos[2]**2)
        if leg1_L > 1.35 + 2.07:
            print(leg1_L, "out of range")
            return self.last_angles
        leg1_theta2 = acos((1.35 ** 2 + leg1_L ** 2 - 2.07 ** 2) / (2 * 1.35 * leg1_L)) - atan(-leg1_pos[2] / leg1_p)
        leg1_theta3 = acos(((1.35**2 + 2.07**2 - leg1_L**2 ) / (2*1.35*2.07))) + pi * 1.26
        if leg1_theta3 > pi:
            leg1_theta3 -= 2 * pi

        # Offset by the starting point of the arm / end of shoulder
        leg2_arm_offset = np.array([ cos(leg2_theta1 + pi) * 0.5, sin(leg2_theta1 + pi) * 0.5, 0]) + self.last_positions[5]

        leg2_p = sqrt((leg2_pos[0] - leg2_arm_offset[0]) ** 2 + (leg2_pos[1] - leg2_arm_offset[1]) ** 2)
        leg2_L = sqrt(leg2_p ** 2 + leg2_pos[2] ** 2)
        if leg2_L > 1.35 + 2.07:
            print("out of range")
            return self.last_angles
        leg2_theta2 = acos((1.35 ** 2 + leg2_L ** 2 - 2.07 ** 2) / (2 * 1.35 * leg2_L)) - atan(-leg2_pos[2] / leg2_p)
        leg2_theta3 = acos(((1.35 ** 2 + 2.07 ** 2 - leg2_L ** 2) / (2 * 1.35 * 2.07))) + pi * 1.26
        if leg2_theta3 > pi:
            leg2_theta3 -= 2 * pi

        ########### LEG 3 ###############
        # Offset by the starting point of the arm / end of shoulder
        leg3_arm_offset = np.array([cos(leg3_theta1 + 1.5 * pi) * 0.5, sin(leg3_theta1 + 1.5 * pi) * 0.5, 0]) + \
                          self.last_positions[9]

        leg3_p = sqrt((leg3_pos[0] - leg3_arm_offset[0]) ** 2 + (leg3_pos[1] - leg3_arm_offset[1]) ** 2)
        leg3_L = sqrt(leg3_p ** 2 + leg3_pos[2] ** 2)
        if leg3_L > 1.35 + 2.07:
            print("out of range")
            return self.last_angles
        leg3_theta2 = acos((1.35 ** 2 + leg3_L ** 2 - 2.07 ** 2) / (2 * 1.35 * leg3_L)) - atan(
            -leg3_pos[2] / leg3_p)
        leg3_theta3 = acos(((1.35 ** 2 + 2.07 ** 2 - leg3_L ** 2) / (2 * 1.35 * 2.07))) + pi * 1.26
        if leg3_theta3 > pi:
            leg3_theta3 -= 2 * pi

        ########### LEG 4 ###############
        # Offset by the starting point of the arm / end of shoulder
        leg4_arm_offset = np.array([cos(leg4_theta1 ) * 0.5, sin(leg4_theta1 ) * 0.5, 0]) + \
                          self.last_positions[13]

        leg4_p = sqrt((leg4_pos[0] - leg4_arm_offset[0]) ** 2 + (leg4_pos[1] - leg4_arm_offset[1]) ** 2)
        leg4_L = sqrt(leg4_p ** 2 + leg4_pos[2] ** 2)
        if leg4_L > 1.35 + 2.07:
            print("out of range")
            return self.last_angles
        leg4_theta2 = acos((1.35 ** 2 + leg4_L ** 2 - 2.07 ** 2) / (2 * 1.35 * leg4_L)) - atan(
            -leg4_pos[2] / leg4_p)
        leg4_theta3 = acos(((1.35 ** 2 + 2.07 ** 2 - leg4_L ** 2) / (2 * 1.35 * 2.07))) + pi * 1.26
        if leg4_theta3 > pi:
            leg4_theta3 -= 2 * pi

        shoulders = self.radToRel([leg1_theta1, leg2_theta1, leg3_theta1, leg4_theta1])

        angles = self.last_angles
        angles[0:4] = shoulders
        angles[4:8] = self.radToRel([leg1_theta2, leg2_theta2, leg3_theta2, leg4_theta2])
        angles[8:12] = self.radToRel([leg1_theta3, leg2_theta3, leg3_theta3, leg4_theta3])

        for i, angle in enumerate(angles):
            if angle < 0:
                angles[i] = 0
                print("Relative position too small")
            elif angle > 1:
                angles[i] = 1
                print("Relative position too big")

        return angles

    def inverse_leg(self, leg_endpoint_coords, leg):
        last_endpoints = [self.last_positions[4], self.last_positions[8], self.last_positions[12], self.last_positions[16]]
        last_endpoints[leg] = np.array(leg_endpoint_coords)
        return self.inverse_kinematics(last_endpoints)

    def forward(self, relJointAngles):
        self.last_angles = np.copy(relJointAngles)
        realAngles = self.relToReal(relJointAngles)
        radAngles = self.realToRad(realAngles)

        j10, j11, j12, j13 = self.leg1Forward(radAngles)

        j20, j21, j22, j23 = self.leg2forward(radAngles)

        j30, j31, j32, j33 = self.leg3forward(radAngles)

        j40, j41, j42, j43 = self.leg4forward(radAngles)

        self.last_positions = [[0, 0, 0],
                j10, j11, j12, j13,
                j20, j21, j22, j23,
                j30, j31, j32, j33,
                j40, j41, j42, j43
        ]

        return self.last_positions

    def legForward(self, rotOff, theta1, theta2, theta3, offset):
        t41 = self.dhToMatrix(0, theta1 + rotOff, 0.5, pi / 2)
        t42 = self.dhToMatrix(0, theta2, 1.35, 0)
        t43 = self.dhToMatrix(0, theta3, 2.07, 0)
        j41 = offset + [t41[0, 3], t41[1, 3], t41[2, 3]]
        joint2 = t41 @ t42
        joint3 = t41 @ t42 @ t43
        j42 = offset + [joint2[0, 3], joint2[1, 3], joint2[2, 3]]
        j43 = offset + [joint3[0, 3], joint3[1, 3], joint3[2, 3]]
        return offset, j41, j42, j43

    def leg4forward(self, radAngles):
        return self.legForward(0, radAngles[3], radAngles[7], radAngles[11], np.array([0.2, 0, 0]))

    def leg3forward(self, radAngles):
        return self.legForward(-pi / 2, radAngles[2], radAngles[6], radAngles[10], np.array([0, -0.2, 0]))

    def leg2forward(self, radAngles):
        return self.legForward(pi, radAngles[1], radAngles[5], radAngles[9], np.array([-0.2, 0, 0]))

    def leg1Forward(self, radAngles):
        return self.legForward(pi / 2, radAngles[0], radAngles[4], radAngles[8], np.array([0, 0.2, 0]))

