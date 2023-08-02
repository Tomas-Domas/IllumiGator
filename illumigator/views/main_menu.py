import arcade

from illumigator import menus, util
from illumigator.views.game import GameView
from illumigator.views.community_level import CommunityView
from illumigator.views.official_level import OfficialView


class MainMenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.menu_music = util.load_sound("Hina_Fallen_leaves.wav", streaming=True)
        arcade.text_pyglet.load_font(util.ENVIRON_ASSETS_PATH + "PressStart2P-Regular.ttf")
        self.menu_player = None
        self.menu = menus.MainMenu()
        self.game_view = GameView(self)
        self.game_view.setup()

    def setup(self):
        pass

    def on_update(self, delta_time: float):
        pass

    def on_draw(self):
        self.window.clear()
        self.menu.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ENTER:
            self.menu_player = arcade.stop_sound(self.menu_player)
            self.window.show_view(self.game_view)
        if symbol == arcade.key.ESCAPE:
            self.window.on_close()
        if symbol == arcade.key.O:
            official_view = OfficialView(self)
            self.window.show_view(official_view)
        if symbol == arcade.key.C:
            community_view = CommunityView(self)
            self.window.show_view(community_view)

    def on_show_view(self):
        scaled_music_volume = util.MUSIC_VOLUME * util.MASTER_VOLUME * 0.5

        if self.menu_player is None:
            self.menu_player = arcade.play_sound(self.menu_music, scaled_music_volume, looping=True)
