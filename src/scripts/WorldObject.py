import random
import numpy
import arcade
import util.util as util
from abc import ABC, abstractmethod


class WorldObject(ABC):
    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def get_intersection(self, ray) -> tuple[numpy.array, object]:
        pass


class Line(WorldObject):
    def __init__(self, point1: numpy.array, point2: numpy.array):
        self.point1 = point1
        self.point2 = point2

    def get_intersection(self, ray) -> tuple[numpy.array, WorldObject]:
        # Don't @ me...    https://en.wikipedia.org/wiki/Line-line_intersection#Given_two_points_on_each_line_segment
        x1 = self.point1[0]
        y1 = self.point1[1]
        x2 = self.point2[0]
        y2 = self.point2[1]

        x3 = ray.origin[0]
        y3 = ray.origin[1]
        x4 = ray.origin[0] + ray.direction[0]
        y4 = ray.origin[1] + ray.direction[1]

        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denominator == 0:  # Line and ray are parallel
            return None, self
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator

        if 0 < t < 1 and u > 0:
            return numpy.array([x1 + t * (x2 - x1), y1 + t * (y2 - y1)]), self
        return None, self

    def draw(self):
        arcade.draw_line(self.point1[0], self.point1[1], self.point2[0], self.point2[1], arcade.color.GOLD)


class Mirror(Line):
    def __init__(self, point1: numpy.array, point2: numpy.array):
        super().__init__(point1, point2)
        # compute the normal of the mirror based on its rotation angle
        normal_unscaled = numpy.array([-(point2[1] - point1[1]), point2[0] - point1[0]])
        self.normal = normal_unscaled / numpy.linalg.norm(normal_unscaled)

    def get_reflected_direction(self, direction):
        return direction - (2 * self.normal * (self.normal @ direction))  # note: @ is dot product

    def draw(self):
        arcade.draw_line(self.point1[0], self.point1[1], self.point2[0], self.point2[1], arcade.color.SILVER)


class Rectangle(WorldObject):
    def __init__(self, center_position: numpy.array, side_lengths: numpy.array,
                 rotation_angle: float = 0, color: tuple[int, int, int] = random.choice(util.COLORS)):
        self.center = center_position
        self.rotation_angle = rotation_angle
        self.color = color
        self.side_lengths = side_lengths

        axis1 = side_lengths[0] * 0.5 * numpy.array([
            numpy.cos(rotation_angle), numpy.sin(rotation_angle)
        ])
        axis2 = side_lengths[1] * 0.5 * numpy.array([
            -numpy.sin(rotation_angle), numpy.cos(rotation_angle)
        ])

        self.elements = [
            Line(center_position - axis1 - axis2,   center_position - axis1 + axis2),
            Line(center_position - axis1 + axis2,   center_position + axis1 + axis2),
            Mirror(center_position + axis1 + axis2,   center_position + axis1 - axis2),
            Line(center_position + axis1 - axis2,   center_position - axis1 - axis2),
        ]

    def draw(self):
        # arcade.draw_rectangle_filled(self.center[0], self.center[1], self.side_lengths[0], self.side_lengths[1],
        #                              self.color, tilt_angle=util.convert_angle_for_arcade(self.rotation_angle))
        for edge in self.elements:
            edge.draw()

    def get_intersection(self, ray) -> tuple[numpy.array, WorldObject]:
        nearest_distance_squared = util.STARTING_DISTANCE_VALUE
        nearest_intersection_object = None
        nearest_intersection_point = None
        for edge in self.elements:
            intersection_point, intersection_object = edge.get_intersection(ray)
            if intersection_point is None:
                continue

            intersection_dist_squared = util.distance_squared(ray.origin, intersection_point)
            if intersection_dist_squared < nearest_distance_squared:
                nearest_distance_squared = intersection_dist_squared
                nearest_intersection_point = intersection_point
                nearest_intersection_object = intersection_object

        return nearest_intersection_point, nearest_intersection_object

