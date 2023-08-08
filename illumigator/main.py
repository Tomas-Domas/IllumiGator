import time

import arcade
import numpy

from illumigator import level, menus, util, level_selector, worldobjects


class GameObject(arcade.Window):
    def __init__(self):
        super().__init__(util.WORLD_WIDTH, util.WORLD_HEIGHT, util.WINDOW_TITLE, resizable=True, antialiasing=True)
        self.set_mouse_visible(False)
        self.current_level: level.Level = None
        self.current_level_creator: level.LevelCreator = None
        self.menu_sound = None
        self.background_music = None
        self.menu_music = None
        self.menu_player = None
        self.bgm_player = None
        self.mouse_position = numpy.zeros(2)

        # ========================= Window =========================
        arcade.set_background_color(arcade.color.BLACK)
        self.set_update_rate(1 / util.FRAME_RATE)

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
        self.current_level = level.load_level(util.load_data(self.current_level_path, True), self.effects_volume * self.master_volume)

        # ========================= Sounds =========================
        self.menu_sound = util.load_sound("retro_blip.wav")
        self.background_music = util.load_sound("ocean-of-ice.wav", streaming=True)
        self.menu_music = util.load_sound("Hina_Fallen_leaves.wav", streaming=True)

        # ========================= Fonts =========================
        arcade.text_pyglet.load_font(util.ENVIRON_ASSETS_PATH + "PressStart2P-Regular.ttf")

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

    def on_update(self, delta_time):
        # STATE MACHINE FOR UPDATING LEVEL
        if self.game_state == "game":
            if self.current_level.update(self.effects_volume*self.master_volume) is False:
                self.game_state = "game_over"

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
                    self.effects_volume * self.master_volume
                )

        elif self.game_state == "level_creator":
            self.current_level_creator.update(self.mouse_position)
            self.current_level.update(self.effects_volume * self.master_volume, ignore_all_checks=True)

        elif self.game_state == "audio":
            self.audio_menu.update()

        # STATE MACHINE FOR UPDATING AUDIO PLAYER
        scaled_music_volume = self.music_volume * self.master_volume

        if self.game_state == "menu" or self.game_state == "paused" or self.game_state == "audio":
            if self.bgm_player is not None:
                self.bgm_player = arcade.stop_sound(self.bgm_player)
            if self.menu_player is None and scaled_music_volume > 0:
                self.menu_player = arcade.play_sound(self.menu_music, float(scaled_music_volume * 0.5), looping=True)
            elif self.menu_player is not None and scaled_music_volume > 0:
                self.menu_player.volume = float(scaled_music_volume * 0.5)

        if self.game_state == "game":
            if self.menu_player is not None:
                self.menu_player = arcade.stop_sound(self.menu_player)
            if self.bgm_player is None and scaled_music_volume > 0:
                self.bgm_player = arcade.play_sound(self.background_music, float(scaled_music_volume), looping=True)

        if self.game_state == "game_over" or self.game_state == "final_win" or self.game_state == "win"\
                or self.game_state == "community_win":
            if self.bgm_player is not None:
                self.bgm_player = arcade.stop_sound(self.bgm_player)

    def on_draw(self):
        self.clear()

        if self.game_state == "menu":
            self.main_menu.draw()

        elif self.game_state == "game" or self.game_state == "level_creator":
            self.current_level.draw()

        elif self.game_state == "paused":
            self.current_level.draw()
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

    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.G:
            util.DEBUG_GEOMETRY = not util.DEBUG_GEOMETRY
        if key == arcade.key.Q:
            self.current_level.gator.rotation_dir += 1
        if key == arcade.key.E:
            self.current_level.gator.rotation_dir -= 1

        if self.effects_volume * self.master_volume > 0.0:
            valid_key_selections = [arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT, arcade.key.W, arcade.key.A,
                                    arcade.key.S, arcade.key.D, arcade.key.ENTER, arcade.key.SPACE, arcade.key.ESCAPE]
            if (
                (self.game_state in ["paused", "win", "options", "audio", "final_win", "official_level_select", "community_level_select"] and key in valid_key_selections) or
                (self.game_state in ["controls", "game"] and key == arcade.key.ESCAPE)
            ):
                arcade.play_sound(self.menu_sound, float(self.effects_volume * self.master_volume))

        if key == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)

        if self.game_state == "menu":
            if key == arcade.key.ENTER or key == arcade.key.SPACE:
                self.current_level.gator.unidle()
                self.game_state = "game"
            if key == arcade.key.ESCAPE:
                self.on_close()
            if key == arcade.key.O:
                self.game_state = "official_level_select"
            if key == arcade.key.C:
                self.game_state = "community_level_select"
            if key == arcade.key.L:
                self.current_level_path = "test.json"
                self.official_level_status = False
                self.current_level = level.load_level(
                    util.load_data(self.current_level_path, True, False),
                    walking_volume=self.effects_volume * self.master_volume
                )
                self.current_level_creator = level.LevelCreator(self.current_level)
                self.game_state = "level_creator"
                self.set_mouse_visible(True)

        elif self.game_state == "game":
            if key == arcade.key.ESCAPE:
                self.game_state = "paused"
            if key == arcade.key.W or key == arcade.key.UP:
                self.current_level.gator.up = True
            if key == arcade.key.A or key == arcade.key.LEFT:
                self.current_level.gator.left = True
            if key == arcade.key.S or key == arcade.key.DOWN:
                self.current_level.gator.down = True
            if key == arcade.key.D or key == arcade.key.RIGHT:
                self.current_level.gator.right = True

        elif self.game_state == "level_creator":
            level_creator = self.current_level_creator

            if key == arcade.key.ESCAPE:
                self.set_mouse_visible(False)
                self.game_state = "menu"

            if key in [arcade.key.KEY_1, arcade.key.KEY_2, arcade.key.KEY_3, arcade.key.KEY_4, arcade.key.KEY_5]:
                level_creator.queued_type_selection = key-48  # To be generated in on_update

            if type(level_creator.selected_world_object) == worldobjects.Wall:
                if key == arcade.key.W or key == arcade.key.UP:
                    level_creator.resize_wall(self.mouse_position, 0, 1)
                if key == arcade.key.A or key == arcade.key.LEFT:
                    level_creator.resize_wall(self.mouse_position, -1, 0)
                if key == arcade.key.S or key == arcade.key.DOWN:
                    level_creator.resize_wall(self.mouse_position, 0, -1)
                if key == arcade.key.D or key == arcade.key.RIGHT:
                    level_creator.resize_wall(self.mouse_position, 1, 0)

            if key == arcade.key.Q:
                level_creator.queued_rotation = 1
            if key == arcade.key.E:
                level_creator.queued_rotation = -1




        elif self.game_state == "paused":
            if key == arcade.key.ESCAPE:
                self.game_state = "game"
            if key == arcade.key.S or key == arcade.key.DOWN:
                self.game_menu.increment_selection()
            if key == arcade.key.W or key == arcade.key.UP:
                self.game_menu.decrement_selection()
            if key == arcade.key.ENTER or key == arcade.key.SPACE:
                if self.game_menu.selection == 0:
                    self.game_state = "game"
                elif self.game_menu.selection == 1:
                    self.reset_level()
                    self.game_state = "game"
                elif self.game_menu.selection == 2:
                    self.game_state = "options"
                elif self.game_menu.selection == 3:
                    self.reset_level()
                    self.game_state = "menu"

        elif self.game_state == "win" or self.game_state == "final_win":
            win_screen = {
                "win":       self.win_menu,
                "final_win": self.final_win_menu
            }
            if key == arcade.key.S or key == arcade.key.DOWN:
                win_screen[self.game_state].increment_selection()
            if key == arcade.key.W or key == arcade.key.UP:
                win_screen[self.game_state].decrement_selection()
            if (key == arcade.key.ENTER or key == arcade.key.SPACE) and (self.game_state == "win" or self.game_state == "final_win"):
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
                        self.game_state = "menu"
                elif self.game_state == "final_win":
                    if selection == 0:
                        self.reset_level()
                        self.game_state = "game"
                    elif selection == 1:
                        self.game_state = "menu"

        elif self.game_state == "game_over" or self.game_state == "community_win":
            menu = {
                "game_over":     self.lose_menu,
                "community_win": self.community_win_menu
            }
            if key == arcade.key.S or key == arcade.key.DOWN:
                menu[self.game_state].increment_selection()
            if key == arcade.key.W or key == arcade.key.UP:
                menu[self.game_state].decrement_selection()
            if key == arcade.key.ENTER or key == arcade.key.SPACE:
                if menu[self.game_state].selection == 0:
                    self.reset_level()
                    self.game_state = "game"
                elif menu[self.game_state].selection == 1:
                    self.reset_level()
                    self.game_state = "menu"

        elif self.game_state == "options":
            if key == arcade.key.ESCAPE:
                self.game_state = "paused"
            if key == arcade.key.S or key == arcade.key.DOWN:
                self.options_menu.increment_selection()
            if key == arcade.key.W or key == arcade.key.UP:
                self.options_menu.decrement_selection()
            if key == arcade.key.ENTER or key == arcade.key.SPACE:
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
            level_selector_menu = {"community_level_select": self.community_selector_menu,
                                   "official_level_select": self.official_selector_menu}

            if key == arcade.key.D or key == arcade.key.RIGHT:
                level_selector_menu[self.game_state].selection += 1
            if key == arcade.key.A or key == arcade.key.LEFT:
                level_selector_menu[self.game_state].selection -= 1
            if key == arcade.key.W or key == arcade.key.UP:
                level_selector_menu[self.game_state].selection -= 5
            if key == arcade.key.S or key == arcade.key.DOWN:
                level_selector_menu[self.game_state].selection += 5
            if key == arcade.key.R and self.game_state == "community_level_select":
                util.update_community_metadata()
                level_selector_menu[self.game_state].update()
            if key == arcade.key.F and self.game_state == "community_level_select":
                try:
                    util.opendir(util.ENVIRON_DATA_PATH + "levels/community")
                except FileNotFoundError:
                    util.opendir(util.VENV_DATA_PATH + "levels/community")
            if key == arcade.key.ESCAPE:
                self.game_state = "menu"
            if key == arcade.key.ENTER or key == arcade.key.SPACE:
                self.current_level_path = level_selector_menu[self.game_state].get_selection()
                self.official_level_status = True if self.game_state == "official_level_select" else False
                self.current_level = level.load_level(
                    util.load_data(self.current_level_path, True, self.official_level_status),
                    walking_volume=self.effects_volume*self.master_volume
                )
                if self.game_state == "official_level_select":
                    self.official_level_index = level_selector_menu[self.game_state].selection + 1
                self.game_state = "game"

    def on_key_release(self, key, key_modifiers):
        if key == arcade.key.W or key == arcade.key.UP:
            self.current_level.gator.up = False
        if key == arcade.key.A or key == arcade.key.LEFT:
            self.current_level.gator.left = False
        if key == arcade.key.S or key == arcade.key.DOWN:
            self.current_level.gator.down = False
        if key == arcade.key.D or key == arcade.key.RIGHT:
            self.current_level.gator.right = False

        if key == arcade.key.Q:
            self.current_level.gator.rotation_dir -= 1
        if key == arcade.key.E:
            self.current_level.gator.rotation_dir += 1

        if key == arcade.key.LEFT:
            self.audio_menu.slider_list[self.audio_menu.selection].left = False
        if key == arcade.key.RIGHT:
            self.audio_menu.slider_list[self.audio_menu.selection].right = False

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.mouse_position[0] = x
        self.mouse_position[1] = y

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if self.game_state != "level_creator" or button != 1:
            return
        self.current_level_creator.on_click(self.mouse_position)

    def on_resize(self, width: float, height: float):
        min_ratio = min(width / util.WORLD_WIDTH, height / util.WORLD_HEIGHT)
        window_width = width / min_ratio if min_ratio != 0 else 1
        window_height = height / min_ratio if min_ratio != 0 else 1
        width_difference = (window_width - util.WORLD_WIDTH) / 2
        height_difference = (window_height - util.WORLD_HEIGHT) / 2
        arcade.set_viewport(-width_difference, util.WORLD_WIDTH + width_difference, -height_difference, util.WORLD_HEIGHT +
                            height_difference)

    def on_close(self):
        self.settings["volume"]["master"] = self.master_volume
        self.settings["volume"]["music"] = self.music_volume
        self.settings["volume"]["effects"] = self.effects_volume
        self.settings["current_level"] = self.official_level_index
        util.write_data("config.json", self.settings)
        arcade.close_window()

    def reset_level(self):
        self.current_level = level.load_level(
            util.load_data(self.current_level_path, True, self.official_level_status),
            self.effects_volume * self.master_volume
        )
        self.game_state = "game"


def main():
    window = GameObject()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
