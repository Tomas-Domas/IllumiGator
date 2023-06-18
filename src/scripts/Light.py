import arcade
import numpy
from util.util import distance_squared

# Light Source Constants
NUM_LIGHT_RAYS = 200

# Ray Casting Constants
MAX_STEPS: int = 100
MAX_DISTANCE: float = 1000
EPSILON: float = 0.5

class LightRay:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction
        self.end = origin + direction*50
        self.child_ray = None

    def calculate_collision(self, world_objects: list) -> tuple:
        min_distance = 100000  # arbitrary large number :)
        collision_object = None
        for wo in world_objects:
            intersection_point = wo.get_intersection_point(self)
            intersection_dist2 = distance_squared(self.origin, intersection_point)

    def draw(self):
        arcade.draw_line(self.origin[0], self.origin[1], self.end[0], self.end[1], arcade.color.WHITE)



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
            ray.calculate_collision(world_objects)

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
