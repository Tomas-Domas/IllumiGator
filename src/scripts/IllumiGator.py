import arcade
from menus import draw_menu
from util import util

windowConstants = util.get_constants()

class GameObject(arcade.Window):
    def __init__(self):
        super().__init__(windowConstants.get('WINDOW_WIDTH'), windowConstants.get('WINDOW_HEIGHT'), windowConstants.get('WINDOW_TITLE'))
        self.set_mouse_visible(False)
        arcade.set_background_color(arcade.color.SKY_BLUE)
    
    def setup(self):
        pass

    def on_draw(self):
        self.clear()
        draw_menu()


def main():
    window = GameObject()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()