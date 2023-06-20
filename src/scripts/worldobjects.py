import numpy
import random
import util.util as util
import geometry

class Wall:
    def __init__(self, center_position: numpy.array, side_lengths: numpy.array,
                 rotation_angle: float = 0, color: tuple[int, int, int] = random.choice(util.COLORS)):
        self.center = center_position
        self.rotation_angle = rotation_angle
        self.color = color
        self.side_lengths = side_lengths

        axis1 = side_lengths[0] * 0.5 * numpy.array([
            numpy.cos(rotation_angle), numpy.sin(rotation_angle)
        ])
        axis2 = side_lengths[1] * 0.5 * numpy.array([
            -numpy.sin(rotation_angle), numpy.cos(rotation_angle)
        ])
        self.geometry_elements = [
            geometry.Line(center_position - axis1 - axis2,   center_position - axis1 + axis2),
            geometry.Line(center_position - axis1 + axis2,   center_position + axis1 + axis2, is_reflective=True),
            geometry.Line(center_position + axis1 + axis2,   center_position + axis1 - axis2),
            geometry.Line(center_position + axis1 - axis2,   center_position - axis1 - axis2),
        ]

    def draw(self):
        # arcade.draw_rectangle_filled(self.center[0], self.center[1], self.side_lengths[0], self.side_lengths[1],
        #                              self.color, tilt_angle=util.convert_angle_for_arcade(self.rotation_angle))
        for edge in self.geometry_elements:
            edge.draw()

    def get_intersection(self, ray) -> tuple[numpy.array, geometry.Geometry]:
        nearest_distance_squared = util.STARTING_DISTANCE_VALUE
        nearest_intersection_object = None
        nearest_intersection_point = None
        for edge in self.geometry_elements:
            intersection_point, intersection_object = edge.get_intersection(ray)
            if intersection_point is None:
                continue

            intersection_dist_squared = util.distance_squared(ray.origin, intersection_point)
            if intersection_dist_squared < nearest_distance_squared:
                nearest_distance_squared = intersection_dist_squared
                nearest_intersection_point = intersection_point
                nearest_intersection_object = intersection_object

        return nearest_intersection_point, nearest_intersection_object

