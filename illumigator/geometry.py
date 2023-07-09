from abc import ABC, abstractmethod
import arcade
import numpy
import math

from illumigator import util


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
    def __init__(self, point1: numpy.ndarray, point2: numpy.ndarray, is_reflective: bool = False,
                 is_refractive: bool = False):
        self._point1 = point1
        self._point2 = point2
        self.is_reflective = is_reflective
        self.is_refractive = is_refractive

    def get_intersection(self, ray) -> numpy.ndarray:
        # Don't @ me...    https://en.wikipedia.org/wiki/Line-line_intersection#Given_two_points_on_each_line_segment
        x1 = self._point1[0]
        y1 = self._point1[1]
        x2 = self._point2[0]
        y2 = self._point2[1]

        x3 = ray._origin[0]
        y3 = ray._origin[1]
        x4 = ray._origin[0] + ray._direction[0]
        y4 = ray._origin[1] + ray._direction[1]

        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denominator == 0:  # Line and ray are parallel
            return None
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator

        if 0 < t < 1 and u > 0:
            return numpy.array([x1 + t * (x2 - x1), y1 + t * (y2 - y1)])
        return None

    def move(self, world_object_center, move_distance, rotate_angle=0):
        self._point1 = util.rotate_around_center(world_object_center, self._point1, rotate_angle) + move_distance
        self._point2 = util.rotate_around_center(world_object_center, self._point2, rotate_angle) + move_distance
        if self.is_reflective or self.is_refractive:
            self.calculate_normal()

    def calculate_normal(self):
        normal_unscaled = numpy.array([-(self._point2[1] - self._point1[1]), self._point2[0] - self._point1[0]])
        self._normal = normal_unscaled / numpy.linalg.norm(normal_unscaled)

    def get_reflected_direction(self, ray):
        return ray._direction - (2 * self._normal * (self._normal @ ray._direction))

    def draw(self):
        if self.is_reflective:
            arcade.draw_line(
                self._point1[0], self._point1[1],
                self._point2[0], self._point2[1],
                arcade.color.WHITE,
            )
        else:
            arcade.draw_line(
                self._point1[0], self._point1[1],
                self._point2[0], self._point2[1],
                arcade.color.BLUE,
            )


class Circle(Geometry):
    def __init__(self, center: numpy.ndarray, radius: float, is_reflective: bool = False, is_refractive: bool = False):
        self.center = center
        self.radius = radius
        self.is_reflective = is_reflective
        self.is_refractive = is_refractive

    def get_intersection(self, ray) -> numpy.ndarray:  # TODO: optimize if necessary
        # Don't @ me...    https://en.wikipedia.org/wiki/Line-sphere_intersection#Calculation_using_vectors_in_3D
        temp_calculation1 = ray._direction @ (ray._origin - self.center)
        temp_calculation2 = numpy.linalg.norm(ray._origin - self.center)
        nabla = (temp_calculation1 * temp_calculation1) - (
            (temp_calculation2 * temp_calculation2) - self.radius * self.radius
        )
        if nabla < 0:
            return None

        nabla_sqrt = math.sqrt(nabla)
        intersection_distance1 = -nabla_sqrt - temp_calculation1
        intersection_distance2 = nabla_sqrt - temp_calculation1

        if intersection_distance1 > 0 and intersection_distance2 > 0:
            return ray._origin + ray._direction * min(intersection_distance1, intersection_distance2)
        elif intersection_distance1 > 0 or intersection_distance2 > 0:
            return ray._origin + ray._direction * max(intersection_distance1, intersection_distance2)
        else:
            return None

    def move(self, world_object_center, move_distance, rotate_angle=0):
        self.center = util.rotate_around_center(world_object_center, self.center, rotate_angle) + move_distance

    def draw(self):
        arcade.draw_circle_outline(
            self.center[0], self.center[1], self.radius, arcade.color.MAGENTA
        )


class Arc(Geometry):
    def __init__(self, center: numpy.ndarray, radius: float, rotation_angle: float, angular_width: float, is_reflective: bool = False, is_refractive: bool = True):
        if angular_width > numpy.pi:
            print("ERROR: Arc angle cannot be greater than PI! Physics calculations will not work correctly for this object!")
        self.drawing_start_angle = rotation_angle - angular_width / 2
        self.drawing_end_angle = rotation_angle + angular_width / 2
        self.physics_start_angle = self.drawing_start_angle
        self.physics_end_angle = self.drawing_end_angle
        self._constrain_physics_angles()

        self.center = center
        self.radius = radius
        self.is_reflective = is_reflective
        self.is_refractive = is_refractive

    def _constrain_physics_angles(self):
        # CONSTRAIN BETWEEN -PI, PI
        if self.physics_start_angle > numpy.pi:
            self.physics_start_angle -= 2 * numpy.pi
        elif self.physics_start_angle < -numpy.pi:
            self.physics_start_angle += 2 * numpy.pi

        if self.physics_end_angle > numpy.pi:
            self.physics_end_angle -= 2 * numpy.pi
        elif self.physics_end_angle < -numpy.pi:
            self.physics_end_angle += 2 * numpy.pi

    def get_intersection(self, ray) -> numpy.ndarray:  # TODO: optimize if necessary
        # Don't @ me...    https://en.wikipedia.org/wiki/Line-sphere_intersection#Calculation_using_vectors_in_3D
        temp_calculation1 = ray._direction @ (ray._origin - self.center)
        temp_calculation2 = numpy.linalg.norm(ray._origin - self.center)
        nabla = (temp_calculation1 * temp_calculation1) - (
            (temp_calculation2 * temp_calculation2) - self.radius * self.radius
        )
        if nabla < 0:
            return None

        nabla_sqrt = math.sqrt(nabla)
        intersection_distance1 = -nabla_sqrt - temp_calculation1
        intersection_distance2 = nabla_sqrt - temp_calculation1

        point1, point1_angle = None, None
        point2, point2_angle = None, None

        if intersection_distance1 > 0:
            point1 = ray._origin + intersection_distance1 * ray._direction
            point1_angle = math.atan2(point1[1] - self.center[1], point1[0] - self.center[0])
            if not ((self.physics_start_angle < point1_angle < self.physics_end_angle) or
                    (self.physics_start_angle < point1_angle and self.physics_end_angle < 0) or
                    (self.physics_end_angle > point1_angle and self.physics_start_angle > 0)):
                point1 = None
        if intersection_distance2 > 0:
            point2 = ray._origin + intersection_distance2 * ray._direction
            point2_angle = math.atan2(point2[1] - self.center[1], point2[0] - self.center[0])
            if not ((self.physics_start_angle < point2_angle < self.physics_end_angle) or
                    (self.physics_start_angle < point2_angle and self.physics_end_angle < 0) or
                    (self.physics_end_angle > point2_angle and self.physics_start_angle > 0)):
                point2 = None


        if point1 is None and point2 is None:
            return None
        if point1 is None:
            return point2
        if point2 is None:
            return point1

        if intersection_distance1 < intersection_distance2:
            return point1
        else:
            return point2

    def move(self, world_object_center, move_distance, rotate_angle=0):
        self.center = util.rotate_around_center(world_object_center, self.center, rotate_angle) + move_distance
        self.drawing_start_angle += rotate_angle
        self.drawing_end_angle += rotate_angle
        self.physics_start_angle += rotate_angle
        self.physics_end_angle += rotate_angle
        self._constrain_physics_angles()

    def draw(self):
        # arcade.draw_circle_outline(self.center[0], self.center[1], self.radius, arcade.color.MAGENTA)
        arcade.draw_arc_outline(
            self.center[0], self.center[1],
            2 * self.radius, 2 * self.radius,
            arcade.color.MAGENTA,
            self.drawing_start_angle * 180 / numpy.pi, self.drawing_end_angle * 180 / numpy.pi, border_width=2
        )

    def get_refracted_direction(self, ray, point: numpy.ndarray):
        # Determine normal
        normal: numpy.ndarray = (point - self.center) / self.radius
        # Determine whether coming into or out of shape
        dot = normal @ ray._direction

        if dot < 0:
            # Determine angle with normal
            angle = numpy.pi - math.acos(dot)
            print("coming in: " + str(angle))
            # Determine new angle
            new_angle = angle / util.INDEX_OF_REFRACTION
            if util.two_d_cross_product(ray._direction, normal) < 0:
                new_angle = -new_angle
            # Make vector with that angle
            return -util.rotate_around_center(numpy.zeros(2), normal, new_angle)

        else:
            # Determine angle with normal
            angle = numpy.pi - math.acos(-dot)
            print("going out: " + str(angle))
            # Determine new angle
            new_angle = angle * util.INDEX_OF_REFRACTION
            if util.two_d_cross_product(ray._direction, normal) > 0:
                new_angle = -new_angle
            # Make vector with that angle
            return util.rotate_around_center(numpy.zeros(2), normal, new_angle)
