import worldobjects
import arcade
import numpy
# import timeit
# import math

# Arcade Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Ray Marching Demo"
BACKGROUND_COLOR = arcade.color.JET


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.mouse_position = numpy.array([SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2])
        self.background_color = BACKGROUND_COLOR

        self.level_objects = []
        self.level_light_sources = []
        self.load_level1()


    def on_draw(self):
        self.clear()
        for source in self.level_light_sources:
            # source.calculate_light_ray_positions()
            source.cast_rays(self.level_objects)
            source.draw()

        for wo in self.level_objects:
            wo.move(numpy.array([1, 0]))
            wo.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_position[0] = x
        self.mouse_position[1] = y


    # ====================================================================================================
    # ==========================================     LEVELS     ==========================================
    # ====================================================================================================

    def load_level1(self):

        self.level_objects.append(
            #                   center position          width & height          rotation
            worldobjects.Wall(numpy.array([500, 300]), numpy.array([3, 8]), numpy.pi/2, "../../assets/wall.png", 1, 16, 16),
        )

        # self.level_light_sources.append(
        #     #                              position                  rotation   spread of beam
        #     worldobjects.RadialLightSource(numpy.array([10, 10]),  numpy.pi,  numpy.pi*2)
        # )

def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()

    # def op1(num):
    #     numpy.square(num)
    # def op2(num):
    #     num * num
    # print("op1 timems:\t", timeit.timeit(lambda: op1(123.123456789), number=1000000))
    # print("op2 timems:\t", timeit.timeit(lambda: op2(123.123456789), number=1000000))


if __name__ == "__main__":
    main()

