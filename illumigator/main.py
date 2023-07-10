import arcade

from illumigator import entity, level, menus, util


class GameObject(arcade.Window):
    def __init__(self):
        super().__init__(util.WINDOW_WIDTH, util.WINDOW_HEIGHT, util.WINDOW_TITLE)
        self.game_state = None
        self.character = None
        self.current_level = None
        self.background_sprite = None
        self.mouse_x = util.WINDOW_WIDTH / 2
        self.mouse_y = util.WINDOW_HEIGHT / 2

        # ========================= Menus =========================
        self.main_menu = None
        self.win_screen = None
        self.options_menu = None
        self.game_menu = None
        self.video_menu = None

        self.set_mouse_visible(False)
        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        self.game_state = "menu"
        self.background_sprite = util.load_sprite(
            "flowers.jpg",
            0.333333,
            center_x=util.WINDOW_WIDTH / 2,
            center_y=util.WINDOW_HEIGHT / 2,
        )
        self.background_sprite.alpha = 100
        self.character = entity.Character()

        self.current_level = level.load_level1()
        # self.current_level = level.load_test_level()

        # ========================= Menus =========================
        self.main_menu = menus.MenuView()
        self.game_menu = menus.InGameMenu()
        self.win_screen = menus.WinScreen()
        self.options_menu = menus.GenericMenu("OPTIONS", ("RETURN", "CONTROLS", "AUDIO", "VIDEO"))
        self.video_menu = menus.GenericMenu("VIDEO", ("RETURN", "720p", "1080p", "1440p", "2160p (4K)"))

    def on_update(self, delta_time):
        if self.game_state == "game":
            self.character.update(self.current_level)
            self.current_level.update(
                self.character, self.mouse_x, self.mouse_y
            )  # Pass mouse coords for debugging purposes
            if any(
                light_receiver.charge >= util.RECEIVER_THRESHOLD
                for light_receiver in self.current_level.light_receiver_list
            ):
                self.game_state = "win"

    def on_draw(self):
        self.clear()

        if self.game_state == "menu":
            self.show_view(self.main_menu)
        elif self.game_state == "game" or self.game_state == "paused":
            self.background_sprite.draw()
            self.current_level.draw()
            self.character.draw()

            if self.game_state == "paused":
                self.game_menu.draw()

        if self.game_state == "win":
            self.win_screen.draw()

        if self.game_state == "options":
            self.options_menu.draw()

        if self.game_state == "video":
            self.video_menu.draw()

    def on_key_press(self, key, key_modifiers):
        if self.game_state == "menu":
            if key == arcade.key.ENTER:
                self.game_state = "game"
            if key == arcade.key.ESCAPE:
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
            if key == arcade.key.ESCAPE:
                self.game_state = "game"
            if key == arcade.key.DOWN:
                self.game_menu.increment_selection()
            if key == arcade.key.UP:
                self.game_menu.decrement_selection()
            if key == arcade.key.ENTER:
                if self.game_menu.selection == 0:
                    self.game_state = "game"
                elif self.game_menu.selection == 1:
                    self.game_state = "options"
                elif self.game_menu.selection == 2:
                    self.game_state = "menu"

        elif self.game_state == "win":
            if key == arcade.key.DOWN:
                self.win_screen.increment_selection()
            if key == arcade.key.UP:
                self.win_screen.decrement_selection()
            if key == arcade.key.ENTER:
                if self.win_screen.selection == 0:
                    self.game_state = "menu"
                elif self.win_screen.selection == 1:
                    self.setup()

        elif self.game_state == "options":
            if key == arcade.key.DOWN:
                self.options_menu.increment_selection()
            if key == arcade.key.UP:
                self.options_menu.decrement_selection()
            if key == arcade.key.ENTER:
                if self.options_menu.selection == 0:
                    self.game_state = "game"
                elif self.options_menu.selection == 1:
                    self.game_state = "controls"
                elif self.options_menu.selection == 2:
                    self.game_state = "audio"
                elif self.options_menu.selection == 3:
                    self.game_state = "video"

        elif self.game_state == "video":
            if key == arcade.key.DOWN:
                self.video_menu.increment_selection()
            if key == arcade.key.UP:
                self.video_menu.decrement_selection()
            if key == arcade.key.ENTER:
                if self.video_menu.selection == 0:
                    self.game_state = "options"
                if self.video_menu.selection == 1:
                    util.WINDOW_WIDTH = 1280
                    util.WINDOW_HEIGHT = 720
                if self.video_menu.selection == 2:
                    util.WINDOW_WIDTH = 1920
                    util.WINDOW_HEIGHT = 1080
                if self.video_menu.selection == 3:
                    util.WINDOW_WIDTH = 2560
                    util.WINDOW_HEIGHT = 1440
                if self.video_menu.selection == 4:
                    util.WINDOW_WIDTH = 3840
                    util.WINDOW_HEIGHT = 2160
                self.current_level = level.load_level1()  # TODO: new scale
                super().set_size(util.WINDOW_WIDTH, util.WINDOW_HEIGHT)

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

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.mouse_x, self.mouse_y = x, y


def main():
    window = GameObject()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
