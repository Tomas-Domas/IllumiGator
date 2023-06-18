import random
from abc import ABC, abstractmethod

import numpy
import arcade

COLORS = [arcade.color.LION, arcade.color.BLUE, arcade.color.RED, arcade.color.GREEN,
          arcade.color.PURPLE, arcade.color.PINK, arcade.color.AMBER, arcade.color.ORANGE]


class WorldObject(ABC):
    @abstractmethod
    def draw(self):
        pass
    @abstractmethod
    def distance_to_point(self, point: numpy.array):
        pass



class Rectangle(WorldObject):
    def __init__(self, position: numpy.array, size: numpy.array,
                 rotation_angle=0, color=random.choice(COLORS)):
        self.position = position
        self.rotation_angle = rotation_angle
        self.color = color
        self.size = size

    def draw(self):
        # Draw the rectangle
        arcade.draw_rectangle_filled(self.position[0], self.position[1], self.size[0], self.size[1], self.color)

    def distance_to_point(self, point: numpy.array): #TODO: change to get_intersection_point()
        distanceDifference = numpy.abs(point - self.position) - (self.size/2)
        outsideDistance = numpy.linalg.norm( numpy.maximum(distanceDifference, numpy.zeros(2)) )
        insideDistance = min(max(distanceDifference[0], distanceDifference[1]), 0)
        return outsideDistance + insideDistance
