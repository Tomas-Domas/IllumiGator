import random
import numpy
import arcade

COLORS = [arcade.color.LION, arcade.color.BLUE, arcade.color.RED, arcade.color.GREEN,
          arcade.color.PURPLE, arcade.color.PINK, arcade.color.AMBER, arcade.color.ORANGE]

# Light Source Constants
NUM_LIGHT_RAYS = 100

# Ray Marching Constants
MAXSTEPS = 100
MAXDISTANCE = 1000
EPSILON = 0.5

class Rectangle:
    def __init__(self, position, size, rotation_angle=0, color=random.choice(COLORS)):
        self.position = position
        self.size = size
        self.rotation_angle = rotation_angle
        self.color = color

    def draw(self):
        # Draw the rectangle
        arcade.draw_rectangle_filled(self.position[0], self.position[1], self.size[0], self.size[1], self.color)

    def sdf(self, point):
        distanceDifference = numpy.abs(point - self.position) - (self.size/2)
        outsideDistance = numpy.linalg.norm( numpy.maximum(distanceDifference, numpy.zeros(2)) )
        insideDistance = min(max(distanceDifference[0], distanceDifference[1]), 0)
        return outsideDistance + insideDistance


class Lens:
    def __init__(self, origin, endpoint, radius_of_curvature=10, rotation_angle=0, color=random.choice(COLORS)):
        self.origin = origin
        self.end = endpoint

        self.length = numpy.linalg.norm(self.end - self.origin)
        self.radius = radius_of_curvature
        self.color = color

    def draw(self):
        arcade.draw_line(self.origin[0], self.origin[1], self.end[0], self.end[1], self.color)

    def sdf(self, point): #TODO: Finish
        origin_to_point_3D = numpy.concatenate((point - self.origin, [0]))
        origin_to_end_3D = numpy.concatenate((self.end - self.origin, [0]))
        cross = numpy.cross(origin_to_point_3D, origin_to_end_3D)
        (True if cross[2] > 0 else False)

        projection = numpy.dot(origin_to_point_3D, origin_to_end_3D)/self.length

        if projection < 0:
            return numpy.linalg.norm(point-self.origin)
        elif projection > self.length:
            return numpy.linalg.norm(point-self.end)
        else:
            return 0


class LightRay:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction
        self.end = origin.copy()

    def ray_march(self, level_elements):
        self.end[0], self.end[1] = self.origin[0], self.origin[1]
        distanceTotal = 0
        step = 0
        while True:
            min_dist = level_elements[0].sdf(self.end)
            for element in level_elements[1:]:
                element_distance = element.sdf(self.end)
                if min_dist > element_distance:
                    min_dist = element_distance
            distanceTotal += min_dist
            self.end += self.direction * min_dist

            step += 1
            if min_dist < EPSILON or step > MAXSTEPS:
                return distanceTotal
            elif distanceTotal > MAXDISTANCE:
                return MAXDISTANCE

    def draw(self):
        arcade.draw_line(self.origin[0], self.origin[1], self.end[0], self.end[1], arcade.color.WHITE)

class LightSource:
    def __init__(self, position, direction):
        self.position = position
        self.direction = direction
        self.light_rays = []

        for l in range(NUM_LIGHT_RAYS):
            angle = l * 2 * numpy.pi/NUM_LIGHT_RAYS
            ray_direction = numpy.array([numpy.cos(angle), numpy.sin(angle)])
            self.light_rays.append(LightRay(self.position, ray_direction))

    def march_rays(self, level_elements):
        for ray in self.light_rays:
            ray.ray_march(level_elements)

    def move_to(self, x, y):
        self.position[0] = x
        self.position[1] = y
        for ray in self.light_rays:
            ray.origin[0] = x
            ray.origin[1] = y

    def draw(self):
        for ray in self.light_rays:
            ray.draw()
        arcade.draw_circle_filled(self.position[0], self.position[1], 30, arcade.color.BLACK)