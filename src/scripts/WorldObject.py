import random
import numpy
import arcade
import Light
from abc import ABC, abstractmethod

COLORS = [arcade.color.LION, arcade.color.BLUE, arcade.color.RED, arcade.color.GREEN,
          arcade.color.PURPLE, arcade.color.PINK, arcade.color.AMBER, arcade.color.ORANGE]


class WorldObject(ABC):
    @abstractmethod
    def draw(self):
        pass
    # @abstractmethod
    # def distance_to_point(self, point: numpy.array):  # TODO: change to get_intersection_point()
    #     pass



class Line(WorldObject):
    def __init__(self, point1: numpy.array, point2: numpy.array):
        self.point1 = point1
        self.point2 = point2

    def get_intersection_point(self, ray: Light.LightRay) -> numpy.array:
        # Don't @ me...    https://en.wikipedia.org/wiki/Line-line_intersection#Given_two_points_on_each_line_segment
        x1 = self.point1[0]
        y1 = self.point1[1]
        x2 = self.point2[0]
        y2 = self.point2[1]

        x3 = ray.origin[0]
        y3 = ray.origin[1]
        x4 = ray.origin[0] + ray.direction[0]
        y4 = ray.origin[1] + ray.direction[1]

        denominator = (x1-x2) * (y3-y4)  -  (y1-y2) * (x3-x4)
        if denominator == 0:  # Line and ray are parallel
            return None
        t =  ((x1-x3) * (y3-y4)  -  (y1-y3) * (x3-x4)) / denominator
        u = -((x1-x2) * (y1-y3)  -  (y1-y2) * (x1-x3)) / denominator

        if 0 < t < 1 and u > 0:
            return numpy.array([ x1 + t * (x2-x1),   y1 + t * (y2-y1) ])
        return None

    def draw(self):
        arcade.draw_line(self.point1[0], self.point1[1], self.point2[0], self.point2[1], arcade.color.GOLD)


class Rectangle(WorldObject):
    def __init__(self, position: numpy.array, size: numpy.array,
                 rotation_angle=0, color=random.choice(COLORS)):
        self.position = position
        self.rotation_angle = rotation_angle
        self.color = color
        self.size = size

    def draw(self):
        arcade.draw_rectangle_filled(self.position[0], self.position[1], self.size[0], self.size[1], self.color)

    def distance_to_point(self, point: numpy.array) -> float:  # TODO: change to get_intersection_point()
        distanceDifference = numpy.abs(point - self.position) - (self.size/2)
        outsideDistance = numpy.linalg.norm( numpy.maximum(distanceDifference, numpy.zeros(2)) )
        insideDistance = min(max(distanceDifference[0], distanceDifference[1]), 0)
        return outsideDistance + insideDistance
