import arcade

from illumigator.views.game import GameView
import util


def main():
    window = arcade.Window(util.WORLD_WIDTH, util.WORLD_HEIGHT, util.WINDOW_TITLE)
    game_view = GameView()
    window.show_view(game_view)
    game_view.setup()
    arcade.run()


if __name__ == "__main__":
    main()
