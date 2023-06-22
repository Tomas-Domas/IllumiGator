import arcade
import numpy
import math
from abc import ABC, abstractmethod

import util.util as util


class Geometry(ABC):
    is_reflective: bool
    is_refractive: bool

    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def get_intersection(self, ray) -> tuple:
        pass

    @abstractmethod
    def move(self, world_object_center, move_distance, rotate_angle=0):
        pass


class Line(Geometry):
    def __init__(self, point1: numpy.array, point2: numpy.array, is_reflective: bool = False,
                 is_refractive: bool = False):
        self.point1 = point1
        self.point2 = point2
        self.is_reflective = is_reflective
        self.is_refractive = is_refractive

        normal_unscaled = numpy.array([-(point2[1] - point1[1]), point2[0] - point1[0]])
        self.normal = normal_unscaled / numpy.linalg.norm(normal_unscaled)

    def get_intersection(self, ray) -> numpy.array:
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
            return None
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator

        if 0 < t < 1 and u > 0:
            return numpy.array([x1 + t * (x2 - x1), y1 + t * (y2 - y1)])
        return None

    def move(self, world_object_center, move_distance, rotate_angle=0):
        self.point1 = util.rotate_around_center(world_object_center, self.point1, rotate_angle) + move_distance
        self.point2 = util.rotate_around_center(world_object_center, self.point2, rotate_angle) + move_distance
        normal_unscaled = numpy.array([-(self.point2[1] - self.point1[1]), self.point2[0] - self.point1[0]])
        self.normal = normal_unscaled / numpy.linalg.norm(normal_unscaled)

    def get_reflected_direction(self, ray):
        return ray.direction - (2 * self.normal * (self.normal @ ray.direction))

    def draw(self):
        if self.is_reflective:
            arcade.draw_line(self.point1[0], self.point1[1], self.point2[0], self.point2[1], arcade.color.WHITE)
        else:
            arcade.draw_line(self.point1[0], self.point1[1], self.point2[0], self.point2[1], arcade.color.BLACK)


class Circle(Geometry):
    def __init__(self, center: numpy.array, radius: float, is_reflective: bool = False, is_refractive: bool = False):
        self.center = center
        self.radius = radius
        self.is_reflective = is_reflective
        self.is_refractive = is_refractive

    def get_intersection(self, ray) -> numpy.array:  # TODO: optimize if necessary
        # Don't @ me...    https://en.wikipedia.org/wiki/Line-sphere_intersection#Calculation_using_vectors_in_3D
        temp_calculation1 = ray.direction @ (ray.origin - self.center)
        temp_calculation2 = numpy.linalg.norm((ray.origin - self.center))
        nabla = (temp_calculation1 * temp_calculation1) - (
                    (temp_calculation2 * temp_calculation2) - self.radius * self.radius)
        if nabla < 0:
            return None

        nabla_sqrt = math.sqrt(nabla)
        intersection_distance1 = - temp_calculation1 - nabla_sqrt
        intersection_distance2 = - temp_calculation1 + nabla_sqrt

        if intersection_distance1 > 0 and intersection_distance2 > 0:
            return ray.origin + ray.direction * min(intersection_distance1, intersection_distance2)
        elif intersection_distance1 > 0 or intersection_distance2 > 0:
            return ray.origin + ray.direction * max(intersection_distance1, intersection_distance2)
        else:
            return None

    def move(self, world_object_center, move_distance, rotate_angle=0):
        self.center = world_object_center

    def get_reflected_direction(self, ray):
        normal = (self.center - ray.end) / self.radius
        return ray.direction - (2 * normal * (normal @ ray.direction))

    def draw(self):
        arcade.draw_circle_outline(self.center[0], self.center[1], self.radius, arcade.color.MAGENTA)

# class Arc(Geometry):  # WIP
#     def __init__(self, center: numpy.array, radius: float, start_angle: float, end_angle: float, is_reflective: bool = False, is_refractive: bool = False):
#         self.center = center
#         self.radius = radius
#         self.start_angle = start_angle
#         self.end_angle = end_angle
#         self.is_reflective = is_reflective
#         self.is_refractive = is_refractive
#
#         def get_intersection(self, ray) -> numpy.array:  # TODO: optimize if necessary
#         # Don't @ me...    https://en.wikipedia.org/wiki/Line-sphere_intersection#Calculation_using_vectors_in_3D
#         temp_calculation1 = ray.direction @ (ray.origin - self.center)
#         temp_calculation2 = numpy.linalg.norm((ray.origin - self.center))
#         nabla = (temp_calculation1*temp_calculation1) - ((temp_calculation2*temp_calculation2) - self.radius*self.radius)
#         if nabla < 0:
#             return None
#
#         nabla_sqrt = math.sqrt(nabla)
#         intersection_distance1 = - temp_calculation1 - nabla_sqrt
#         intersection_distance2 = - temp_calculation1 + nabla_sqrt
#
#         if intersection_distance1 > 0 and intersection_distance2 > 0:
#             return ray.origin + ray.direction * min(intersection_distance1, intersection_distance2)
#         elif intersection_distance1 > 0 or intersection_distance2 > 0:
#             return ray.origin + ray.direction * max(intersection_distance1, intersection_distance2)
#         else:
#             return None
#
#     def draw(self):
#         arcade.draw_arc_outline(self.center[0], self.center[1], self.radius, self.radius, arcade.color.MAGENTA, self.start_angle, self.end_angle)
