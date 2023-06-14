import random
import arcade
import numpy
from src.scripts.Shapes import Rectangle, LightRay

# Arcade Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Ray Marching Demo"
BACKGROUND_COLOR = arcade.color.JET

# Random Generation Constants
NUM_RECTANGLES = 8
NUM_LIGHT_RAYS = 200

# Ray Marching Constants
MAXSTEPS = 30
MAXDISTANCE = 1000
EPSILON = 1

class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.mouse_x = SCREEN_WIDTH/2
        self.mouse_y = SCREEN_HEIGHT/2
        self.background_color = BACKGROUND_COLOR
        self.level_elements = []
        self.light_rays = []

        for _ in range(NUM_RECTANGLES):    #ADD A NUMBER OF RANDOM RECTANGLES
            position = numpy.array([random.randint(30, SCREEN_WIDTH - 30), random.randint(30, SCREEN_HEIGHT - 30)])
            dimensions = numpy.array([random.randint(50, 200), random.randint(50, 200)])
            self.level_elements.append(Rectangle(position, dimensions, 0))

        for l in range(NUM_LIGHT_RAYS): #ADD A NUMBER OF LIGHT RAYS
            angle = l * 2 * numpy.pi/NUM_LIGHT_RAYS
            position = numpy.array([SCREEN_WIDTH/2, SCREEN_HEIGHT/2])
            direction = numpy.array([numpy.cos(angle), numpy.sin(angle)])
            length = self.ray_march(position, direction)

            self.light_rays.append(LightRay(position, direction, length))

    # def on_update(self, delta_time):

    def on_draw(self):
        self.clear()
        for element in self.level_elements:
            element.draw()
        for ray in self.light_rays:
            position = numpy.array([float(self.mouse_x), float(self.mouse_y)])
            direction = ray.direction
            length = self.ray_march(position, direction)

            ray.origin = position
            ray.length = length
            ray.end = position + length * direction
            ray.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y


    def ray_march(self, origin, direction):
        startPoint = origin.copy()
        distanceTotal = 0
        for s in range(MAXSTEPS):
            min_dist = self.level_elements[0].sdf(startPoint)
            for element in self.level_elements:
                element_distance = element.sdf(startPoint)
                if min_dist > element_distance:
                    min_dist = element_distance
            distanceTotal += min_dist
            startPoint += direction * min_dist

            if min_dist < EPSILON:
                return distanceTotal
            elif distanceTotal > MAXDISTANCE:
                break

        return MAXDISTANCE


def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
