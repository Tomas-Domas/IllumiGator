import arcade

from illumigator.views.main_menu import MainMenuView
import util


def main():
    window = arcade.Window(util.WORLD_WIDTH, util.WORLD_HEIGHT, util.WINDOW_TITLE)
    main_menu_view = MainMenuView()
    window.show_view(main_menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
