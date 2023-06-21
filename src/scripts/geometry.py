import numpy
import arcade
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
        x4 = ray.origin[0] + ray.angle[0]
        y4 = ray.origin[1] + ray.angle[1]

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

    def get_intersection(self, ray) -> tuple[numpy.array, Geometry]:  # TODO: optimize if necessary
        # Don't @ me...    https://en.wikipedia.org/wiki/Line-sphere_intersection#Calculation_using_vectors_in_3D
        temp_calculation = ray.angle @ (ray.origin - self.center)
        nabla = numpy.square(temp_calculation) - (numpy.square(numpy.linalg.norm((ray.origin - self.center))) - self.radius*self.radius)
        if nabla < 0:
            return None, self

        nabla_sqrt = numpy.sqrt(nabla)
        intersection_distance1 = - temp_calculation - nabla_sqrt
        intersection_distance2 = - temp_calculation + nabla_sqrt

        if intersection_distance1 > 0 and intersection_distance2 > 0:
            return ray.origin + ray.angle * min(intersection_distance1, intersection_distance2), self
        elif intersection_distance1 > 0 or intersection_distance2 > 0:
            return ray.origin + ray.angle * max(intersection_distance1, intersection_distance2), self
        else:
            return None, self


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
#     def get_intersection(self, ray) -> tuple[numpy.array, Geometry]:
#         # Don't @ me...    https://en.wikipedia.org/wiki/Line-sphere_intersection#Calculation_using_vectors_in_3D
#
#         # TODO: Angle checking shenanigans
#
#         temp_calculation = ray.direction @ (ray.origin - self.center)
#         nabla = numpy.square(temp_calculation) - (
#                     numpy.square(numpy.linalg.norm((ray.origin - self.center))) - self.radius * self.radius)
#         if nabla < 0:
#             return None, self
#
#         nabla_sqrt = numpy.sqrt(nabla)
#         intersection_distance1 = - temp_calculation - nabla_sqrt
#         intersection_distance2 = - temp_calculation + nabla_sqrt
#
#         if intersection_distance1 > 0 and intersection_distance2 > 0:
#             return ray.origin + ray.direction * min(intersection_distance1, intersection_distance2), self
#         elif intersection_distance1 > 0 or intersection_distance2 > 0:
#             return ray.origin + ray.direction * max(intersection_distance1, intersection_distance2), self
#         else:
#             return None, self
#
#     def draw(self):
#         arcade.draw_arc_outline(self.center[0], self.center[1], self.radius, self.radius, arcade.color.MAGENTA, self.start_angle, self.end_angle)
