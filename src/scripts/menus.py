import arcade
from util import util

x_midpoint = util.WINDOW_WIDTH // 2
y_midpoint = util.WINDOW_HEIGHT // 2

def draw_title_menu():
    arcade.draw_text("IllumiGator", x_midpoint, y_midpoint, arcade.color.WHITE, 48, anchor_x="center")
    arcade.draw_text("Press ENTER to start", x_midpoint, y_midpoint - 50, arcade.color.WHITE, 24, anchor_x="center")
    arcade.draw_text("Press ESCAPE to quit", x_midpoint, y_midpoint - 100, arcade.color.WHITE, 24, anchor_x="center")

# TODO: FIX IN_GAME MENU
def draw_ingame_menu():
    arcade.draw_rectangle_filled(x_midpoint, y_midpoint, util.WINDOW_WIDTH // 3, util.WINDOW_HEIGHT // 2, arcade.color.BLACK)
    arcade.draw_text('PAUSED', x_midpoint, y_midpoint + util.WINDOW_HEIGHT // 4, arcade.color.WHITE, 48, anchor_x='center')