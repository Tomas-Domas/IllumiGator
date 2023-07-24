import cProfile
import arcade
import time

from illumigator import entity, level, menus, util, level_selector
from illumigator.util import ENVIRON_ASSETS_PATH, WORLD_WIDTH, WORLD_HEIGHT, WINDOW_TITLE


class GameObject(arcade.Window):
    def __init__(self):
        super().__init__(WORLD_WIDTH, WORLD_HEIGHT, WINDOW_TITLE, resizable=True, antialiasing=True)
        self.enemy = None
        self.character = None
        self.current_level = None
        self.menu_sound = None
        self.background_music = None
        self.menu_music = None
        self.pause_music = None
        self.menu_player = None
        self.bgm_player = None
        self.pause_player = None

        # ========================= Window =========================
        arcade.set_background_color(arcade.color.BLACK)
        self.mouse_x = util.WORLD_WIDTH // 2
        self.mouse_y = util.WORLD_HEIGHT // 2

        # ========================= Menus =========================
        self.main_menu = None
        self.win_menu = None
        self.lose_menu = None
        self.options_menu = None
        self.game_menu = None
        self.controls_menu = None
        self.audio_menu = None
        self.official_selector_menu = None
        self.community_selector_menu = None
        self.final_win_menu = None
        self.community_win_menu = None

        # ========================= Settings =========================
        self.settings = util.load_data("config.json")
        self.master_volume = self.settings["volume"]["master"]
        self.music_volume = self.settings["volume"]["music"]
        self.effects_volume = self.settings["volume"]["effects"]

        # ========================= State =========================
        self.game_state = None
        self.official_level_count = util.load_data("levels.json", True, True)["level_count"]
        self.official_level_index = self.settings["current_level"]
        self.current_level_path = "level_" + str(self.official_level_index) + ".json"
        self.official_level_status = True

    def setup(self):
        self.game_state = "menu"
        self.character = entity.Character(walking_volume=self.effects_volume*self.master_volume)
        self.enemy = entity.Enemy()

        self.current_level = level.load_level(util.load_data(self.current_level_path, True), self.character, self.enemy)

        # ========================= Sounds =========================
        self.menu_sound = util.load_sound("retro_blip.wav")
        self.background_music = util.load_sound("ocean-of-ice.mp3")
        self.menu_music = util.load_sound("Hina_Fallen_leaves.mp3")
        self.pause_music = util.load_sound("Hina_Fallen_leaves.mp3")

        # ========================= Fonts =========================
        arcade.text_pyglet.load_font(ENVIRON_ASSETS_PATH + "PressStart2P-Regular.ttf")
        arcade.text_pyglet.load_font(ENVIRON_ASSETS_PATH + "AtlantisInternational.ttf")

        # ========================= Menus =========================
        self.main_menu = menus.MainMenu()
        self.game_menu = menus.GenericMenu("PAUSED", ("RESUME", "RESTART", "OPTIONS", "QUIT TO MENU"), overlay=True)
        self.win_menu = menus.GenericMenu("LEVEL COMPLETED", ("CONTINUE", "RETRY", "QUIT TO MENU"))
        self.final_win_menu = menus.GenericMenu("YOU WIN", ("RETRY", "QUIT TO MENU"))
        self.lose_menu = menus.GenericMenu("YOU DIED", ("RETRY", "QUIT TO MENU"))
        self.options_menu = menus.GenericMenu("OPTIONS", ("RETURN", "CONTROLS", "AUDIO", "FULLSCREEN"))
        self.controls_menu = menus.ControlsMenu()
        self.audio_menu = menus.AudioMenu(("MASTER", "MUSIC", "EFFECTS"),
                                          (self.master_volume, self.music_volume, self.effects_volume))
        self.official_selector_menu = level_selector.LevelSelector()
        self.community_selector_menu = level_selector.LevelSelector(is_community=True)
        self.community_win_menu = menus.GenericMenu("YOU WIN", ("RETRY", "QUIT TO MENU"))

    # def reload(self):

    def on_update(self, delta_time):
        # STATE MACHINE FOR UPDATING LEVEL
        if self.game_state == "game":
            if self.character.update(self.current_level, self.effects_volume*self.master_volume, self.enemy) is False:
                self.game_state = "game_over"

            self.enemy.update(self.current_level, self.character)
            self.current_level.update(self.character, self.enemy)
            if any(light_receiver.charge >= util.RECEIVER_THRESHOLD for light_receiver in self.current_level.light_receiver_list):
                time.sleep(0.5)
                if not self.official_level_status:
                    self.game_state = "community_win"
                    self.official_level_status = False
                elif self.official_level_index == self.official_level_count:
                    self.official_level_status = True
                    self.current_level_path = "level_" + str(self.official_level_index) + ".json"
                    self.game_state = "final_win"
                else:
                    self.official_level_index += 1
                    self.official_level_status = True
                    self.current_level_path = "level_" + str(self.official_level_index) + ".json"
                    self.game_state = "win"

                self.current_level = level.load_level(
                    util.load_data(self.current_level_path, True, self.official_level_status),
                    self.character,
                    self.enemy)

            if self.character.status == "dead":
                # Show dead animations
                self.character.left_character_loader.dead = True
                self.character.right_character_loader.dead = True
                self.enemy.state = "player_dead"
                # self.game_state = "game_over"

        elif self.game_state == "audio":
            self.audio_menu.update()

        # STATE MACHINE FOR UPDATING AUDIO PLAYER
        scaled_music_volume = self.music_volume * self.master_volume

        if self.game_state == "menu":
            if self.pause_player is not None:
                self.pause_player.pause()
            if self.bgm_player is not None:
                self.bgm_player.pause()
            # This mp3 is a little loud, so the volume is automatically downscaled.
            if self.menu_player is None:
                self.menu_player = arcade.play_sound(self.menu_music, scaled_music_volume * 0.5, looping=True)
            else:
                self.menu_player.volume = scaled_music_volume * 0.5
                self.menu_player.play()

        elif self.game_state == "game":
            if self.pause_player is not None:
                self.pause_player.pause()
            if self.menu_player is not None:
                self.menu_player.pause()
            if self.bgm_player is None:
                self.bgm_player = arcade.play_sound(self.background_music, scaled_music_volume, looping=True)
            else:
                self.bgm_player.volume = scaled_music_volume
                self.bgm_player.play()

        if self.game_state == "paused" or self.game_state == "audio":
            if self.bgm_player is not None:
                self.bgm_player.pause()
            if self.pause_player is None:
                self.pause_player = arcade.play_sound(self.pause_music, scaled_music_volume, looping=True)
            else:
                self.pause_player.volume = scaled_music_volume
                self.pause_player.play()

        if self.game_state == "game_over" or self.game_state == "final_win" or self.game_state == "win"\
                or self.game_state == "community_win":
            self.bgm_player.pause()

    def on_draw(self):
        self.clear()

        if self.game_state == "menu":
            self.main_menu.draw()

        elif self.game_state == "game":
            self.current_level.draw()
            self.character.draw()
            self.enemy.draw()

        elif self.game_state == "paused":
            self.current_level.draw()
            self.character.draw()
            self.enemy.draw()
            self.game_menu.draw()

        elif self.game_state == "win":
            self.win_menu.draw()

        elif self.game_state == "game_over":
            self.lose_menu.draw()

        elif self.game_state == "options":
            self.options_menu.draw()

        elif self.game_state == "video":
            self.video_menu.draw()

        elif self.game_state == "controls":
            self.controls_menu.draw()

        elif self.game_state == "audio":
            self.master_volume = self.audio_menu.slider_list[0].pos
            self.music_volume = self.audio_menu.slider_list[1].pos
            self.effects_volume = self.audio_menu.slider_list[2].pos
            self.audio_menu.draw()

        elif self.game_state == "official_level_select":
            self.official_selector_menu.draw()

        elif self.game_state == "community_level_select":
            self.community_selector_menu.draw()

        elif self.game_state == "final_win":
            self.final_win_menu.draw()

        elif self.game_state == "community_win":
            self.community_win_menu.draw()
    
    def unidle(self):
        self.character.last_movement_timestamp = time.time()
        self.character.left_character_loader.idle = False
        self.character.right_character_loader.idle = False

    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.Q:
            self.character.rotation_dir += 1
        if key == arcade.key.E:
            self.character.rotation_dir -= 1
        valid_menu_press = key == arcade.key.UP or key == arcade.key.DOWN or key == arcade.key.LEFT \
                           or key == arcade.key.RIGHT or key == arcade.key.W or key == arcade.key.A \
                           or key == arcade.key.S or key == arcade.key.D or key == arcade.key.ENTER \
                           or key == arcade.key.ESCAPE
        game_paused = self.game_state == "paused" or self.game_state == "win" or self.game_state == "options" \
                      or self.game_state == "audio" or self.game_state == "final_win"
        if game_paused and valid_menu_press:
            if self.effects_volume * self.master_volume != 0:
                arcade.play_sound(self.menu_sound, self.effects_volume * self.master_volume)

        if key == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)

        if self.game_state == "menu":
            if key == arcade.key.ENTER:
                self.unidle()
                self.game_state = "game"
            if key == arcade.key.ESCAPE:
                self.on_close()
            if key == arcade.key.O:
                self.game_state = "official_level_select"
            if key == arcade.key.C:
                self.game_state = "community_level_select"

        elif self.game_state == "game":
            if key == arcade.key.G:
                util.DEBUG_GEOMETRY = not util.DEBUG_GEOMETRY
            if key == arcade.key.L:
                util.DEBUG_LIGHTS = not util.DEBUG_LIGHTS

            if key == arcade.key.ESCAPE:
                self.game_state = "paused"
            if key == arcade.key.W or key == arcade.key.UP:
                self.character.up = True
            if key == arcade.key.A or key == arcade.key.LEFT:
                self.character.left = True
            if key == arcade.key.S or key == arcade.key.DOWN:
                self.character.down = True
            if key == arcade.key.D or key == arcade.key.RIGHT:
                self.character.right = True

        elif self.game_state == "paused":
            if key == arcade.key.ESCAPE:
                self.game_state = "game"
            if key == arcade.key.S or key == arcade.key.DOWN:
                self.game_menu.increment_selection()
            if key == arcade.key.W or key == arcade.key.UP:
                self.game_menu.decrement_selection()
            if key == arcade.key.ENTER:
                if self.game_menu.selection == 0:
                    self.game_state = "game"
                elif self.game_menu.selection == 1:
                    self.reset_level()
                    self.game_state = "game"
                elif self.game_menu.selection == 2:
                    self.game_state = "options"
                elif self.game_menu.selection == 3:
                    self.bgm_player.seek(0.0)
                    if self.pause_player is not None:
                        self.pause_player.seek(0.0)
                    self.reset_level()
                    self.game_state = "menu"

        elif self.game_state == "win" or self.game_state == "final_win":
            win_screen = {"win": self.win_menu,
                          "final_win": self.final_win_menu}
            if key == arcade.key.S or key == arcade.key.DOWN:
                win_screen[self.game_state].increment_selection()
            if key == arcade.key.W or key == arcade.key.UP:
                win_screen[self.game_state].decrement_selection()
            if key == arcade.key.ENTER and (self.game_state == "win" or self.game_state == "final_win"):
                selection = win_screen[self.game_state].selection
                if self.game_state == "win":
                    if selection == 0:
                        self.game_state = "game"
                    elif selection == 1:
                        self.official_level_index -= 1
                        self.current_level_path = "level_" + str(self.official_level_index) + ".json"
                        self.reset_level()
                        self.game_state = "game"
                    elif selection == 2:
                        self.bgm_player.seek(0.0)
                        self.game_state = "menu"
                elif self.game_state == "final_win":
                    if selection == 0:
                        self.reset_level()
                        self.game_state = "game"
                    elif selection == 1:
                        self.bgm_player.seek(0.0)
                        self.game_state = "menu"

        elif self.game_state == "game_over" or self.game_state == "community_win":
            menu = {"game_over": self.lose_menu,
                    "community_win": self.community_win_menu}
            if key == arcade.key.S or key == arcade.key.DOWN:
                menu[self.game_state].increment_selection()
            if key == arcade.key.W or key == arcade.key.UP:
                menu[self.game_state].decrement_selection()
            if key == arcade.key.ENTER:
                if menu[self.game_state].selection == 0:
                    self.reset_level()
                    self.game_state = "game"
                elif menu[self.game_state].selection == 1:
                    self.bgm_player.seek(0.0)
                    self.reset_level()
                    self.game_state = "menu"

        elif self.game_state == "options":
            if key == arcade.key.ESCAPE:
                self.game_state = "paused"
            if key == arcade.key.S or key == arcade.key.DOWN:
                self.options_menu.increment_selection()
            if key == arcade.key.W or key == arcade.key.UP:
                self.options_menu.decrement_selection()
            if key == arcade.key.ENTER:
                if self.options_menu.selection == 0:
                    self.game_state = "paused"
                elif self.options_menu.selection == 1:
                    self.game_state = "controls"
                elif self.options_menu.selection == 2:
                    self.game_state = "audio"
                elif self.options_menu.selection == 3:
                    self.set_fullscreen(not self.fullscreen)

        elif self.game_state == "controls":
            if key == arcade.key.ESCAPE:
                self.game_state = "options"

        elif self.game_state == "audio":
            if key == arcade.key.ESCAPE:
                self.game_state = "options"
            if key == arcade.key.LEFT:
                self.audio_menu.slider_list[self.audio_menu.selection].left = True
            if key == arcade.key.RIGHT:
                self.audio_menu.slider_list[self.audio_menu.selection].right = True
            if key == arcade.key.UP:
                self.audio_menu.slider_list[self.audio_menu.selection].left = False
                self.audio_menu.slider_list[self.audio_menu.selection].right = False
                self.audio_menu.decrement_selection()
            if key == arcade.key.DOWN:
                self.audio_menu.slider_list[self.audio_menu.selection].left = False
                self.audio_menu.slider_list[self.audio_menu.selection].right = False
                self.audio_menu.increment_selection()

        if self.game_state == "community_level_select" or self.game_state == "official_level_select":
            level_selector = {"community_level_select": self.community_selector_menu,
                              "official_level_select": self.official_selector_menu}

            if key == arcade.key.D or key == arcade.key.RIGHT:
                level_selector[self.game_state].selection += 1
            if key == arcade.key.A or key == arcade.key.LEFT:
                level_selector[self.game_state].selection -= 1
            if key == arcade.key.W or key == arcade.key.UP:
                level_selector[self.game_state].selection -= 5
            if key == arcade.key.S or key == arcade.key.DOWN:
                level_selector[self.game_state].selection += 5
            if key == arcade.key.R and self.game_state == "community_level_select":
                util.update_community_metadata()
                level_selector[self.game_state].update()
            if key == arcade.key.F and self.game_state == "community_level_select":
                try:
                    util.opendir(util.ENVIRON_DATA_PATH + "levels/community")
                except FileNotFoundError:
                    util.opendir(util.VENV_DATA_PATH + "levels/community")
            if key == arcade.key.ESCAPE:
                self.game_state = "menu"
            if key == arcade.key.ENTER:
                self.current_level_path = level_selector[self.game_state].get_selection()
                self.official_level_status = True if self.game_state == "official_level_select" else False
                self.current_level = level.load_level(
                    util.load_data(self.current_level_path, True, self.official_level_status),
                    self.character,
                    self.enemy)
                if self.game_state == "official_level_select":
                    self.official_level_index = level_selector[self.game_state].selection + 1
                self.game_state = "menu"

    def on_key_release(self, key, key_modifiers):
        if key == arcade.key.W or key == arcade.key.UP:
            self.character.up = False
        if key == arcade.key.A or key == arcade.key.LEFT:
            self.character.left = False
        if key == arcade.key.S or key == arcade.key.DOWN:
            self.character.down = False
        if key == arcade.key.D or key == arcade.key.RIGHT:
            self.character.right = False

        if key == arcade.key.Q:
            self.character.rotation_dir -= 1
        if key == arcade.key.E:
            self.character.rotation_dir += 1

        if key == arcade.key.LEFT:
            self.audio_menu.slider_list[self.audio_menu.selection].left = False
        if key == arcade.key.RIGHT:
            self.audio_menu.slider_list[self.audio_menu.selection].right = False

    def on_resize(self, width: float, height: float):
        min_ratio = min(width / WORLD_WIDTH, height / WORLD_HEIGHT)
        window_width = width / min_ratio
        window_height = height / min_ratio
        width_difference = (window_width - WORLD_WIDTH) / 2
        height_difference = (window_height - WORLD_HEIGHT) / 2
        arcade.set_viewport(-width_difference, WORLD_WIDTH + width_difference, -height_difference, WORLD_HEIGHT +
                            height_difference)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        util.mouseX, util.mouseY = x, y

    def on_close(self):
        self.settings["volume"]["master"] = self.master_volume
        self.settings["volume"]["music"] = self.music_volume
        self.settings["volume"]["effects"] = self.effects_volume
        self.settings["current_level"] = self.official_level_index
        util.write_data("config.json", self.settings)
        arcade.close_window()

    def reset_level(self):
        self.enemy.state = "asleep"
        self.unidle()

        # Create New character model
        self.character = entity.Character(walking_volume=self.effects_volume)
        
        self.current_level = level.load_level(util.load_data(
            self.current_level_path, True, self.official_level_status), self.character, self.enemy)
        self.game_state = "game"


def main():
    window = GameObject()
    window.setup()

    window.game_state = "game"
    window.on_update(1 / 60)
    window.game_state = "menu"

    arcade.run()


    # window.game_state = "game"
    # command = "for _ in range(100):\n\twindow.on_update(1/60)"
    # cProfile.runctx(command, {'window': window}, {}, sort='tottime')


if __name__ == "__main__":
    main()
