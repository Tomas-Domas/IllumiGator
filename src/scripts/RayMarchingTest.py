import arcade
import random
import numpy

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Ray Marching Demo"

COLORS = [arcade.color.LION, arcade.color.BLUE, arcade.color.RED, arcade.color.GREEN,
          arcade.color.PURPLE, arcade.color.PINK, arcade.color.AMBER, arcade.color.ORANGE]
BACKGROUND_COLOR = arcade.color.JET


class Rectangle:
    def __init__(self, x, y, w, h):
        self.position = numpy.array([x, y])
        self.size = numpy.array([w, h])
        self.color = random.choice(COLORS)

    def draw(self):
        # Draw the rectangle
        arcade.draw_rectangle_filled(self.position[0], self.position[1], self.size[0], self.size[1], self.color)

    def sdf(self, point):
        distanceDifference = numpy.abs(point - self.position) - (self.size/2)
        outsideDistance = numpy.linalg.norm( numpy.maximum(distanceDifference, numpy.zeros(2)) )
        insideDistance = min(max(distanceDifference[0], distanceDifference[1]), 0)
        return outsideDistance + insideDistance


class LightRay:
    def __init__(self, origin, direction):
        self.origin = origin
        self.end = origin + 10*direction
        self.direction = direction

    def draw(self):
        arcade.draw_line(self.origin[0], self.origin[1], self.end[0], self.end[1], arcade.color.WHITE)


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.background_color = BACKGROUND_COLOR
        self.elements = [
            Rectangle(random.randint(30, SCREEN_WIDTH - 30), random.randint(30, SCREEN_HEIGHT - 30),
                      random.randint(10, 100), random.randint(10, 100))
            for _ in range(1)
        ]

        NUM_OF_RAYS = 1
        self.light_rays = self.elements = [
            Rectangle(random.randint(30, SCREEN_WIDTH-30), random.randint(30, SCREEN_HEIGHT-30), random.randint(10,100), random.randint(10, 100))
            for _ in range(NUM_OF_RAYS)
        ]


    # def on_update(self, delta_time):

    def on_mouse_motion(self, x, y, dx, dy):
        print(self.elements[0].sdf(numpy.array([x, y])))

    def on_draw(self):
        self.clear()
        for elem in self.elements:
            elem.draw()


def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
