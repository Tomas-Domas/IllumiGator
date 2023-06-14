import arcade
from menus import draw_menu
from util import util

windowConstants = util.get_constants()

class GameObject(arcade.Window):
    def __init__(self):
        super().__init__(windowConstants.get('WINDOW_WIDTH'), windowConstants.get('WINDOW_HEIGHT'), windowConstants.get('WINDOW_TITLE'))
        self.background = None
        self.set_mouse_visible(False)
        arcade.set_background_color(arcade.color.SKY_BLUE)
        self.player_list = None

    def setup(self):
        self.game_state = 'menu'

        background_path = ':resources:../../../../../assets/background.jpg'
        self.background = arcade.load_texture(background_path)

        # Boiler-plate sprite code
        self.player_list = arcade.SpriteList()
        gator_path = ':resources:../../../../../assets/gator.png'
        self.gator_sprite = arcade.Sprite(gator_path, 1)
        self.gator_sprite.center_x = windowConstants.get('WINDOW_WIDTH') // 2
        self.gator_sprite.center_y = windowConstants.get('WINDOW_HEIGHT') // 2
        self.player_list.append(self.gator_sprite)

    def on_draw(self):
        self.clear()

        if self.game_state == 'menu':
            draw_menu()
        elif self.game_state == 'game':
            arcade.draw_lrwh_rectangle_textured(0, 0,
                                                util.WINDOW_WIDTH, util.WINDOW_HEIGHT,
                                                self.background)
            self.player_list.draw()
    
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