import arcade

from illumigator import util

x_midpoint = util.WINDOW_WIDTH // 2
y_midpoint = util.WINDOW_HEIGHT // 2


def draw_title_menu():
    arcade.draw_text("IllumiGator", x_midpoint, y_midpoint, arcade.color.WHITE, 48, anchor_x="center")
    arcade.draw_text("Press ENTER to start", x_midpoint, y_midpoint - 50, arcade.color.WHITE, 24, anchor_x="center")
    arcade.draw_text("Press ESCAPE to quit", x_midpoint, y_midpoint - 100, arcade.color.WHITE, 24, anchor_x="center")


class InGameMenu:
    def __init__(self, selection=0):
        self._selection = selection
        self.options = ('RESUME', 'QUIT TO MENU')

    def draw(self):
        dy = 0
        arcade.draw_rectangle_filled(x_midpoint, y_midpoint, util.WINDOW_WIDTH // 3, util.WINDOW_HEIGHT // 2,
                                     arcade.color.BLACK)
        arcade.draw_text('PAUSED', x_midpoint, y_midpoint + util.WINDOW_HEIGHT // 4, arcade.color.WHITE, 48,
                         anchor_x='center', anchor_y='top')
        for index, option in enumerate(self.options):
            color = arcade.color.WHITE
            if index == self._selection:
                color = arcade.color.RED
            arcade.draw_text(option, x_midpoint, y_midpoint - dy, color, 24, anchor_x='center')
            dy += 50

    def increment_selection(self):
        self._selection = 0 if self._selection == len(self.options) - 1 else self._selection + 1

    def decrement_selection(self):
        self._selection = len(self.options) - 1 if self._selection == 0 else self._selection - 1

    @property
    def selection(self):
        return self._selection


class WinScreen:
    def __init__(self, selection=0):
        self._selection = selection
        self.options = ('CONTINUE?', 'QUIT TO MENU')

    def draw(self):
        dy = 0
        arcade.draw_rectangle_filled(x_midpoint, y_midpoint, util.WINDOW_WIDTH // 3, util.WINDOW_HEIGHT // 2,
                                     arcade.color.WHITE)
        arcade.draw_text('YOU WIN!', x_midpoint, y_midpoint + util.WINDOW_HEIGHT // 4, arcade.color.BLACK, 48,
                         anchor_x='center', anchor_y='top')
        for index, option in enumerate(self.options):
            color = arcade.color.BLACK
            if index == self._selection:
                color = arcade.color.YELLOW
            arcade.draw_text(option, x_midpoint, y_midpoint - dy, color, 24, anchor_x='center')
            dy += 50

    def increment_selection(self):
        self._selection = 0 if self._selection == len(self.options) - 1 else self._selection + 1

    def decrement_selection(self):
        self._selection = len(self.options) - 1 if self._selection == 0 else self._selection - 1

    @property
    def selection(self):
        return self._selection
