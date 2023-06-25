import worldobjects
import arcade
import numpy
# import timeit
# import math
from illumigator.util import WINDOW_WIDTH, WINDOW_HEIGHT

# Arcade Constants
SCREEN_TITLE = "Ray Marching Demo"
BACKGROUND_COLOR = arcade.color.JET


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.mouse_position = numpy.array([WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2])
        self.background_color = BACKGROUND_COLOR

        self.load_level1()

    def on_draw(self):
        self.clear()
        for source in self.level_light_sources:
            source.cast_rays(self.level_objects)
            source.move(numpy.zeros(2), 0.03)
            source.draw()

        for wo in self.level_objects:
            wo.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_position[0] = x
        self.mouse_position[1] = y

    # ====================================================================================================
    # ==========================================     LEVELS     ==========================================
    # ====================================================================================================

    def load_level1(self):

        self.level_objects = [
            worldobjects.Wall(numpy.array([8, WINDOW_HEIGHT / 2]), numpy.array([80, 1]), numpy.pi / 2),
            worldobjects.Wall(numpy.array([WINDOW_WIDTH - 8, WINDOW_HEIGHT / 2]), numpy.array([80, 1]), numpy.pi / 2),
            worldobjects.Wall(numpy.array([WINDOW_WIDTH / 2, WINDOW_HEIGHT - 8]), numpy.array([80, 1]), numpy.pi),
            worldobjects.Wall(numpy.array([WINDOW_WIDTH / 2, 8]), numpy.array([80, 1]), numpy.pi),
            worldobjects.Mirror(numpy.array([WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2]), 0),
            worldobjects.LightReceiver(numpy.array([100, 100]), 0)
        ]

        self.level_light_sources = [
            worldobjects.RadialLightSource(numpy.array([WINDOW_WIDTH - 100, WINDOW_HEIGHT - 100]), 0, numpy.pi / 4)
        ]


def main():
    MyGame(WINDOW_WIDTH, WINDOW_HEIGHT, SCREEN_TITLE)
    arcade.run()

    # def op1(num):
    #     numpy.square(num)
    # def op2(num):
    #     num * num
    # print("op1 timems:\t", timeit.timeit(lambda: op1(123.123456789), number=1000000))
    # print("op2 timems:\t", timeit.timeit(lambda: op2(123.123456789), number=1000000))


if __name__ == "__main__":
    main()
