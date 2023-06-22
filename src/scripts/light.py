import math
import arcade
import util.util as util

# Ray Casting Constants
MAX_DISTANCE: float = 1000
MAX_GENERATIONS: int = 5

# Light Source Constants
NUM_LIGHT_RAYS = 50


class LightRay:
    def __init__(self, origin, direction, generation=0):
        self.origin = origin
        self.direction = direction
        self.end = None
        self.child_ray = None
        self.generation = generation

    def cast_ray(self, world_objects: list):
        nearest_distance_squared = util.STARTING_DISTANCE_VALUE
        nearest_intersection_geometry = None
        for wo in world_objects:
            for segment in wo.geometry_segments:
                intersection_point = segment.get_intersection(self)
                if intersection_point is None:
                    continue

                intersection_dist_squared = util.distance_squared(self.origin, intersection_point)
                if intersection_dist_squared < nearest_distance_squared:
                    nearest_distance_squared = intersection_dist_squared
                    nearest_intersection_geometry = segment

        if nearest_intersection_geometry is None:
            self.end = self.origin + self.direction * util.MAX_RAY_DISTANCE
            self.child_ray = None
            return

        self.end = self.origin + self.direction * math.sqrt(nearest_distance_squared)

        if nearest_intersection_geometry.is_reflective and self.generation < MAX_GENERATIONS:  # if the ray hit a mirror, create child and cast it
            self.generate_child_ray(nearest_intersection_geometry.get_reflected_direction(self))
            self.child_ray.cast_ray(world_objects)
        else:
            self.child_ray = None

    def generate_child_ray(self, direction):
        if self.child_ray is None:
            self.child_ray = LightRay(self.end + direction * 0.001, direction, generation=self.generation+1)
        else:
            self.child_ray.origin = self.end + direction * 0.001
            self.child_ray.direction = direction

    def draw(self):
        arcade.draw_line(self.origin[0], self.origin[1], self.end[0], self.end[1], arcade.color.WHITE)
        if self.child_ray is not None:
            self.child_ray.draw()
