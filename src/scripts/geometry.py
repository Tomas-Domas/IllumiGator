import random
import numpy
import arcade
import util.util as util
from abc import ABC, abstractmethod


class Geometry(ABC):
    is_reflective: bool
    is_refractive: bool
    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def get_intersection(self, ray) -> tuple:
        pass


class Line(Geometry):
    def __init__(self, point1: numpy.array, point2: numpy.array, is_reflective: bool = False, is_refractive: bool = False):
        self.point1 = point1
        self.point2 = point2
        self.is_reflective = is_reflective
        self.is_refractive = is_refractive

        if is_reflective or is_refractive:
            normal_unscaled = numpy.array([-(point2[1] - point1[1]), point2[0] - point1[0]])
            self.normal = normal_unscaled / numpy.linalg.norm(normal_unscaled)


    def get_intersection(self, ray) -> tuple[numpy.array, Geometry]:
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

    def get_reflected_direction(self, direction):
        print( direction - (2 * self.normal * (self.normal @ direction)))
        return direction - (2 * self.normal * (self.normal @ direction))

    def draw(self):
        arcade.draw_line(self.point1[0], self.point1[1], self.point2[0], self.point2[1], arcade.color.GOLD)


class Circle(Geometry):
    def __init__(self, center: numpy.array, radius: float, is_reflective: bool = False, is_refractive: bool = False):
        self.center = center
        self.radius = radius
        self.is_reflective = is_reflective
        self.is_refractive = is_refractive

    def get_intersection(self, ray) -> tuple[numpy.array, Geometry]:
        # Don't @ me...    https://en.wikipedia.org/wiki/Line–sphere_intersection#Calculation_using_vectors_in_3D
        nabla = numpy.square(ray.direction @ (ray.origin - self.center)) - (numpy.square(numpy.linalg.norm((ray.origin - self.center))) - self.radius*self.radius)
        if nabla < 0:
            return None, self
        intersection_distance = - (ray.direction @ (ray.origin - self.center)) - numpy.sqrt(nabla)
        return ray.origin + ray.direction * intersection_distance, self

    def draw(self):
        arcade.draw_circle_outline(self.center[0], self.center[1], self.radius, arcade.color.MAGENTA)