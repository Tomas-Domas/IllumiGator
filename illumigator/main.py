import arcade

from illumigator.views.main_menu import MainMenuView
import util

class GameObject(arcade.Window):
    def __init__(self):
        super().__init__(util.WORLD_WIDTH, util.WORLD_HEIGHT, util.WINDOW_TITLE, resizable=True, antialiasing=True)
        self.set_mouse_visible(False)

    def setup(self):
        main_menu_view = MainMenuView()
        self.show_view(main_menu_view)

    def on_resize(self, width: float, height: float):
        min_ratio = min(width / util.WORLD_WIDTH, height / util.WORLD_HEIGHT)
        window_width = width / min_ratio if min_ratio != 0 else 1
        window_height = height / min_ratio if min_ratio != 0 else 1
        width_difference = (window_width - util.WORLD_WIDTH) / 2
        height_difference = (window_height - util.WORLD_HEIGHT) / 2
        arcade.set_viewport(-width_difference, util.WORLD_WIDTH + width_difference, -height_difference,
                            util.WORLD_HEIGHT +
                            height_difference)

    def on_close(self):
        settings = {"current_level": util.CURRENT_LEVEL,
                    "volume": {"master": util.MASTER_VOLUME,
                               "music": util.MUSIC_VOLUME,
                               "effects": util.EFFECTS_VOLUME}}
        print(settings)  # TODO: fix settings writing
        util.write_data("config.json", settings)
        arcade.close_window()


def main():
    window = GameObject()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
