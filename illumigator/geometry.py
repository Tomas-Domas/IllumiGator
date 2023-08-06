import math
from abc import ABC, abstractmethod

import arcade
import numpy

from illumigator import util


class Geometry(ABC):
    def __init__(self, parent_object, is_reflective: bool, is_refractive: bool, is_receiver: bool, is_enemy: bool):
        self.parent_object = parent_object
        self.is_reflective = is_reflective
        self.is_refractive = is_refractive
        self.is_receiver = is_receiver
        self.is_enemy = is_enemy

    @abstractmethod
    def draw(self, *, color=arcade.color.BLUE, thickness=3):
        pass

    @abstractmethod
    def move(self, world_object_center, move_distance, rotate_angle=0):
        pass


class Line(Geometry):
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
        super().__init__(parent_object, is_reflective, is_refractive, is_receiver, is_enemy)
        if is_reflective:
            self._normal = None
        self._point1 = point1
        self._point2 = point2
        self._length = numpy.linalg.norm(point2 - point1)

    def move(self, world_object_center, move_distance, rotate_angle=0):
        self._point1 = (
            util.rotate_around_point(world_object_center, self._point1, rotate_angle)
            + move_distance
        )
        self._point2 = (
            util.rotate_around_point(world_object_center, self._point2, rotate_angle)
            + move_distance
        )
        if self.is_reflective:
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


# class Circle(Geometry):
#     def __init__(
#         self,
#         parent_object,
#         center: numpy.ndarray,
#         radius: float,
#         is_reflective: bool = False,
#         is_refractive: bool = False,
#         is_receiver: bool = False,
#         is_enemy: bool = False
#     ):
#         super().__init__(parent_object, is_reflective, is_refractive, is_receiver, is_enemy)
#         self.center = center
#         self.radius = radius
#
#     def move(self, world_object_center, move_distance, rotate_angle=0):
#         self.center = (
#             util.rotate_around_point(world_object_center, self.center, rotate_angle)
#             + move_distance
#         )
#
#     def draw(self, *, color=arcade.color.MAGENTA, thickness=1):
#         arcade.draw_circle_outline(
#             self.center[0], self.center[1],
#             self.radius, color,
#             border_width=thickness
#         )


class Arc(Geometry):
    def __init__(
        self,
        parent_object,
        center: numpy.ndarray,
        radius: float,
        rotation_angle: float,
        angular_width: float,
        is_reflective: bool = False,
        is_refractive: bool = True,
        is_receiver: bool = False,
        is_enemy: bool = False
    ):
        super().__init__(parent_object, is_reflective, is_refractive, is_receiver, is_enemy)
        if angular_width > numpy.pi:
            raise ValueError("Arc angle cannot be greater than PI")
        self._start_angle = rotation_angle - angular_width / 2
        self._end_angle = rotation_angle + angular_width / 2
        self._constrain_angles()

        self.center = center
        self.radius = radius

    def _constrain_angles(self):  # Constrain between (-PI, PI)
        if self._start_angle > numpy.pi:
            self._start_angle -= 2 * numpy.pi
        elif self._start_angle < -numpy.pi:
            self._start_angle += 2 * numpy.pi

        if self._end_angle > numpy.pi:
            self._end_angle -= 2 * numpy.pi
        elif self._end_angle < -numpy.pi:
            self._end_angle += 2 * numpy.pi

    def move(self, world_object_center, move_distance, rotate_angle=0):
        self.center = (
            util.rotate_around_point(world_object_center, self.center, rotate_angle)
            + move_distance
        )
        self._start_angle += rotate_angle
        self._end_angle += rotate_angle
        self._start_angle += rotate_angle
        self._end_angle += rotate_angle
        self._constrain_angles()

    def draw(self, *, color=arcade.color.MAGENTA, thickness=3):
        if self._start_angle < self._end_angle:
            arcade.draw_arc_outline(
                self.center[0], self.center[1],
                2 * self.radius, 2 * self.radius,
                color,
                self._start_angle * 180 / numpy.pi,
                self._end_angle * 180 / numpy.pi,
                border_width=thickness*2,
                num_segments=512,
            )
        else:
            arcade.draw_arc_outline(
                self.center[0], self.center[1],
                2 * self.radius, 2 * self.radius,
                color,
                self._start_angle * 180 / numpy.pi,
                self._end_angle * 180 / numpy.pi + 360,
                border_width=thickness*2,
                num_segments=512,
            )

    def get_refracted_direction(self, ray):
        # Determine normal
        normal = (ray._end - self.center) / self.radius
        # Determine whether coming into or out of shape
        dot_product = normal @ ray.direction

        if dot_product < 0:  # Ray is coming into the shape
            # Determine refraction angle with respect to normal
            angle = (numpy.pi - math.acos(dot_product)) / util.INDEX_OF_REFRACTION
            if util.two_d_cross_product(ray.direction, normal) < 0:
                angle = -angle
            # Create vector with new angle from normal
            return -util.rotate(normal, angle)

        else:  # Ray is going out of shape
            angle = (numpy.pi - math.acos(-dot_product)) * util.INDEX_OF_REFRACTION
            if util.two_d_cross_product(ray.direction, normal) > 0:
                angle = -angle
            return util.rotate(normal, angle)
