import worldobjects
import arcade
import numpy
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

        self.level_objects = []
        self.level_light_sources = []
        self.load_level1()


    def on_draw(self):
        self.clear()
        for source in self.level_light_sources:
            source.move_to(self.mouse_position)
            source.cast_rays(self.level_objects)
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


        self.level_objects.append(
            #                 center position          width & height          rotation
            worldobjects.Wall(numpy.array([200, 200]), numpy.array([200, 50]), numpy.pi/8)
        )

        self.level_light_sources.append(
            #                        position                  rotation               spread of beam
            light.RadialLightSource(numpy.array([300, 500]),  numpy.array([0, -1]),  numpy.pi/4)
        )






def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()