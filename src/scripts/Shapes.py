import random
import numpy
import arcade

COLORS = [arcade.color.LION, arcade.color.BLUE, arcade.color.RED, arcade.color.GREEN,
          arcade.color.PURPLE, arcade.color.PINK, arcade.color.AMBER, arcade.color.ORANGE]

class Rectangle:
    def __init__(self, position, size, rotation_angle=0):
        self.position = position
        self.size = size
        self.rotation_angle = rotation_angle
        self.color = random.choice(COLORS)

    def draw(self):
        # Draw the rectangle
        arcade.draw_rectangle_filled(self.position[0], self.position[1], self.size[0], self.size[1], self.color)

    def sdf(self, point):
        distanceDifference = numpy.abs(point - self.position) - (self.size/2)
        outsideDistance = numpy.linalg.norm( numpy.maximum(distanceDifference, numpy.zeros(2)) )
        insideDistance = min(max(distanceDifference[0], distanceDifference[1]), 0)
        return outsideDistance + insideDistance


class Lens:
    def __init__(self, origin, endpoint, radius_of_curvature=10, rotation_angle=0):
        self.origin = origin
        self.end = endpoint
        self.radius = radius_of_curvature
        self.color = random.choice(COLORS)

    def draw(self):
        draw_line_from_vectors(self.origin, self.end, self.color)

    def sdf(self, point):
        origin_to_point_3D = numpy.concatenate((point - self.origin, [0]))
        origin_to_end_3D = numpy.concatenate((self.end - self.origin, [0]))
        cross = numpy.cross(origin_to_point_3D, origin_to_end_3D)
        return True if cross[2] > 0 else False

def draw_line_from_vectors(v1, v2, color):
    arcade.draw_line(v1[0], v1[1], v2[0], v2[1], color)