import time

import arcade

from illumigator.views.game import GameView
from illumigator import entity, level, menus, util, level_selector


class GameObject(arcade.Window):
    def __init__(self):
        super().__init__(util.WORLD_WIDTH, util.WORLD_HEIGHT, util.WINDOW_TITLE, resizable=True, antialiasing=True)
        self.set_mouse_visible(False)
        self.menu_sound = None
        self.background_music = None
        self.menu_music = None
        self.menu_player = None

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

        # ========================= State =========================
        self.game_state = None

    def setup(self):
        self.game_state = "menu"

        # ========================= Sounds =========================
        self.menu_sound = util.load_sound("retro_blip.wav")
        self.menu_music = util.load_sound("Hina_Fallen_leaves.wav", streaming=True)

        # ========================= Fonts =========================
        arcade.text_pyglet.load_font(util.ENVIRON_ASSETS_PATH + "PressStart2P-Regular.ttf")

        # ========================= Menus =========================
        self.win_menu = menus.GenericMenu("LEVEL COMPLETED", ("CONTINUE", "RETRY", "QUIT TO MENU"))
        self.final_win_menu = menus.GenericMenu("YOU WIN", ("RETRY", "QUIT TO MENU"))
        self.lose_menu = menus.GenericMenu("YOU DIED", ("RETRY", "QUIT TO MENU"))
        self.controls_menu = menus.ControlsMenu()
        self.audio_menu = menus.AudioMenu(("MASTER", "MUSIC", "EFFECTS"),
                                          (self.master_volume, self.music_volume, self.effects_volume))
        self.official_selector_menu = level_selector.LevelSelector()
        self.community_selector_menu = level_selector.LevelSelector(is_community=True)
        self.community_win_menu = menus.GenericMenu("YOU WIN", ("RETRY", "QUIT TO MENU"))


    def on_update(self, delta_time):
        # STATE MACHINE FOR UPDATING LEVEL

        if self.game_state == "audio":
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

        if self.game_state == "game_over" or self.game_state == "final_win" or self.game_state == "win"\
                or self.game_state == "community_win":
            if self.bgm_player is not None:
                self.bgm_player = arcade.stop_sound(self.bgm_player)

    def on_draw(self):
        self.clear()

        if self.game_state == "menu":
            self.main_menu.draw()

        elif self.game_state == "paused":
            self.current_level.draw()
            self.character.draw()
            self.enemy.draw()
            self.game_menu.draw()

        elif self.game_state == "win":
            self.win_menu.draw()

        elif self.game_state == "game_over":
            self.lose_menu.draw()

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
        valid_menu_press = key == arcade.key.UP or key == arcade.key.DOWN or key == arcade.key.LEFT \
                           or key == arcade.key.RIGHT or key == arcade.key.W or key == arcade.key.A \
                           or key == arcade.key.S or key == arcade.key.D or key == arcade.key.ENTER \
                           or key == arcade.key.ESCAPE
        game_paused = self.game_state == "paused" or self.game_state == "win" or self.game_state == "options" \
                      or self.game_state == "audio" or self.game_state == "final_win" \
                      or self.game_state == "official_level_select" or self.game_state == "community_level_select"
        if game_paused and valid_menu_press:
            if self.effects_volume * self.master_volume > 0.0:
                arcade.play_sound(self.menu_sound, float(self.effects_volume * self.master_volume))

        if key == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)

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
                        self.game_state = "menu"
                elif self.game_state == "final_win":
                    if selection == 0:
                        self.reset_level()
                        self.game_state = "game"
                    elif selection == 1:
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

    def on_key_release(self, key, key_modifiers):
        if key == arcade.key.LEFT:
            self.audio_menu.slider_list[self.audio_menu.selection].left = False
        if key == arcade.key.RIGHT:
            self.audio_menu.slider_list[self.audio_menu.selection].right = False

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