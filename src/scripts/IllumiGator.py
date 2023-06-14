import arcade
from menus import draw_menu
from util import util
import Shapes
import numpy

windowConstants = util.get_constants()

class GameObject(arcade.Window):
    def __init__(self):
        super().__init__(windowConstants.get('WINDOW_WIDTH'), windowConstants.get('WINDOW_HEIGHT'), windowConstants.get('WINDOW_TITLE'))
        self.background = None
        self.set_mouse_visible(False)
        arcade.set_background_color(arcade.color.SKY_BLUE)
        self.elem_list = None
    
    def setup(self):
        self.game_state = 'menu'
        self.elem_list = [Shapes.Rectangle(numpy.array([2.5, windowConstants.get('WINDOW_HEIGHT') // 2]), numpy.array([5, windowConstants.get('WINDOW_HEIGHT')]))]

    def on_draw(self):
        self.clear()

        if self.game_state == 'menu':
            draw_menu()
        elif self.game_state == 'game':
            for elem in self.elem_list:
                elem.draw()
    
    def on_key_press(self, key, key_modifiers):
        if self.game_state == 'menu':
            if key == arcade.key.ENTER:
                self.game_state = 'game'
            if key == arcade.key.ESCAPE:
                arcade.close_window()

def main():
    window = GameObject()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()