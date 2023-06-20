import arcade
from menus import draw_title_menu, InGameMenu
from util import util
import WorldObject
import numpy

class Level:
    def __init__(self, elem_list: list[WorldObject.WorldObject], name='default'):
        self.elem_list = elem_list
        self.name = name
    
    def draw(self):
        for elem in self.elem_list:
            elem.draw()

class Character:
    def __init__(self, sprite_path, scale_factor=1, image_width=128, image_height=128, center_x=util.WINDOW_WIDTH // 2, center_y=util.WINDOW_HEIGHT // 2, velocity=10):
        self.character_sprite = arcade.Sprite(sprite_path, scale_factor, image_width=image_width, image_height=image_height, center_x=center_x, center_y=center_y )
        self.velocity = velocity

    def draw(self):
        self.character_sprite.draw()

    @property
    def center_x(self):
        return self.center_x
    
    @center_x.setter
    def center_x(self, center_x):
        self.center_x = center_x
    
    @property 
    def center_y(self):
        return self.center_y

    @center_y.setter
    def center_y(self, center_y):
        self.center_y = center_y

class GameObject(arcade.Window):
    def __init__(self):
        super().__init__(util.WINDOW_WIDTH, util.WINDOW_HEIGHT, util.WINDOW_TITLE)
        self.background = None
        self.set_mouse_visible(False)
        arcade.set_background_color(arcade.color.SKY_BLUE)
        self.elem_list = None
        self.game_menu = None
        self.tile_map = None
        self.character = None
    
    def setup(self):
        self.game_state = 'menu'
        self.elem_list = [WorldObject.Rectangle(numpy.array([2.5, util.WINDOW_HEIGHT // 2]), numpy.array([5, util.WINDOW_HEIGHT]))]
        self.game_menu = InGameMenu()
        self.character = Character('sprite.png')

    def on_draw(self):
        self.clear()

        if self.game_state == 'menu':
            draw_title_menu()
        elif self.game_state == 'game' or self.game_state == 'paused':
            for elem in self.elem_list:
                elem.draw()
            self.character.draw()
            if self.game_state == 'paused':
                self.game_menu.draw()
    
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
            if key == arcade.key.DOWN:
                self.game_menu.increment_selection()
            if key == arcade.key.UP:
                self.game_menu.decrement_selection()
            if key == arcade.key.ENTER:
                if self.game_menu.selection == 0:
                    self.game_state = 'game'
                elif self.game_menu.selection == 1:
                    self.game_state = 'menu'

def main():
    window = GameObject()
    window.setup()
    arcade.run()

if __name__ == '__main__':
    main()
