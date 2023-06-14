import arcade
from util import util

windowConstants = util.get_constants()

title_x = windowConstants.get('WINDOW_WIDTH') // 2
title_y = windowConstants.get('WINDOW_HEIGHT') // 2

def draw_menu():
    arcade.draw_text("IllumiGator", title_x, title_y, arcade.color.WHITE, 48, anchor_x="center")
    arcade.draw_text("Press ENTER to start", title_x, title_y - 50, arcade.color.WHITE, 24, anchor_x="center")
    arcade.draw_text("Press ESCAPE to quit", title_x, title_y - 100, arcade.color.WHITE, 24, anchor_x="center")