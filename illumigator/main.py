import arcade
import numpy

from illumigator import entity, level, menus, util
from util import WORLD_WIDTH, WORLD_HEIGHT, WINDOW_TITLE


class GameObject(arcade.Window):
    def __init__(self):
        super().__init__(WORLD_WIDTH, WORLD_HEIGHT, WINDOW_TITLE, resizable=True)
        self.enemy = None
        self.character = None
        self.current_level = None
        self.menu_sound = None
        self.background_music = None
        self.music_player = None

        # ========================= Window =========================
        arcade.set_background_color(arcade.color.BLACK)
        self.background_sprite = None
        self.mouse_x = util.WORLD_WIDTH // 2
        self.mouse_y = util.WORLD_HEIGHT // 2
        self.set_mouse_visible(False)

        # ========================= State =========================
        self.game_state = None

        # ========================= Menus =========================
        self.main_menu = None
        self.win_screen = None
        self.options_menu = None
        self.game_menu = None
        self.controls_menu = None
        self.audio_menu = None

        # ========================= Settings =========================
        self.settings = util.load_data("config.json")
        self.master_volume = self.settings["master_volume"]

    def setup(self):
        self.game_state = "menu"
        self.background_sprite = util.load_sprite(
            "flowers.jpg",
            0.333333,
            center_x=WORLD_WIDTH // 2,
            center_y=WORLD_HEIGHT // 2,
        )
        self.background_sprite.alpha = 100
        self.character = entity.Character()
        self.enemy = entity.Enemy()

        self.current_level = level.load_level1()
        # self.current_level = level.load_test_level()

        # ========================= Sounds =========================
        self.menu_sound = util.load_sound("retro_blip.wav")
        self.background_music = util.load_sound("sprazara.mp3")

        # ========================= Fonts =========================
        arcade.text_pyglet.load_font("assets/PressStart2P-Regular.ttf")
        arcade.text_pyglet.load_font("assets/AtlantisInternational.ttf")

        # ========================= Menus =========================
        self.main_menu = menus.MainMenu()
        self.game_menu = menus.GenericMenu("PAUSED", ("RESUME", "RESTART", "OPTIONS", "QUIT TO MENU"), overlay=True)
        self.win_screen = menus.GenericMenu("YOU WIN", ("CONTINUE", "RETRY", "QUIT TO MENU"))
        self.options_menu = menus.GenericMenu("OPTIONS", ("RETURN", "CONTROLS", "AUDIO", "FULLSCREEN"))
        self.controls_menu = menus.ControlsMenu()
        self.audio_menu = menus.AudioMenu(master_volume=self.master_volume)
    # def reload(self):

    def on_update(self, delta_time):
        if self.game_state == "game":
            self.character.update(self.current_level)
            self.enemy.update(self.current_level, self.character)
            self.current_level.update(
                self.character, self.mouse_x, self.mouse_y
            )  # Pass mouse coords for debugging purposes
            if any(
                    light_receiver.charge >= util.RECEIVER_THRESHOLD
                    for light_receiver in self.current_level.light_receiver_list
            ):
                self.game_state = "win"

            if self.character.status == "dead":
                self.game_state = "win"

        if self.game_state == "audio":
            self.audio_menu.update()

    def on_draw(self):
        self.clear()

        if self.game_state == "menu":
            self.main_menu.draw()
        elif self.game_state == "game" or self.game_state == "paused":
            self.background_sprite.draw()
            self.current_level.draw()
            self.character.draw()
            self.enemy.draw()

            if self.music_player is None:
                self.music_player = arcade.play_sound(self.background_music, looping=True)
            else:
                self.music_player.play()

            if self.game_state == "paused":
                self.music_player.pause()
                self.game_menu.draw()

        if self.game_state == "win":
            self.win_screen.draw()
            self.music_player.pause()

        # if self.game_state == "game_over":

        if self.game_state == "options":
            self.options_menu.draw()

        if self.game_state == "video":
            self.video_menu.draw()

        if self.game_state == "controls":
            self.controls_menu.draw()

        if self.game_state == "audio":
            self.master_volume = self.audio_menu.slider.pos
            self.audio_menu.draw()

    def on_key_press(self, key, key_modifiers):

        if key == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)

        if self.game_state == "menu":
            if key == arcade.key.ENTER:
                self.game_state = "game"
            if key == arcade.key.ESCAPE:
                self.settings["master_volume"] = self.master_volume
                print(self.settings["master_volume"])
                util.write_data("config.json", self.settings)
                arcade.close_window()

        elif self.game_state == "game":
            if key == arcade.key.G:
                util.DEBUG_GEOMETRY = not util.DEBUG_GEOMETRY
            if key == arcade.key.L:
                util.DEBUG_LIGHT_SOURCES = not util.DEBUG_LIGHT_SOURCES

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

            if key == arcade.key.Q:
                self.character.rotation_dir += 1
            if key == arcade.key.E:
                self.character.rotation_dir -= 1

        elif self.game_state == "paused":
            arcade.play_sound(self.menu_sound)
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
                    self.current_level = level.load_level1()
                    self.character.reset_pos(util.WORLD_WIDTH // 2, util.WORLD_HEIGHT // 2)
                    self.enemy.reset_pos(util.WORLD_WIDTH - 200, util.WORLD_HEIGHT - 200)
                    self.game_state = "game"
                elif self.game_menu.selection == 2:
                    self.game_state = "options"
                elif self.game_menu.selection == 3:
                    self.music_player.seek(0.0)
                    self.setup()

        elif self.game_state == "win":
            arcade.play_sound(self.menu_sound)
            if key == arcade.key.S or key == arcade.key.DOWN:
                self.win_screen.increment_selection()
            if key == arcade.key.W or key == arcade.key.UP:
                self.win_screen.decrement_selection()
            if key == arcade.key.ENTER:
                if self.win_screen.selection == 0:
                    self.game_state = "menu"
                if self.win_screen.selection == 1:
                    self.current_level = level.load_level1()
                    self.character.reset_pos(util.WORLD_WIDTH // 2, util.WORLD_HEIGHT // 2)
                    self.enemy.reset_pos(util.WORLD_WIDTH - 200, util.WORLD_HEIGHT - 200)
                    self.game_state = "game"
                elif self.win_screen.selection == 2:
                    self.music_player.seek(0.0)
                    self.setup()

        elif self.game_state == "options":
            arcade.play_sound(self.menu_sound)
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
                self.audio_menu.slider.left = True
            if key == arcade.key.RIGHT:
                self.audio_menu.slider.right = True

    def on_key_release(self, key, key_modifiers):
        if key == arcade.key.W or key == arcade.key.UP:
            self.character.up = False
        if key == arcade.key.A or key == arcade.key.LEFT:
            self.character.left = False
        if key == arcade.key.S or key == arcade.key.DOWN:
            self.character.down = False
        if key == arcade.key.D or key == arcade.key.RIGHT:
            self.character.right = False
        self.character.update(self.current_level)

        if key == arcade.key.Q:
            self.character.rotation_dir -= 1
        if key == arcade.key.E:
            self.character.rotation_dir += 1

        if self.game_state == "audio":
            if key == arcade.key.LEFT:
                self.audio_menu.slider.left = False
            if key == arcade.key.RIGHT:
                self.audio_menu.slider.right = False

    def on_resize(self, width: float, height: float):
        min_ratio = min(width / WORLD_WIDTH, height / WORLD_HEIGHT)
        window_width = width / min_ratio
        window_height = height / min_ratio
        width_difference = (window_width - WORLD_WIDTH) / 2
        height_difference = (window_height - WORLD_HEIGHT) / 2
        arcade.set_viewport(-width_difference, WORLD_WIDTH + width_difference, -height_difference, WORLD_HEIGHT +
                            height_difference)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.mouse_x, self.mouse_y = x, y

    def on_close(self):
        self.settings["master_volume"] = self.master_volume
        print(self.settings["master_volume"])
        util.write_data("config.json", self.settings)
        arcade.close_window()


def main():
    window = GameObject()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
