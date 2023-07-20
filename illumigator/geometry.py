from abc import ABC, abstractmethod
import arcade
import numpy
import math

from illumigator import util


class Geometry(ABC):
    def __init__(self, parent_object, is_reflective: bool, is_refractive: bool, is_receiver: bool):
        self.parent_object = parent_object
        self.is_reflective = is_reflective
        self.is_refractive = is_refractive
        self.is_receiver = is_receiver

    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def move(self, world_object_center, move_distance, rotate_angle=0):
        pass


class Line(Geometry):
    def __init__(
        self,
        parent_object,
        point1: numpy.ndarray,
        point2: numpy.ndarray,
        is_reflective: bool = False,
        is_refractive: bool = False,
        is_receiver: bool = False
    ):
        super().__init__(parent_object, is_reflective, is_refractive, is_receiver)
        self._point1 = point1
        self._point2 = point2
        self._length = numpy.linalg.norm(point2 - point1)

    def move(self, world_object_center, move_distance, rotate_angle=0):
        self._point1 = (
            util.rotate_around_center(world_object_center, self._point1, rotate_angle)
            + move_distance
        )
        self._point2 = (
            util.rotate_around_center(world_object_center, self._point2, rotate_angle)
            + move_distance
        )
        self.calculate_normal()

    def calculate_normal(self):
        normal_unscaled = numpy.array(
            [-(self._point2[1] - self._point1[1]), self._point2[0] - self._point1[0]]
        )
        self._normal = normal_unscaled / numpy.linalg.norm(normal_unscaled)

    def get_reflected_direction(self, ray):
        return ray._direction - (2 * self._normal * (self._normal @ ray._direction))

    def draw(self):
        if self.is_reflective:
            arcade.draw_line(
                self._point1[0],
                self._point1[1],
                self._point2[0],
                self._point2[1],
                arcade.color.WHITE,
            )
        else:
            arcade.draw_line(
                self._point1[0],
                self._point1[1],
                self._point2[0],
                self._point2[1],
                arcade.color.BLUE,
            )


class Circle(Geometry):
    def __init__(
        self,
        parent_object,
        center: numpy.ndarray,
        radius: float,
        is_reflective: bool = False,
        is_refractive: bool = False,
        is_receiver: bool = False
    ):
        super().__init__(parent_object, is_reflective, is_refractive, is_receiver)
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
            return ray._origin + ray._direction * min(
                intersection_distance1, intersection_distance2
            )
        elif intersection_distance1 > 0 or intersection_distance2 > 0:
            return ray._origin + ray._direction * max(
                intersection_distance1, intersection_distance2
            )
        else:
            return None

    def move(self, world_object_center, move_distance, rotate_angle=0):
        self.center = (
            util.rotate_around_center(world_object_center, self.center, rotate_angle)
            + move_distance
        )

    def draw(self):
        arcade.draw_circle_outline(
            self.center[0], self.center[1], self.radius, arcade.color.MAGENTA
        )


class Arc(Geometry):
    def __init__(
        self,
        parent_object,
        center: numpy.ndarray,
        radius: float,
        rotation_angle: float,
        angular_width: float,
        is_reflective: bool = False,
        is_refractive: bool = True,
        is_receiver: bool = False
    ):
        super().__init__(parent_object, is_reflective, is_refractive, is_receiver)
        if angular_width > numpy.pi:
            raise ValueError("Arc angle cannot be greater than PI")
        self._start_angle = rotation_angle - angular_width / 2
        self._end_angle = rotation_angle + angular_width / 2
        self._constrain_angles()

        self.center = center
        self.radius = radius
        self.is_reflective = is_reflective
        self.is_refractive = is_refractive

    def _constrain_angles(self):  # Constrain between (-PI, PI)
        if self._start_angle > numpy.pi:
            self._start_angle -= 2 * numpy.pi
        elif self._start_angle < -numpy.pi:
            self._start_angle += 2 * numpy.pi

        if self._end_angle > numpy.pi:
            self._end_angle -= 2 * numpy.pi
        elif self._end_angle < -numpy.pi:
            self._end_angle += 2 * numpy.pi

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

        point1: numpy.ndarray = None
        point2: numpy.ndarray = None
        point1_angle, point2_angle = None, None

        if intersection_distance1 > 0:
            point1 = ray._origin + intersection_distance1 * ray._direction
            point1_angle = math.atan2(
                point1[1] - self.center[1], point1[0] - self.center[0]
            )
            if not (
                (self._start_angle < point1_angle < self._end_angle) or (
                    self._end_angle < self._start_angle and (
                        0 <= self._start_angle <= point1_angle
                        or point1_angle <= self._end_angle <= 0
                    )
                )
            ):
                point1 = None
        if intersection_distance2 > 0:
            point2 = ray._origin + intersection_distance2 * ray._direction
            point2_angle = math.atan2(
                point2[1] - self.center[1], point2[0] - self.center[0]
            )
            if not (
                (self._start_angle < point2_angle < self._end_angle)
                or (
                    self._end_angle < self._start_angle
                    and (
                        0 <= self._start_angle <= point2_angle
                        or point2_angle <= self._end_angle <= 0
                    )
                )
            ):
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
        self.center = (
            util.rotate_around_center(world_object_center, self.center, rotate_angle)
            + move_distance
        )
        self._start_angle += rotate_angle
        self._end_angle += rotate_angle
        self._start_angle += rotate_angle
        self._end_angle += rotate_angle
        self._constrain_angles()

    def draw(self):
        if self._start_angle < self._end_angle:
            arcade.draw_arc_outline(
                self.center[0],
                self.center[1],
                2 * self.radius,
                2 * self.radius,
                arcade.color.MAGENTA,
                self._start_angle * 180 / numpy.pi,
                self._end_angle * 180 / numpy.pi,
                border_width=3,
                num_segments=512,
            )
        else:
            arcade.draw_arc_outline(
                self.center[0],
                self.center[1],
                2 * self.radius,
                2 * self.radius,
                arcade.color.MAGENTA,
                self._start_angle * 180 / numpy.pi,
                self._end_angle * 180 / numpy.pi + 360,
                border_width=3,
                num_segments=512,
            )

    def get_refracted_direction(self, ray):
        # Determine normal
        normal = (ray._end - self.center) / self.radius
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
