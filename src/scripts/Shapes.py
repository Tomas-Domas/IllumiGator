import random
import numpy
import arcade

COLORS = [arcade.color.LION, arcade.color.BLUE, arcade.color.RED, arcade.color.GREEN,
          arcade.color.PURPLE, arcade.color.PINK, arcade.color.AMBER, arcade.color.ORANGE]

# Light Source Constants
NUM_LIGHT_RAYS = 1

# Ray Marching Constants
MAXSTEPS = 100
MAXDISTANCE = 1000
MAX_GENS = 5
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
        distance_difference = numpy.abs(point - self.position) - (self.size / 2)
        outside_distance = numpy.linalg.norm(numpy.maximum(distance_difference, numpy.zeros(2)))
        inside_distance = min(max(distance_difference[0], distance_difference[1]), 0)
        return outside_distance + inside_distance


class Mirror(Rectangle):
    def __init__(self, position, size, rotation_angle=0):
        # initialize the mirror as a type of rectangle
        super().__init__(position, size, rotation_angle, arcade.color.SILVER)
        # compute the normal of the mirror based on its rotation angle
        self.normal = numpy.array([numpy.cos(rotation_angle), numpy.sin(rotation_angle)])

    def reflect(self, direction):
        # calculate reflected direction of ray hitting mirror
        reflected_direction = direction - 2 * numpy.dot(direction, self.normal) * self.normal
        return reflected_direction


class Lens:
    def __init__(self, origin, endpoint, radius_of_curvature=10, rotation_angle=0, color=random.choice(COLORS)):
        self.origin = origin
        self.end = endpoint

        self.length = numpy.linalg.norm(self.end - self.origin)
        self.radius = radius_of_curvature
        self.color = color

    def draw(self):
        arcade.draw_line(self.origin[0], self.origin[1], self.end[0], self.end[1], self.color)

    def sdf(self, point):  # TODO: Finish
        origin_to_point_3D = numpy.concatenate((point - self.origin, [0]))
        origin_to_end_3D = numpy.concatenate((self.end - self.origin, [0]))
        cross = numpy.cross(origin_to_point_3D, origin_to_end_3D)
        (True if cross[2] > 0 else False)

        projection = numpy.dot(origin_to_point_3D, origin_to_end_3D) / self.length

        if projection < 0:
            return numpy.linalg.norm(point - self.origin)
        elif projection > self.length:
            return numpy.linalg.norm(point - self.end)
        else:
            return 0


class LightRay:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction
        self.end = origin.copy()
        self.child = None  # initialize child to null

    def ray_march(self, level_elements, generation=0):
        if generation > MAX_GENS:
            return
        # start ray marching from the origin of the ray
        self.end[0], self.end[1] = self.origin[0], self.origin[1]
        distance_total = 0
        step = 0
        while True:
            # compute the shortest distance from the end of the ray to all elements in the level
            min_dist = level_elements[0].sdf(self.end)
            nearest_element = level_elements[0]
            for element in level_elements[1:]:
                element_distance = element.sdf(self.end)
                # if the curr elem is closer than curr closest then update the min dist and nearest elem
                if min_dist > element_distance:
                    min_dist = element_distance
                    nearest_element = element
            # add the shortest distance to the total distance that the ray has travelled
            distance_total += min_dist
            # move the end of the ray along its direction by the shortest distance
            self.end += self.direction * min_dist

            step += 1
            if min_dist < EPSILON:
                if isinstance(nearest_element, Mirror) and step < MAXSTEPS:
                    """
                    if the ray hit a mirror and hasn't taken too many steps 
                    create child from the hit point with the 
                    reflected direction and continue ray marching
                    """
                    self.child = LightRay(self.end, nearest_element.reflect(self.direction))
                    self.child.ray_march(level_elements, generation=generation + 1)
                return distance_total
            elif step > MAXSTEPS:
                return distance_total
            elif distance_total > MAXDISTANCE:
                return MAXDISTANCE

    def draw(self):
        arcade.draw_line(self.origin[0], self.origin[1], self.end[0], self.end[1], arcade.color.WHITE)
        if self.child:
            self.child.draw()

class LightSource:
    def __init__(self, position, direction, angular_spread):
        self.position = position
        self.direction = direction
        self.light_rays = []
        self.angular_spread = angular_spread

        angle = numpy.arctan2(direction[1], direction[0])

        for l in range(NUM_LIGHT_RAYS):  # TODO: Switch to "spotlight" using self.direction instead of point source
            ray_angle = (l / NUM_LIGHT_RAYS) * (angle - angular_spread / 2) + (1 - l / NUM_LIGHT_RAYS) * (
                    angle + angular_spread / 2)
            ray_direction = numpy.array([numpy.cos(ray_angle), numpy.sin(ray_angle)])
            self.light_rays.append(LightRay(self.position, ray_direction))

    def march_rays(self, level_elements):
        for ray in self.light_rays:
            ray.ray_march(level_elements, generation=0)

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
