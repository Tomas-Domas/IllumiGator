import arcade
import numpy
import geometry
import util.util as util

# Ray Casting Constants
MAX_DISTANCE: float = 1000
MAX_GENERATIONS: int = 10

class LightRay:
    def __init__(self, origin, direction, generation=0):
        self.origin = origin
        self.direction = direction
        self.end = None
        self.child_ray = None
        self.generation = generation

    def cast_ray(self, world_objects: list[geometry.Geometry]):
        nearest_distance_squared = util.STARTING_DISTANCE_VALUE
        nearest_intersection_object: geometry.Geometry = None
        for wo in world_objects:
            intersection_point, intersection_object = wo.get_intersection(self)
            if intersection_point is None:
                continue

            intersection_dist_squared = util.distance_squared(self.origin, intersection_point)
            if intersection_dist_squared < nearest_distance_squared:
                nearest_distance_squared = intersection_dist_squared
                nearest_intersection_object = intersection_object

        if nearest_intersection_object is None:
            self.end = self.origin + self.direction * util.MAX_RAY_DISTANCE
            self.child_ray = None
            return

        self.end = self.origin + self.direction * numpy.sqrt(nearest_distance_squared)

        if nearest_intersection_object.is_reflective and self.generation < MAX_GENERATIONS:  # if the ray hit a mirror, create child and cast it
            self.generate_child_ray(nearest_intersection_object.get_reflected_direction(self.direction))
            self.child_ray.cast_ray(world_objects)
        else:
            self.child_ray = None

    def generate_child_ray(self, direction):
        if self.child_ray is None:
            self.child_ray = LightRay(self.end + direction * 0.1, direction, generation=self.generation+1)
        else:
            self.child_ray.origin = self.end + direction * 0.1
            self.child_ray.direction = direction

    def draw(self):
        arcade.draw_line(self.origin[0], self.origin[1], self.end[0], self.end[1], arcade.color.WHITE)
        if self.child_ray is not None:
            self.child_ray.draw()
