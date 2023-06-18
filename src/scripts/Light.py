import arcade
import numpy

# Light Source Constants
NUM_LIGHT_RAYS = 1

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

    def ray_march(self, level_elements):
        self.end[0], self.end[1] = self.origin[0], self.origin[1]
        distanceTotal = 0
        step = 0
        while True:
            min_dist = level_elements[0].distance_to_point(self.end)
            for element in level_elements[1:]:
                element_distance = element.distance_to_point(self.end)
                if min_dist > element_distance:
                    min_dist = element_distance
            distanceTotal += min_dist
            self.end += self.direction * min_dist

            step += 1
            if min_dist < EPSILON or step > MAX_STEPS:
                return distanceTotal
            elif distanceTotal > MAX_DISTANCE:
                return MAX_DISTANCE

    def draw(self):
        arcade.draw_line(self.origin[0], self.origin[1], self.end[0], self.end[1], arcade.color.WHITE)



class LightSource:
    def __init__(self, position, direction, angular_spread):
        self.position = position
        self.direction = direction
        self.light_rays = []
        self.angular_spread = angular_spread

        angle = numpy.arctan2(direction[1], direction[0])

        for l in range(NUM_LIGHT_RAYS):
            ray_angle = (l/NUM_LIGHT_RAYS)*(angle-angular_spread/2) + (1 - l/NUM_LIGHT_RAYS)*(angle+angular_spread/2)
            ray_direction = numpy.array([numpy.cos(ray_angle), numpy.sin(ray_angle)])
            self.light_rays.append(LightRay(self.position, ray_direction))

    def march_rays(self, level_elements):
        for ray in self.light_rays:
            ray.ray_march(level_elements)

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
        arcade.draw_circle_filled(self.position[0], self.position[1], 20, arcade.color.BLACK)
