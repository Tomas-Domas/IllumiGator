import math

import arcade
import numpy

from illumigator import util

class Line:
    def __init__(
        self,
        parent_object,
        point1: numpy.ndarray,
        point2: numpy.ndarray,
        is_reflective: bool = False,
        is_refractive: bool = False,
        is_receiver: bool = False,
        is_enemy: bool = False
    ):
        self.parent_object = parent_object
        self._point1 = point1
        self._point2 = point2
        self.is_reflective = is_reflective
        self.is_refractive = is_refractive
        self.is_receiver = is_receiver
        self.is_enemy = is_enemy

        self._normal = None

    def move(self, world_object_center, move_distance, rotate_angle=0):
        self._point1 = (
            util.rotate_around_point(world_object_center, self._point1, rotate_angle)
            + move_distance
        )
        self._point2 = (
            util.rotate_around_point(world_object_center, self._point2, rotate_angle)
            + move_distance
        )
        if self.is_reflective or self.is_refractive:
            self.calculate_normal()

    def calculate_normal(self):
        x = self._point1[1] - self._point2[1]
        y = self._point2[0] - self._point1[0]
        self._normal = numpy.array([x, y]) / math.sqrt(x*x + y*y)

    def draw(self, *, color=arcade.color.ORANGE_RED, thickness=1):
        arcade.draw_line(
            self._point1[0], self._point1[1],
            self._point2[0], self._point2[1],
            color,
            line_width=thickness
        )
