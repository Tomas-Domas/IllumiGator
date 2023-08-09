import arcade

from illumigator import menus


class ControlsView(arcade.View):
    def __init__(self, options_view):
        super().__init__()
        self.options_view = options_view
        self.menu = menus.ControlsMenu()

    def on_draw(self):
        self.window.clear()
        self.menu.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            self.window.show_view(self.options_view)
