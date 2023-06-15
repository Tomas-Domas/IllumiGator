import arcade
from menus import draw_ingame_menu, draw_title_menu
from util import util
import Shapes
import numpy

class GameObject(arcade.Window):
    def __init__(self):
        super().__init__(util.WINDOW_WIDTH, util.WINDOW_HEIGHT, util.WINDOW_TITLE)
        self.background = None
        self.set_mouse_visible(False)
        arcade.set_background_color(arcade.color.SKY_BLUE)
        self.elem_list = None
    
    def setup(self):
        self.game_state = 'menu'
        self.elem_list = [Shapes.Rectangle(numpy.array([2.5, util.WINDOW_HEIGHT // 2]), numpy.array([5, util.WINDOW_HEIGHT]))]

    def on_draw(self):
        self.clear()
        print(self.game_state)

        if self.game_state == 'menu':
            draw_title_menu()
        elif self.game_state == 'game' or self.game_state == 'paused':
            for elem in self.elem_list:
                elem.draw()
            if self.game_state == 'paused':
                draw_ingame_menu()
    
    def on_key_press(self, key, key_modifiers):
        if self.game_state == 'menu':
            if key == arcade.key.ENTER:
                self.game_state = 'game'
            if key == arcade.key.ESCAPE:
                arcade.close_window()

        elif self.game_state == 'game':
            if key == arcade.key.ESCAPE:
                self.game_state = 'paused'

        elif self.game_state == 'paused':
            if key == arcade.key.ESCAPE:
                self.game_state = 'game'

def main():
    window = GameObject()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()