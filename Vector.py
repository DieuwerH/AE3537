import math

class Vector:

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def rotate_z(self, theta):
        theta = math.radians(theta)
        newx = ((math.cos(theta)*self.x) + (-1* math.sin(theta) * self.y))
        newy = ((math.sin(theta)*self.x) + (math.cos(theta) * self.y))
        newz = self.z
        self.x = newx
        self.y = newy
        self.z = newz

    def print(self):
        print('x:', self.x, 'y:', self.y, 'z:', self.z)