import arcade

from illumigator.views.controls import ControlsView
from illumigator.views.audio import AudioView
from illumigator import menus, util


class OptionsView(arcade.View):
    def __init__(self, paused_view):
        super().__init__()
        self.paused_view = paused_view
        self.menu_effect = util.load_sound("retro_blip.wav")
        self.effect_keys = (arcade.key.UP, arcade.key.DOWN,
                            arcade.key.W, arcade.key.S,
                            arcade.key.ESCAPE, arcade.key.ENTER)
        self.options_menu = menus.GenericMenu("OPTIONS", ("RETURN", "CONTROLS", "AUDIO", "FULLSCREEN"))

    def on_draw(self):
        self.window.clear()
        self.options_menu.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        scaled_effects_volume = util.EFFECTS_VOLUME * util.MASTER_VOLUME

        if symbol in self.effect_keys and scaled_effects_volume > 0:
            arcade.play_sound(self.menu_effect)

        if symbol == arcade.key.ESCAPE:
            self.window.show_view(self.paused_view)
        if symbol == arcade.key.S or symbol == arcade.key.DOWN:
            self.options_menu.increment_selection()
        if symbol == arcade.key.W or symbol == arcade.key.UP:
            self.options_menu.decrement_selection()
        if symbol == arcade.key.ENTER:
            if self.options_menu.selection == 0:
                self.window.show_view(self.paused_view)
            elif self.options_menu.selection == 1:
                controls_view = ControlsView(self)
                self.window.show_view(controls_view)
            elif self.options_menu.selection == 2:
                audio_view = AudioView(self)
                self.window.show_view(audio_view)
            elif self.options_menu.selection == 3:
                self.window.set_fullscreen(not self.window.fullscreen)
