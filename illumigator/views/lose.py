import arcade

from illumigator import menus, util


class LoseView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.menu = menus.GenericMenu("YOU DIED", ("RETRY", "QUIT TO MENU"))
        self.menu_effect = util.load_sound("retro_blip.wav")
        self.effect_keys = (arcade.key.UP, arcade.key.DOWN,
                            arcade.key.W, arcade.key.S,
                            arcade.key.ENTER)

    def on_draw(self):
        self.window.clear()
        self.menu.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        scaled_effects_volume = util.EFFECTS_VOLUME * util.MASTER_VOLUME

        if symbol in self.effect_keys and scaled_effects_volume > 0:
            arcade.play_sound(self.menu_effect)

        if symbol == arcade.key.S or symbol == arcade.key.DOWN:
            self.menu.increment_selection()
        if symbol == arcade.key.W or symbol == arcade.key.UP:
            self.menu.decrement_selection()
        if symbol == arcade.key.ENTER:
            if self.menu.selection == 0:
                self.game_view.reset_level()
                self.window.show_view(self.game_view)
            elif self.menu.selection == 1:
                self.game_view.reset_level()
                self.window.show_view(self.game_view.main_menu_view)
