import arcade

from illumigator import util, level_selector


class OfficialView(arcade.View):
    def __init__(self, main_menu_view):
        super().__init__()
        self.main_menu_view = main_menu_view
        arcade.text_pyglet.load_font(util.ENVIRON_ASSETS_PATH + "PressStart2P-Regular.ttf")
        self.menu = level_selector.LevelSelector()

    def on_draw(self):
        self.window.clear()
        self.menu.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.D or symbol == arcade.key.RIGHT:
            self.menu.selection += 1
        if symbol == arcade.key.A or symbol == arcade.key.LEFT:
            self.menu.selection -= 1
        if symbol == arcade.key.W or symbol == arcade.key.UP:
            self.menu.selection -= 5
        if symbol == arcade.key.S or symbol == arcade.key.DOWN:
            self.menu.selection += 5
        if symbol == arcade.key.ESCAPE:
            self.window.show_view(self.main_menu_view)
        if symbol == arcade.key.ENTER:
            util.OFFICIAL_LEVEL_STATUS = True
            util.CURRENT_LEVEL_PATH = self.menu.get_selection()
            util.CURRENT_LEVEL = self.menu.selection + 1
            self.window.show_view(self.main_menu_view.game_view)
