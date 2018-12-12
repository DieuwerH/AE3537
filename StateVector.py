import numpy as np
import datetime
import pytz


class StateVector:
    omega_earth = 7.2921158553e-5

    def __init__(self, px, py, pz, vx, vy, vz):
        self.pos = np.array([px,py,pz])
        self.vel = np.array([vx,vy,vz])

    def __str__(self):
        return 'Pos: ' + str(self.pos) + ', Vel:' + str(self.vel)

    def __repr__(self):
        return 'StateVector()'

    def rotate_time(self, time):
        # DateTime of Vernal Equinox 2018
        L0 = datetime.datetime(2018, 3, 20, 16, 15, 0, 0, pytz.UTC)
        # turning rate per second
        # omega_earth = 7.2921158553e-5

        timediff = (time - L0).total_seconds()
        angle = self.omega_earth * timediff
        self.rotate_velocity_angle(angle)
        self.rotate_position_angle(angle)

    def rotate_velocity_angle(self, angle):
        rotation_matrix = np.array([
            [np.cos(angle), np.sin(angle), 0],
            [-np.sin(angle), np.cos(angle), 0],
            [0, 0, 1]
        ])
        plus1min1 = np.array([
            [0,1,0],
            [-1,0,0],
            [0,0,0]
        ])

        # turning rate per second
        # omega_earth = 7.2921158553e-5
        derivative_matrix = (self.omega_earth*plus1min1).dot(rotation_matrix)

        self.vel = rotation_matrix.dot(self.vel) + derivative_matrix.dot(self.pos)


    def rotate_position_angle(self, angle):
        rotation_matrix = np.array([
            [np.cos(angle), np.sin(angle), 0],
            [-np.sin(angle), np.cos(angle), 0],
            [0,0,1]
        ])
        self.pos = rotation_matrix.dot(self.pos)

    def dotPosPos(self, other):
        return np.vdot(self.pos, other.pos)
        # return (self.posX() * other.posX()) + (self.posY() + other.posY()) + (self.posZ() + other.posZ())

    def dotVelPos(self, other):
        return np.vdot(self.vel, other.pos)
        # return (self.velX() * other.posX()) + (self.velY() + other.posY()) + (self.velZ() + other.posZ())

    def dotPosVel(self, other):
        return np.vdot(self.pos, other.vel)
        # return (self.posX() * other.velX()) + (self.posY() + other.velY()) + (self.posZ() + other.velZ())

    def dotVelVel(self, other):
        return np.vdot(self.vel, other.vel)
        # return (self.velX() * other.velX()) + (self.velY() + other.velY()) + (self.velZ() + other.velZ())

    def minus(self, other):
        return StateVector(self.posX() - other.posX(), self.posY() - other.posY(), self.posZ() - other.posZ(),
                           self.velX(), self.velY(), self.velZ())

    def plus(self, other):
        return StateVector(self.posX() + other.posX(), self.posY() + other.posY(), self.posZ() - other.posZ(),
                           self.velX(), self.velY(), self.velZ())

    def times(self, scalar):
        return StateVector(self.posX() * scalar, self.posY() * scalar, self.posZ() * scalar, 0,0,0)

    def divide(self, scalar):
        return StateVector(self.posX() / scalar, self.posY() / scalar, self.posZ() / scalar, 0,0,0)
    # get x position
    def posX(self):
        return self.pos[0]

    # get y position
    def posY(self):
        return self.pos[1]

    # get z position
    def posZ(self):
        return self.pos[2]

    # get x velocity
    def velX(self):
        return self.vel[0]

    # get x=y velocity
    def velY(self):
        return self.vel[1]

    # get z velocity
    def velZ(self):
        return self.vel[2]

    # get radial distance
    def getRange(self):
        return np.linalg.norm(self.pos)
        # return np.sqrt(np.square(self.posX()) + np.square(self.posY()) + np.square(self.posZ()))

    # get inclination
    def getPhi(self):
        return np.arccos(self.posZ()/self.getRange())

    # get azimuth angle
    def getTheta(self):
        return np.arctan2(self.posY(), self.posX())

    # Retrieve spherical coordinates
    # returns r, theta, phi
    def getSpecricalCoordinates(self):
        return (self.getRange(), self.getTheta(), self.getPhi())

    def printLength(self):
        print(np.sqrt( np.square(self.posX()) + np.square(self.posY()) + np.square(self.posZ()) ))