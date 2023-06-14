import random
import arcade
import numpy

from src.scripts.Shapes import Rectangle, Lens

# Arcade Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Ray Marching Demo"
BACKGROUND_COLOR = arcade.color.JET

# Random Generation Constants
NUM_RECTANGLES = 8
NUM_LIGHT_RAYS = 100

# Ray Marching Constants
MAXSTEPS = 30
MAXDISTANCE = 700
EPSILON = 0.5


class LightRay:
    def __init__(self, origin, direction, length):
        self.origin = origin
        self.direction = direction
        self.end = origin + length * direction

    def draw(self):
        arcade.draw_line(self.origin[0], self.origin[1], self.end[0], self.end[1], arcade.color.WHITE)


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.background_color = BACKGROUND_COLOR
        self.level_elements = []
        self.light_rays = []

        for _ in range(NUM_RECTANGLES):    #ADD A NUMBER OF RANDOM RECTANGLES
            position = numpy.array([random.randint(30, SCREEN_WIDTH - 30), random.randint(30, SCREEN_HEIGHT - 30)])
            dimensions = numpy.array([random.randint(10, 100), random.randint(10, 100)])
            self.level_elements.append(Rectangle(position, dimensions, 0))

        for l in range(NUM_LIGHT_RAYS): #ADD A NUMBER OF LIGHT RAYS
            angle = l * 2 * numpy.pi/NUM_LIGHT_RAYS
            position = numpy.array([SCREEN_WIDTH/2, SCREEN_HEIGHT/2])
            direction = numpy.array([numpy.cos(angle), numpy.sin(angle)])
            length, element = self.ray_march(position, direction)

            self.light_rays.append(LightRay(position, direction, length))

    # def on_update(self, delta_time):

    def on_draw(self):
        self.clear()
        for element in self.level_elements:
            element.draw()
        for ray in self.light_rays:
            ray.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        for ray in self.light_rays:
            position = numpy.array([float(x), float(y)])
            direction = ray.direction
            length, element = self.ray_march(position, direction)

            ray.origin = position
            ray.length = length
            ray.end = position + length * direction

    def ray_march(self, origin, direction):
        startPoint = origin.copy()
        distanceTotal = 0
        collision_element_index = 0
        for i in range(MAXSTEPS):
            min_dist = self.level_elements[0].sdf(startPoint)
            for element in self.level_elements:
                element_distance = element.sdf(startPoint)
                if min_dist > element_distance:
                    min_dist = element_distance
                    collision_element_index = i
            distanceTotal += min_dist
            startPoint += direction * min_dist

            if min_dist < EPSILON:
                return distanceTotal, collision_element_index
            elif distanceTotal > MAXDISTANCE:
                break

        return MAXDISTANCE, -1


def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
