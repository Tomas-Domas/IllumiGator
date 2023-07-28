import arcade
import time

from illumigator.views.paused import PausedView
from illumigator.views.lose import LoseView
from illumigator.views.win import WinView
from illumigator.views.community_win import CommunityWinView
from illumigator.views.final_win import FinalWinView
from illumigator import entity, level, util


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.window.set_mouse_visible(False)
        self.character = None
        self.enemy = None
        self.current_level = None
        self.bgm_player = None

        self.bgm_music = util.load_sound("ocean-of-ice.wav", streaming=True)
        arcade.text_pyglet.load_font(util.ENVIRON_ASSETS_PATH + "PressStart2P-Regular.ttf")

        # ========================= Level Data =========================
        self.settings = util.load_data("config.json")
        self.official_level_count = util.load_data("levels.json", True, True)["level_count"]
        self.official_level_index = self.settings["current_level"]
        self.current_level_path = "level_" + str(self.official_level_index) + ".json"
        self.official_level_status = True

    def setup(self):
        self.character = entity.Character(walking_volume=util.EFFECTS_VOLUME * util.MASTER_VOLUME)
        self.enemy = entity.Enemy()
        self.current_level = level.load_level(util.load_data(self.current_level_path, True), self.character, self.enemy)

    def on_update(self, delta_time: float):
        if self.character.update(self.current_level, util.EFFECTS_VOLUME * util.MASTER_VOLUME, self.enemy) is False:
            lose_view = LoseView()
            self.window.show_view(lose_view)

        self.enemy.update(self.current_level, self.character)
        self.current_level.update(self.character, self.enemy)

        if any(light_receiver.charge >= util.RECEIVER_THRESHOLD for light_receiver in
               self.current_level.light_receiver_list):
            time.sleep(0.5)
            if not self.official_level_status:
                self.official_level_status = False
                community_win_view = CommunityWinView()
                self.window.show_view(community_win_view)
            elif self.official_level_index == self.official_level_count:
                self.official_level_status = True
                self.current_level_path = "level_" + str(self.official_level_index) + ".json"
                final_win_view = FinalWinView()
                self.window.show_view(final_win_view)
            else:
                self.official_level_index += 1
                self.official_level_status = True
                self.current_level_path = "level_" + str(self.official_level_index) + ".json"
                win_view = WinView()
                self.window.show_view(win_view)

            self.current_level = level.load_level(
                util.load_data(self.current_level_path, True, self.official_level_status),
                self.character,
                self.enemy)

        if self.character.status == "dead":
            # Show death animations
            self.character.left_character_loader.dead = True
            self.character.right_character_loader.dead = True
            self.enemy.state = "player_dead"

    def on_draw(self):
        self.window.clear()
        self.current_level.draw()
        self.character.draw()
        self.enemy.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.Q:
            self.character.rotation_dir += 1
        if symbol == arcade.key.E:
            self.character.rotation_dir -= 1
        if symbol == arcade.key.ESCAPE:
            paused_view = PausedView(self)
            self.window.show_view(paused_view)
        if symbol == arcade.key.W or symbol == arcade.key.UP:
            self.character.up = True
        if symbol == arcade.key.A or symbol == arcade.key.LEFT:
            self.character.left = True
        if symbol == arcade.key.S or symbol == arcade.key.DOWN:
            self.character.down = True
        if symbol == arcade.key.D or symbol == arcade.key.RIGHT:
            self.character.right = True

    def on_key_release(self, _symbol: int, _modifiers: int):
        if _symbol == arcade.key.W or _symbol == arcade.key.UP:
            self.character.up = False
        if _symbol == arcade.key.A or _symbol == arcade.key.LEFT:
            self.character.left = False
        if _symbol == arcade.key.S or _symbol == arcade.key.DOWN:
            self.character.down = False
        if _symbol == arcade.key.D or _symbol == arcade.key.RIGHT:
            self.character.right = False
        if _symbol == arcade.key.Q:
            self.character.rotation_dir -= 1
        if _symbol == arcade.key.E:
            self.character.rotation_dir += 1

    def update_audio(self):
        scaled_music_volume = util.MUSIC_VOLUME * util.MASTER_VOLUME

        if self.bgm_player is None and scaled_music_volume > 0:
            self.bgm_player = arcade.play_sound(self.bgm_music, scaled_music_volume, looping=True)

    def unidle(self):
        self.character.last_movement_timestamp = time.time()
        self.character.left_character_loader.idle = False
        self.character.right_character_loader.idle = False

    def reset_level(self):
        self.enemy.state = "asleep"
        self.unidle()

        # Create New character model
        self.character = entity.Character(walking_volume=util.EFFECTS_VOLUME)

        self.current_level = level.load_level(util.load_data(
            self.current_level_path, True, self.official_level_status), self.character, self.enemy)
