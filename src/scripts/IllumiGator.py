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


class GameObject(arcade.Window):
    def __init__(self):
        super().__init__(util.WINDOW_WIDTH, util.WINDOW_HEIGHT, util.WINDOW_TITLE)
        self.background = None
        self.set_mouse_visible(False)
        arcade.set_background_color(arcade.color.SKY_BLUE)
        self.elem_list = None
        self.game_menu = None
        self.tile_map = None
        self.character_sprite = None
        # self.scene = None
    
    def setup(self):
        self.game_state = 'menu'
        self.elem_list = [WorldObject.Rectangle(numpy.array([2.5, util.WINDOW_HEIGHT // 2]), numpy.array([5, util.WINDOW_HEIGHT]))]
        self.game_menu = InGameMenu()
        self.character_sprite = arcade.Sprite('sprite.png', 1, image_width=128, image_height=128, center_x=util.WINDOW_WIDTH // 2, center_y=util.WINDOW_HEIGHT // 2)

        # map_name = 'test-map.json'

        # layer_options = {
        #     "Platforms": {
        #         "use_spatial_hash": True,
        #     },
        # }

        # # Read in the tiled map
        # self.tile_map = arcade.load_tilemap(map_name, 1, layer_options)

        # # Initialize Scene with TileMap
        # self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # if self.tile_map.background_color:
        #     arcade.set_background_color(self.tile_map.background_color)

    def on_draw(self):
        self.clear()

        if self.game_state == 'menu':
            draw_title_menu()
        elif self.game_state == 'game' or self.game_state == 'paused':
            for elem in self.elem_list:
                elem.draw()
            self.character_sprite.draw()
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
