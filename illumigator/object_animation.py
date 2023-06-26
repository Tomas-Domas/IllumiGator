import numpy


class ObjectAnimation:
    t: float  # as in time for a parametric equation
    dt: float
    endpoint1: numpy.ndarray
    endpoint2: numpy.ndarray

    def __init__(self, endpoint1: numpy.ndarray, endpoint2: numpy.ndarray, dt):
        self.t = 0
        self.dt = dt
        self.endpoint1 = endpoint1
        self.endpoint2 = endpoint2

    def get_new_position(self):
        self.t = self.t + self.dt
        if self.t > 1:
            self.dt = - self.dt
            self.t = 1
        if self.t < 0:
            self.dt = - self.dt
            self.t = 0

        return self.endpoint1 + self.t * (self.endpoint2 - self.endpoint1)

    def backtrack(self):
        self.t = self.t - self.dt
        if self.t > 1:
            self.dt = - self.dt
            self.t = 1
        if self.t < 0:
            self.dt = - self.dt
            self.t = 0
