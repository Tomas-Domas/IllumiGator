import arcade

from illumigator import menus, util


class WinView(arcade.View):
    def __init__(self, game_view, main_menu_view):
        super().__init__()
        self.game_view = game_view
        self.main_menu_view = main_menu_view
        self.win_menu = menus.GenericMenu("LEVEL COMPLETED", ("CONTINUE", "RETRY", "QUIT TO MENU"))

    def on_draw(self):
        self.win_menu.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.S or symbol == arcade.key.DOWN:
            self.win_menu.increment_selection()
        if symbol == arcade.key.W or symbol == arcade.key.UP:
            self.win_menu.decrement_selection()
        if symbol == arcade.key.ENTER:
            selection = self.win_menu.selection
            if selection == 0:
                self.window.show_view(self.game_view)
            elif selection == 1:
                util.CURRENT_LEVEL -= 1
                util.CURRENT_LEVEL_PATH = "level_" + str(util.CURRENT_LEVEL) + ".json"
                self.game_view.reset_level()
                self.window.show_view(self.game_view)
            elif selection == 2:
                self.window.show_view(self.main_menu_view)
