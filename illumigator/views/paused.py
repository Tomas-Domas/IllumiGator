import arcade

from illumigator.views.options import OptionsView
from illumigator import menus, util


class PausedView(arcade.View):
    def __init__(self, game_view, main_menu_view):
        super().__init__()
        self.main_menu_view = main_menu_view
        self.game_view = game_view
        self.menu_effect = util.load_sound("retro_blip.wav")
        self.menu_music = util.load_sound("Hina_Fallen_leaves.wav", streaming=True)
        self.menu_player = None
        self.effect_keys = (arcade.key.UP, arcade.key.DOWN,
                            arcade.key.W, arcade.key.S,
                            arcade.key.ESCAPE, arcade.key.ENTER)
        self.menu = menus.GenericMenu("PAUSED", ("RESUME", "RESTART", "OPTIONS", "QUIT TO MENU"), overlay=True)

    def on_draw(self):
        self.window.clear()
        self.game_view.on_draw()
        self.menu.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        scaled_effects_volume = util.EFFECTS_VOLUME * util.MASTER_VOLUME

        if symbol in self.effect_keys and scaled_effects_volume > 0:
            arcade.play_sound(self.menu_effect)

        if symbol == arcade.key.ESCAPE:
            self.menu_player = arcade.stop_sound(self.menu_player)
            self.window.show_view(self.game_view)
        if symbol == arcade.key.S or symbol == arcade.key.DOWN:
            self.menu.increment_selection()
        if symbol == arcade.key.W or symbol == arcade.key.UP:
            self.menu.decrement_selection()
        if symbol == arcade.key.ENTER:
            if self.menu.selection == 0:
                self.menu_player = arcade.stop_sound(self.menu_player)
                self.window.show_view(self.game_view)
            elif self.menu.selection == 1:
                self.menu_player = arcade.stop_sound(self.menu_player)
                self.game_view.reset_level()
                self.window.show_view(self.game_view)
            elif self.menu.selection == 2:
                self.menu_player = arcade.stop_sound(self.menu_player)
                options_view = OptionsView(self)
                self.window.show_view(options_view)
            elif self.menu.selection == 3:
                self.menu_player = arcade.stop_sound(self.menu_player)
                self.game_view.reset_level()
                self.window.show_view(self.main_menu_view)

    def on_show_view(self):
        scaled_music_volume = util.MUSIC_VOLUME * util.MASTER_VOLUME * 0.5

        if self.menu_player is None and scaled_music_volume > 0:
            self.menu_player = arcade.play_sound(self.menu_music, scaled_music_volume, looping=True)
