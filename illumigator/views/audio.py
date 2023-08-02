import arcade

from illumigator import menus, util


class AudioView(arcade.View):
    def __init__(self, options_view):
        super().__init__()
        self.options_view = options_view
        self.menu_effect = util.load_sound("retro_blip.wav")
        self.effect_keys = (arcade.key.UP, arcade.key.DOWN, arcade.key.W, arcade.key.S,
                            arcade.key.LEFT, arcade.key.RIGHT, arcade.key.A, arcade.key.D,
                            arcade.key.ESCAPE, arcade.key.ENTER)
        self.menu = menus.AudioMenu(("MASTER", "MUSIC", "EFFECTS"),
                                    (util.MASTER_VOLUME, util.MUSIC_VOLUME, util.EFFECTS_VOLUME))

    def on_update(self, delta_time: float):
        self.menu.update()
        util.MASTER_VOLUME = self.menu.slider_list[0].pos
        util.MUSIC_VOLUME = self.menu.slider_list[1].pos
        util.EFFECTS_VOLUME = self.menu.slider_list[2].pos
        self.options_view.paused_view.menu_player.volume = util.MASTER_VOLUME * util.MUSIC_VOLUME * 0.5

    def on_draw(self):
        self.window.clear()
        self.menu.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        scaled_effects_volume = util.EFFECTS_VOLUME * util.MASTER_VOLUME

        if symbol in self.effect_keys and scaled_effects_volume > 0:
            arcade.play_sound(self.menu_effect)

        if symbol == arcade.key.ESCAPE:
            self.window.show_view(self.options_view)
        if symbol == arcade.key.LEFT:
            self.menu.slider_list[self.menu.selection].left = True
        if symbol == arcade.key.RIGHT:
            self.menu.slider_list[self.menu.selection].right = True
        if symbol == arcade.key.UP:
            self.menu.slider_list[self.menu.selection].left = False
            self.menu.slider_list[self.menu.selection].right = False
            self.menu.decrement_selection()
        if symbol == arcade.key.DOWN:
            self.menu.slider_list[self.menu.selection].left = False
            self.menu.slider_list[self.menu.selection].right = False
            self.menu.increment_selection()

    def on_key_release(self, _symbol: int, _modifiers: int):
        if _symbol == arcade.key.LEFT:
            self.menu.slider_list[self.menu.selection].left = False
        if _symbol == arcade.key.RIGHT:
            self.menu.slider_list[self.menu.selection].right = False
