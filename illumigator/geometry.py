from abc import ABC, abstractmethod
import arcade
import numpy
import math

from illumigator import util


class Geometry(ABC):
    def __init__(self, is_reflective: bool, is_refractive: bool):
        self.is_reflective = is_reflective
        self.is_refractive = is_refractive

    @abstractmethod
    def draw(self):
        pass
    @abstractmethod
    def get_intersection(self, ray) -> tuple:
        pass
    @abstractmethod
    def move(self, world_object_center, move_distance, rotate_angle=0):
        pass

    @abstractmethod
    def scale(self, scale_factor):
        pass


class Line(Geometry):
    def __init__(self, point1: numpy.ndarray, point2: numpy.ndarray, is_reflective: bool = False, is_refractive: bool = False):
        super().__init__(is_reflective, is_refractive)
        self._point1 = point1
        self._point2 = point2

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

    def scale(self, scale_factor):
        self._point1 *= scale_factor
        self._point2 *= scale_factor

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
        super().__init__(is_reflective, is_refractive)
        self.center = center
        self.radius = radius

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

    def scale(self, scale_factor):
        self.center *= scale_factor
        self.radius *= scale_factor

    def draw(self):
        arcade.draw_circle_outline(
            self.center[0], self.center[1], self.radius, arcade.color.MAGENTA
        )


class Arc(Geometry):
    def __init__(self, center: numpy.ndarray, radius: float, rotation_angle: float, angular_width: float,
                 is_reflective: bool = False, is_refractive: bool = True):
        super().__init__(is_reflective, is_refractive)
        if angular_width > numpy.pi:
            raise ValueError("Arc angle cannot be greater than PI")
        self._drawing_start_angle = rotation_angle - angular_width / 2
        self._drawing_end_angle = rotation_angle + angular_width / 2
        self._physics_start_angle = self._drawing_start_angle
        self._physics_end_angle = self._drawing_end_angle
        self._constrain_physics_angles()

        self.center = center
        self.radius = radius
        self.is_reflective = is_reflective
        self.is_refractive = is_refractive

    def _constrain_physics_angles(self):  # Constrain between (-PI, PI)
        if self._physics_start_angle > numpy.pi:
            self._physics_start_angle -= 2 * numpy.pi
        elif self._physics_start_angle < -numpy.pi:
            self._physics_start_angle += 2 * numpy.pi

        if self._physics_end_angle > numpy.pi:
            self._physics_end_angle -= 2 * numpy.pi
        elif self._physics_end_angle < -numpy.pi:
            self._physics_end_angle += 2 * numpy.pi

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
            if not ((self._physics_start_angle < point1_angle < self._physics_end_angle) or
                    (self._physics_start_angle < point1_angle and self._physics_end_angle < 0) or
                    (self._physics_end_angle > point1_angle and self._physics_start_angle > 0)):
                point1 = None
        if intersection_distance2 > 0:
            point2 = ray._origin + intersection_distance2 * ray._direction
            point2_angle = math.atan2(point2[1] - self.center[1], point2[0] - self.center[0])
            if not ((self._physics_start_angle < point2_angle < self._physics_end_angle) or
                    (self._physics_start_angle < point2_angle and self._physics_end_angle < 0) or
                    (self._physics_end_angle > point2_angle and self._physics_start_angle > 0)):
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
        self._drawing_start_angle += rotate_angle
        self._drawing_end_angle += rotate_angle
        self._physics_start_angle += rotate_angle
        self._physics_end_angle += rotate_angle
        self._constrain_physics_angles()

    def scale(self, scale_factor):
        self.center *= scale_factor
        self.radius *= scale_factor

    def draw(self):
        arcade.draw_arc_outline(
            self.center[0], self.center[1],
            2 * self.radius, 2 * self.radius,
            arcade.color.MAGENTA,
            self._drawing_start_angle * 180 / numpy.pi, self._drawing_end_angle * 180 / numpy.pi, border_width=2
        )

    def get_refracted_direction(self, ray, point: numpy.ndarray):
        # Determine normal
        normal = (point - self.center) / self.radius
        # Determine whether coming into or out of shape
        dot_product = normal @ ray._direction

        if dot_product < 0:  # Ray is coming into the shape
            # Determine refraction angle with respect to normal
            angle = (numpy.pi - math.acos(dot_product)) / util.INDEX_OF_REFRACTION
            if util.two_d_cross_product(ray._direction, normal) < 0:
                angle = -angle
            # Create vector with new angle from normal
            return -util.rotate_around_center(numpy.zeros(2), normal, angle)

        else:  # Ray is going out of shape
            angle = (numpy.pi - math.acos(-dot_product)) * util.INDEX_OF_REFRACTION
            if util.two_d_cross_product(ray._direction, normal) > 0:
                angle = -angle
            return util.rotate_around_center(numpy.zeros(2), normal, angle)
