import arcade
import math
import numpy

from illumigator import util


class LightRay:
    def __init__(self, origin, direction, generation=0):
        self._origin = origin
        self._direction = direction
        self._end = numpy.zeros(2)
        self._child_ray = None
        self._generation = generation

    def cast_ray(self, world_objects: list):
        nearest_distance_squared = util.STARTING_DISTANCE_VALUE
        nearest_intersection_worldobject = None
        nearest_intersection_geometry = None
        for wo in world_objects:
            for segment in wo._geometry_segments:
                intersection_point = segment.get_intersection(self)
                if intersection_point is None:
                    continue

                intersection_dist_squared = util.distance_squared(self._origin, intersection_point)
                if intersection_dist_squared < nearest_distance_squared:
                    nearest_distance_squared = intersection_dist_squared
                    nearest_intersection_worldobject = wo
                    nearest_intersection_geometry = segment

        if nearest_intersection_geometry is None:
            self._end = self._origin + self._direction * util.MAX_RAY_DISTANCE
            self._child_ray = None
            return

        self._end = self._origin + self._direction * math.sqrt(nearest_distance_squared)
        if nearest_intersection_worldobject._is_receiver:  # Charge receiver when a light ray hits it
            nearest_intersection_worldobject.charge += util.LIGHT_INCREMENT
        elif nearest_intersection_geometry.is_reflective and self._generation < util.MAX_GENERATIONS:  # if the ray hit a mirror, create child and cast it
            self._generate_child_ray(nearest_intersection_geometry.get_reflected_direction(self))
            self._child_ray.cast_ray(world_objects)
            return
        self._child_ray = None


    def _generate_child_ray(self, direction):
        if self._child_ray is None:
            self._child_ray = LightRay(self._end + direction * 0.001, direction, generation=self._generation + 1)
        else:
            self._child_ray._origin = self._end + direction * 0.001
            self._child_ray._direction = direction

    def draw(self):
        arcade.draw_line(self._origin[0], self._origin[1], self._end[0], self._end[1], arcade.color.WHITE)
        if self._child_ray is not None:
            self._child_ray.draw()
