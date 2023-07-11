import numpy


class ObjectAnimation:
    t: float  # as in time for a parametric equation
    dt: float
    endpoint1: numpy.ndarray
    endpoint2: numpy.ndarray
    angle1: float
    angle2: float

    def __init__(self, endpoint1: numpy.ndarray, endpoint2: numpy.ndarray, dt, angle1=0, angle2=0):
        self.t = 0
        self.dt = dt
        self.endpoint1 = endpoint1
        self.endpoint2 = endpoint2
        self.angle1 = angle1
        self.angle2 = angle2


    def get_new_position(self):
        self.t = self.t + self.dt
        if self.t > 1:
            self.dt = -self.dt
            self.t = 1
        if self.t < 0:
            self.dt = -self.dt
            self.t = 0

        return (
            self.endpoint1 + self.t * (self.endpoint2 - self.endpoint1),
            self.angle1 + self.t * (self.angle2 - self.angle1)
        )

    def backtrack(self):
        self.t = self.t - self.dt
        if self.t > 1:
            self.dt = -self.dt
            self.t = 1
        if self.t < 0:
            self.dt = -self.dt
            self.t = 0
