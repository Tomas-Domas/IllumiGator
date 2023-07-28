import arcade

from illumigator.views.controls import ControlsView
from illumigator.views.audio import AudioView
from illumigator import menus, util


class OptionsView(arcade.View):
    def __init__(self, paused_view):
        super().__init__()
        self.paused_view = paused_view
        self.menu_effect = util.load_sound("retro_blip.wav")
        self.menu_music = util.load_sound("Hina_Fallen_leaves.wav", streaming=True)
        self.menu_player = None
        self.effect_keys = (arcade.key.UP, arcade.key.DOWN,
                            arcade.key.W, arcade.key.S,
                            arcade.key.ESCAPE, arcade.key.ENTER)
        self.options_menu = menus.GenericMenu("OPTIONS", ("RETURN", "CONTROLS", "AUDIO", "FULLSCREEN"))

    def on_draw(self):
        self.window.clear()
        self.options_menu.draw()

    def on_update(self, delta_time: float):
        self.update_audio()

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
                controls_view = ControlsView()
                self.window.show_view(controls_view)
            elif self.options_menu.selection == 2:
                audio_view = AudioView()
                self.window.show_view(audio_view)
            elif self.options_menu.selection == 3:
                self.window.set_fullscreen(not self.window.fullscreen)

    def update_audio(self):
        scaled_music_volume = util.MUSIC_VOLUME * util.MASTER_VOLUME * 0.5  # damp loud audio
        is_playable = self.menu_player is None and self.paused_view.menu_player is None

        if is_playable and scaled_music_volume > 0:
            self.menu_player = arcade.play_sound(self.menu_music, scaled_music_volume, looping=True)
