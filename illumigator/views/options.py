import arcade

from paused import PausedView
from controls import ControlsView
from audio import AudioView
from illumigator import menus, util


class OptionsView(arcade.View):
    def __init__(self):
        super().__init__()
        self.menu_player = None
        self.options_menu = menus.GenericMenu("OPTIONS", ("RETURN", "CONTROLS", "AUDIO", "FULLSCREEN"))
        self.effect_keys = (arcade.key.UP, arcade.key.LEFT, arcade.key.RIGHT, arcade.key.UP,
                            arcade.key.W, arcade.key.A, arcade.key.D, arcade.key.S,
                            arcade.key.ESCAPE, arcade.key.ENTER)
        self.menu_sound = util.load_sound("retro_blip.wav")
        self.menu_music = util.load_sound("Hina_Fallen_leaves.wav", streaming=True)

    def on_draw(self):
        self.options_menu.draw()

    def on_update(self, delta_time: float):
        self.update_audio()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            paused_view = PausedView()
            self.window.show_view(paused_view)
        if symbol == arcade.key.S or symbol == arcade.key.DOWN:
            self.options_menu.increment_selection()
        if symbol == arcade.key.W or symbol == arcade.key.UP:
            self.options_menu.decrement_selection()
        if symbol == arcade.key.ENTER:
            if self.options_menu.selection == 0:
                paused_view = PausedView()
                self.window.show_view(paused_view)
            elif self.options_menu.selection == 1:
                controls_view = ControlsView()
                self.window.show_view(controls_view)
            elif self.options_menu.selection == 2:
                audio_view = AudioView()
                self.window.show_view(audio_view)
            elif self.options_menu.selection == 3:
                self.window.set_fullscreen(not self.window.fullscreen)

    def update_audio(self):
        scaled_effects_volume = util.EFFECTS_VOLUME * util.MASTER_VOLUME
        scaled_music_volume = util.MUSIC_VOLUME * util.MASTER_VOLUME * 0.5  # damp loud audio

        if scaled_effects_volume > 0.0:
            arcade.play_sound(self.menu_sound, scaled_effects_volume)

        if self.menu_player is None and scaled_music_volume > 0:
            self.menu_player = arcade.play_sound(self.menu_music, scaled_music_volume, looping=True)
