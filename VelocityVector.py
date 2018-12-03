import numpy as np
import datetime

class VelocityVector:

    def __init__(self, x, y, z):
        self.vec = np.array([x,y,z])

    def __str__(self):
        return str(self.vec)

    def __repr__(self):
        return "VelocityVector()"

    def rotate_time(self, time):
        # DateTime of Vernal Equinox 2018
        L0 = datetime.datetime(2018, 3, 20, 17, 15, 0, 0)
        # turning rate per second
        omega_earth = 7.2921158553e-5

        timediff = (time - L0).total_seconds()
        angle = omega_earth * timediff
        self.rotate_angle(angle)

    def rotate_angle(self, angle):
        rotation_matrix = np.array([
            [np.cos(angle), np.sin(angle), 0],
            [-np.sin(angle), np.cos(angle), 0],
            [0, 0, 1]
        ])
        self.vec = rotation_matrix.dot(self.vec)

    def getX(self):
        return self.vec[0]

    def getY(self):
        return self.vec[1]

    def getZ(self):
        return self.vec[2]