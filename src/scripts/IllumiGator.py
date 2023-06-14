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
        self.game_state = 'menu'

    def on_draw(self):
        self.clear()
        if self.game_state == 'menu':
            draw_menu()
        elif self.game_state == 'game':
            arcade.draw_text('IN THE GAME STATE', windowConstants.get('WINDOW_WIDTH') // 2, windowConstants.get('WINDOW_HEIGHT') // 2,
                             arcade.color.WHITE, 48, anchor_x='center')
    
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