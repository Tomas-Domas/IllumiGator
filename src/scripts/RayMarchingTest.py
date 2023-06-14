import arcade
import random
import numpy

from src.scripts.Shapes import Rectangle, Lens

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Ray Marching Demo"
BACKGROUND_COLOR = arcade.color.JET


class LightRay:
    def __init__(self, origin, direction, length):
        self.origin = origin
        self.end = origin + length*direction
        self.direction = direction

    def draw(self):
        arcade.draw_line(self.origin[0], self.origin[1], self.end[0], self.end[1], arcade.color.WHITE)


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.background_color = BACKGROUND_COLOR
        self.level_elements = []

        # for _ in range(1):    #ADD A NUMBER OF RANDOM RECTANGLES
        #     position = numpy.array([random.randint(30, SCREEN_WIDTH - 30), random.randint(30, SCREEN_HEIGHT - 30)])
        #     dimensions = numpy.array([random.randint(10, 100), random.randint(10, 100)])
        #     self.level_elements.append(Rectangle(position, dimensions, 0))

        self.level_elements.append(Lens( numpy.array([100, 100]), numpy.array([300, 300]), 100 ))

    # def on_update(self, delta_time):

    def on_mouse_motion(self, x, y, dx, dy):
        lens = self.level_elements[0]
        print(lens.sdf(numpy.array([x, y])))

    def on_draw(self):
        self.clear()
        for element in self.level_elements:
            element.draw()


def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
