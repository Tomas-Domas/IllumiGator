import arcade

from illumigator import util

x_midpoint = util.WORLD_WIDTH // 2
y_midpoint = util.WORLD_HEIGHT // 2


class Slider:
    def __init__(self,
                 center_x=0,
                 center_y=0,
                 scale=1,
                 pos=1):
        self._pos = pos
        self.center_x = center_x
        self.center_y = center_y
        self.scale = scale

        self.slider_width = 128 * scale
        self.rel_cursor_pos = (center_x - self.slider_width // 2) + pos * self.slider_width
        self.slider = util.load_sprite("slider.png", scale=scale, center_x=center_x, center_y=center_y)
        self.cursor = util.load_sprite("cursor.png", scale=scale, center_x=self.rel_cursor_pos, center_y=center_y)

        self.left = False
        self.right = False

    def update(self):

        if self.left:
            self.pos = self.pos - 0.02
        if self.right:
            self.pos = self.pos + 0.02

        self.cursor.center_x = (self.center_x - self.slider_width // 2) + self._pos * self.slider_width

    def draw(self):
        self.slider.draw()
        self.cursor.draw()

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, pos):
        if not pos < 0 and not pos > 1:
            self._pos = pos


class MainMenu():
    @staticmethod
    def draw():
        arcade.draw_text(
            "Illumi",
            x_midpoint,
            y_midpoint,
            arcade.color.YELLOW,
            util.H2_FONT_SIZE,
            anchor_x="right",
            font_name=util.MENU_FONT,
        )
        arcade.draw_text(
            "Gator",
            x_midpoint,
            y_midpoint,
            arcade.color.GREEN,
            util.H2_FONT_SIZE,
            anchor_x="left",
            font_name=util.MENU_FONT,
            bold=True
        )
        arcade.draw_text(
            "Press ENTER to start",
            x_midpoint,
            y_midpoint - 50,
            arcade.color.WHITE,
            util.BODY_FONT_SIZE,
            anchor_x="center",
            font_name=util.MENU_FONT)
        arcade.draw_text(
            "Press ESCAPE to quit",
            x_midpoint,
            y_midpoint - 100,
            arcade.color.WHITE,
            util.BODY_FONT_SIZE,
            anchor_x="center",
            font_name=util.MENU_FONT
        )


class GenericMenu:
    def __init__(self, title, options, selection=0):
        self.title = title
        self.options = options
        self._selection = selection

    def draw(self):
        dy = 0
        arcade.draw_text(
            self.title,
            x_midpoint,
            y_midpoint + util.WORLD_HEIGHT // 4,
            arcade.color.WHITE,
            util.H2_FONT_SIZE,
            anchor_x="center",
            anchor_y="top",
            font_name=util.MENU_FONT
        )
        for index, option in enumerate(self.options):
            color = arcade.color.WHITE
            if index == self._selection:
                color = arcade.color.RED
            arcade.draw_text(
                option,
                x_midpoint,
                y_midpoint - dy,
                color,
                util.H3_FONT_SIZE,
                anchor_x="center",
                font_name=util.MENU_FONT
            )
            dy += 50

    def increment_selection(self):
        self._selection = (
            0 if self._selection == len(self.options) - 1 else self._selection + 1
        )

    def decrement_selection(self):
        self._selection = (
            len(self.options) - 1 if self._selection == 0 else self._selection - 1
        )

    @property
    def selection(self):
        return self._selection


class InGameMenu:
    def __init__(self, selection=0):
        self._selection = selection
        self.options = ("RESUME", "RESTART", "OPTIONS", "QUIT TO MENU")

    def draw(self):
        dy = 0
        arcade.draw_rectangle_filled(
            x_midpoint,
            y_midpoint,
            util.WORLD_WIDTH // 3,
            util.WORLD_HEIGHT // 2,
            arcade.color.BLACK,
        )
        arcade.draw_text(
            "PAUSED",
            x_midpoint,
            y_midpoint + util.WORLD_HEIGHT // 4,
            arcade.color.WHITE,
            util.H2_FONT_SIZE,
            anchor_x="center",
            anchor_y="top",
            font_name=util.MENU_FONT
        )
        for index, option in enumerate(self.options):
            color = arcade.color.WHITE
            if index == self._selection:
                color = arcade.color.RED
            arcade.draw_text(
                option,
                x_midpoint,
                y_midpoint - dy,
                color,
                util.H3_FONT_SIZE,
                anchor_x="center",
                font_name=util.MENU_FONT
            )
            dy += 50

    def increment_selection(self):
        self._selection = (
            0 if self._selection == len(self.options) - 1 else self._selection + 1
        )

    def decrement_selection(self):
        self._selection = (
            len(self.options) - 1 if self._selection == 0 else self._selection - 1
        )

    @property
    def selection(self):
        return self._selection


class WinScreen:
    def __init__(self, selection=0):
        self._selection = selection
        self.options = ("CONTINUE?", "RETRY", "QUIT TO MENU")

    def draw(self):
        dy = 0
        arcade.draw_rectangle_filled(
            x_midpoint,
            y_midpoint,
            util.WORLD_WIDTH // 3,
            util.WORLD_HEIGHT // 2,
            arcade.color.WHITE,
        )
        arcade.draw_text(
            "YOU WIN!",
            x_midpoint,
            y_midpoint + util.WORLD_HEIGHT // 4,
            arcade.color.BLACK,
            48,
            anchor_x="center",
            anchor_y="top",
            font_name=util.WIN_FONT
        )
        for index, option in enumerate(self.options):
            color = arcade.color.BLACK
            if index == self._selection:
                color = arcade.color.YELLOW
            arcade.draw_text(
                option, x_midpoint, y_midpoint - dy, color, 24, anchor_x="center", font_name=util.WIN_FONT
            )
            dy += 50

    def increment_selection(self):
        self._selection = (
            0 if self._selection == len(self.options) - 1 else self._selection + 1
        )

    def decrement_selection(self):
        self._selection = (
            len(self.options) - 1 if self._selection == 0 else self._selection - 1
        )

    @property
    def selection(self):
        return self._selection


class ControlsMenu:
    def __init__(self):
        self.wasd_row = ("A", "S", "D")

    def draw(self):
        # ========================= Movement Key Sprites =========================
        util.load_sprite("key.png", 1, center_x=util.WORLD_WIDTH // 4, center_y=util.WORLD_HEIGHT // 2).draw()
        for index in range(-1, 2):
            util.load_sprite("key.png", 1,
                             center_x=util.WORLD_WIDTH // 4 + index*64, center_y=util.WORLD_HEIGHT // 2 - 64).draw()

        util.load_sprite("arrow.png", 1, center_x=util.WORLD_WIDTH // 4, center_y=util.WORLD_HEIGHT // 2 - 164).draw()
        for index in range(-1, 2):
            util.load_sprite("arrow.png", 1,
                             center_x=util.WORLD_WIDTH // 4 + index * 64, center_y=util.WORLD_HEIGHT // 2 - 228,
                             angle=90 + (index + 1) * 90).draw()

        # ========================= Rotation Key Sprites =========================
        util.load_sprite("key.png", 1, center_x=util.WORLD_WIDTH * 3 // 4 - 32, center_y=util.WORLD_HEIGHT // 2).draw()
        util.load_sprite("key.png", 1, center_x=util.WORLD_WIDTH * 3 // 4 + 32, center_y=util.WORLD_HEIGHT // 2).draw()

        # ========================= Titles =========================
        arcade.draw_text("PRESS ESCAPE TO RETURN",
                         util.WORLD_WIDTH // 2,
                         util.WORLD_HEIGHT - util.H3_FONT_SIZE,
                         font_size=util.H3_FONT_SIZE,
                         anchor_x="center",
                         anchor_y="top",
                         color=arcade.color.RED,
                         font_name=util.MENU_FONT
                         )
        arcade.draw_text("MOVEMENT",
                         util.WORLD_WIDTH // 4,
                         util.WORLD_HEIGHT // 2 + 100,
                         font_size=util.BODY_FONT_SIZE,
                         anchor_x="center",
                         font_name=util.MENU_FONT
                         )
        arcade.draw_text("ROTATION",
                         util.WORLD_WIDTH * 3 // 4,
                         util.WORLD_HEIGHT // 2 + 100,
                         font_size=util.BODY_FONT_SIZE,
                         anchor_x="center",
                         font_name=util.MENU_FONT
                         )

        # ========================= Movement Key Labels =========================
        arcade.draw_text("W",
                         util.WORLD_WIDTH // 4,
                         util.WORLD_HEIGHT // 2,
                         font_size=util.H3_FONT_SIZE,
                         anchor_x="center",
                         anchor_y="center",
                         color=arcade.color.BLACK_OLIVE,
                         font_name=util.MENU_FONT
                         )
        for index in range(-1, 2):
            arcade.draw_text(self.wasd_row[index+1],
                             util.WORLD_WIDTH // 4 + index*64,
                             util.WORLD_HEIGHT // 2 - 64,
                             font_size=util.H3_FONT_SIZE,
                             anchor_x="center",
                             anchor_y="center",
                             color=arcade.color.BLACK_OLIVE,
                             font_name=util.MENU_FONT
                             )

        # ========================= Rotation Key Labels =========================
        arcade.draw_text("Q",
                         util.WORLD_WIDTH * 3 // 4 - 32,
                         util.WORLD_HEIGHT // 2,
                         font_size=util.H3_FONT_SIZE,
                         anchor_x="center",
                         anchor_y="center",
                         color=arcade.color.BLACK_OLIVE,
                         font_name=util.MENU_FONT
                         )
        arcade.draw_text("E",
                         util.WORLD_WIDTH * 3 // 4 + 32,
                         util.WORLD_HEIGHT // 2,
                         font_size=util.H3_FONT_SIZE,
                         anchor_x="center",
                         anchor_y="center",
                         color=arcade.color.BLACK_OLIVE,
                         font_name=util.MENU_FONT
                         )


class AudioMenu:
    def __init__(self, master_volume):
        self.slider = Slider(util.WORLD_WIDTH // 2, util.WORLD_HEIGHT // 2, 2, master_volume)

    def draw(self):
        arcade.draw_text("MASTER VOLUME: " + str(int(self.slider.pos * 100)),
                         self.slider.center_x,
                         self.slider.center_y + 50,
                         font_size=util.H3_FONT_SIZE,
                         color=arcade.color.BLUE,
                         anchor_x="center",
                         font_name=util.MENU_FONT
                         )
        arcade.draw_text("PRESS ESCAPE TO RETURN",
                         util.WORLD_WIDTH // 2,
                         util.WORLD_HEIGHT - util.H3_FONT_SIZE,
                         font_size=util.H3_FONT_SIZE,
                         anchor_x="center",
                         anchor_y="top",
                         color=arcade.color.RED,
                         font_name=util.MENU_FONT
                         )
        self.slider.draw()

    def update(self):
        self.slider.update()
