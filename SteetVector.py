import numpy as np
import datetime
import time_helper


class StateVector:

    def __init__(self, pos=np.array([0, 0, 0]), vel=np.array([0,0,0]), time=datetime.datetime.now()):
        self.pos_eci = np.array(pos)
        self.vel_eci = np.array(vel)
        self.time = time
        self.pos_ecef, self.vel_ecef = self.calculate_ecef()

    def calculate_ecef(self):
        angle = time_helper.datetime2rad(self.time)
        pos_ecef = self.calculate_ecef_pos(angle)
        vel_ecef = self.calculate_ecef_vel(angle)
        return pos_ecef, vel_ecef

    def calculate_ecef_pos(self, angle):
        rotation_matrix = np.array([
            [np.cos(angle), np.sin(angle), 0],
            [-np.sin(angle), np.cos(angle), 0],
            [0, 0, 1] ])
        return rotation_matrix.dot(self.pos_eci)

    def calculate_ecef_vel(self, angle):
        rotation_matrix = np.array([
            [np.cos(angle), np.sin(angle), 0],
            [-np.sin(angle), np.cos(angle), 0],
            [0, 0, 1]
        ])
        plus1min1 = np.array([
            [0, 1, 0],
            [-1, 0, 0],
            [0, 0, 0]
        ])
        omega_earth = 7.2921158553e-5
        derivative_matrix = (omega_earth * plus1min1).dot(rotation_matrix)
        return rotation_matrix.dot(self.vel_eci) + derivative_matrix.dot(self.pos_eci)

    def get_range(self):
        return np.linalg.norm(self.pos_ecef)
