import arcade
import numpy
from WorldObject import Mirror
import util.util as util

# Light Source Constants
NUM_LIGHT_RAYS = 50

# Ray Casting Constants
MAX_DISTANCE: float = 1000
MAX_GENERATIONS: int = 10

class LightRay:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction
        self.end = None
        self.child_ray = None



    def cast_ray(self, world_objects: list, generation: int = 0):
        min_dist_squared = util.STARTING_DISTANCE_VALUE
        collision_object = None
        for wo in world_objects:
            intersection_point = wo.get_intersection_point(self)
            if intersection_point is None:
                continue

            intersection_dist_squared = util.distance_squared(self.origin, intersection_point)
            if intersection_dist_squared < min_dist_squared:
                min_dist_squared = intersection_dist_squared
                collision_object = wo

        if collision_object is None:
            self.end = self.origin + self.direction * 1000
            self.child_ray = None
            return

        self.end = self.origin + self.direction * numpy.sqrt(min_dist_squared)

        if isinstance(collision_object, Mirror) and generation < MAX_GENERATIONS:  # if the ray hit a mirror, create child and cast it
            reflected_direction = collision_object.get_reflected_direction(self.direction)
            self.child_ray = LightRay(self.end + reflected_direction*0.1, reflected_direction)
            self.child_ray.cast_ray(world_objects, generation=generation+1)
        else:
            self.child_ray = None



    def draw(self):
        arcade.draw_line(self.origin[0], self.origin[1], self.end[0], self.end[1], arcade.color.WHITE)
        if self.child_ray is not None:
            self.child_ray.draw()



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
            self.light_rays.append(LightRay(self.position, ray_direction))

    def cast_rays(self, world_objects):
        for ray in self.light_rays:
            ray.cast_ray(world_objects)



    def move_to(self, new_position):
        self.position[0] = new_position[0]
        self.position[1] = new_position[1]
        for ray in self.light_rays:
            ray.origin[0] = new_position[0]
            ray.origin[1] = new_position[1]
            ray.end = ray.origin + ray.direction*1000

    def draw(self):
        for ray in self.light_rays:
            ray.draw()
        arcade.draw_circle_filled(self.position[0], self.position[1], 10, arcade.color.BLACK)
