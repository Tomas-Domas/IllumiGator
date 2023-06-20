import random
import arcade
import numpy
import geometry
import light

# Arcade Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Ray Marching Demo"
BACKGROUND_COLOR = arcade.color.JET

# Random Generation Constants
NUM_OBJECTS = 10


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.mouse_position = numpy.array([SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2])
        self.background_color = BACKGROUND_COLOR
        self.world_objects = []
        self.light_sources = []

        # for n in range(NUM_OBJECTS):  # add a bunch of random line segments
        #     position = numpy.array([random.randint(30, SCREEN_WIDTH - 30), random.randint(30, SCREEN_HEIGHT - 30)])
        #     dimensions = numpy.array([random.randint(-200, 200), random.randint(-200, 200)])
        #     if n <= 5:
        #         self.world_objects.append(WorldObject.Mirror(position, position + dimensions))
        #     else:
        #         self.world_objects.append(WorldObject.Line(position, position + dimensions))

        # for _ in range(0, 17):
        #     self.world_objects.append(WorldObject.Rectangle(numpy.array([40 + _*50, 200]), numpy.array([20, 50]), _*numpy.pi/16))

        self.world_objects.append(geometry.Circle(numpy.array([200, 200]), 50))

        self.light_sources.append(light.LightSource(numpy.zeros(2), numpy.array([0, -1]), numpy.pi/4))

    def on_draw(self):
        self.clear()
        for source in self.light_sources:
            source.move_to(self.mouse_position)
            source.cast_rays(self.world_objects)
            source.draw()

        for wo in self.world_objects:
            wo.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_position[0] = x
        self.mouse_position[1] = y


def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
