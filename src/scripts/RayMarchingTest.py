import random
import arcade
import numpy
import WorldObject
import Light

# Arcade Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Ray Marching Demo"
BACKGROUND_COLOR = arcade.color.JET

# Random Generation Constants
NUM_RECTANGLES = 8


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.mouse_x = SCREEN_WIDTH / 2
        self.mouse_y = SCREEN_HEIGHT / 2
        self.background_color = BACKGROUND_COLOR
        self.world_objects = []
        self.light_sources = []

        for _ in range(NUM_RECTANGLES):  # ADD A NUMBER OF RANDOM RECTANGLES
            position = numpy.array([random.randint(30, SCREEN_WIDTH - 30), random.randint(30, SCREEN_HEIGHT - 30)])
            dimensions = numpy.array([random.randint(50, 200), random.randint(50, 200)])
            self.world_objects.append(WorldObject.Rectangle(position, dimensions, 0))

        self.light_sources.append(Light.LightSource(numpy.zeros(2), numpy.array([0.6, 0.8]), numpy.pi / 2))

    def on_draw(self):
        self.clear()
        for element in self.world_objects:
            element.draw()
        for source in self.light_sources:
            source.move_to(self.mouse_x, self.mouse_y)
            source.march_rays(self.world_objects)
            source.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y


def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
