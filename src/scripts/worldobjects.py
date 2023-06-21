import arcade
import numpy
import random
import util.util as util
import geometry
import light


# Light Source Constants
NUM_LIGHT_RAYS = 100


class WorldObject:
    sprite: arcade.Sprite
    geometry_segments: list[geometry.Geometry]

class Wall(WorldObject):
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
            geometry.Line(center_position - axis1 + axis2,   center_position + axis1 + axis2),
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



class LightSource:
    def __init__(self, position, direction, angular_spread):
        self.position = position
        self.direction = direction
        self.light_rays = []
        self.angular_spread = angular_spread

        angle = numpy.arctan2(direction[1], direction[0])

        for n in range(NUM_LIGHT_RAYS):
            ray_angle = (n/NUM_LIGHT_RAYS)*(angle-angular_spread/2) + (1 - n/NUM_LIGHT_RAYS)*(angle+angular_spread/2)
            ray_direction = numpy.array([numpy.cos(ray_angle), numpy.sin(ray_angle)])
            self.light_rays.append(light.LightRay(self.position, ray_direction))


    def cast_rays(self, world_objects):
        for ray in self.light_rays:
            ray.cast_ray(world_objects)


    def move_to(self, new_position):
        self.position[0] = new_position[0]
        self.position[1] = new_position[1]
        for ray in self.light_rays:
            ray.origin[0] = new_position[0]
            ray.origin[1] = new_position[1]


    def draw(self):
        for ray in self.light_rays:
            ray.draw()
        arcade.draw_circle_filled(self.position[0], self.position[1], 10, arcade.color.BLACK)