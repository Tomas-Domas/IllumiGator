import arcade
from illumigator import util

x_midpoint = util.WORLD_WIDTH // 2
y_midpoint = util.WORLD_HEIGHT // 2
planet_size = 64


class LevelSelector:
    def __init__(self, selection=0):
        self._selection = selection
        util.update_community_metadata()
        self.levels = util.get_community_metadata()[1]

        self.page_count = util.get_community_metadata()[0]
        self.current_page = 1

        self.level_names = []
        self.planets = []

        for i in range(0, len(self.levels)):
            self.level_names.append(self.levels[i]["level_name"])

        for index in range(0, len(self.levels)):
            column = index % 5
            row = index // 5
            y_start_point = util.WORLD_HEIGHT - util.WORLD_HEIGHT // 4 - (3/2 * planet_size)
            self.planets.append(util.load_sprite(
                "planet.png",
                scale=2,
                center_x=column * util.WORLD_WIDTH // 5 + (3/2 * planet_size),
                center_y=y_start_point - row * util.WORLD_HEIGHT // 4))

    def update(self):
        self.level_names = []
        self.planets = []
        self.levels = util.get_community_metadata(page=self.current_page)[1]

        for i in range(0, len(self.levels)):
            self.level_names.append(self.levels[i]["level_name"])

        for index in range(0, len(self.levels)):
            column = index % 5
            row = index // 5
            y_start_point = util.WORLD_HEIGHT - util.WORLD_HEIGHT // 4 - (3 / 2 * planet_size)
            self.planets.append(util.load_sprite(
                "planet.png",
                scale=2,
                center_x=column * util.WORLD_WIDTH // 5 + (3 / 2 * planet_size),
                center_y=y_start_point - row * util.WORLD_HEIGHT // 4))

    def draw(self):
        arcade.draw_text("COMMUNITY LEVELS",
                         util.WORLD_WIDTH // 2,
                         util.WORLD_HEIGHT - util.H3_FONT_SIZE,
                         font_size=util.H3_FONT_SIZE,
                         anchor_x="center",
                         anchor_y="top",
                         color=arcade.color.RED,
                         font_name=util.MENU_FONT
                         )

        for index, name in enumerate(self.level_names):
            color = arcade.color.WHITE
            if index == self.selection:
                color = arcade.color.RED
            arcade.draw_text(name if len(name) < 9 else name[:8] + "...",
                             self.planets[index].center_x,
                             self.planets[index].center_y + 64,
                             font_size=util.BODY_FONT_SIZE,
                             font_name=util.MENU_FONT,
                             color=color,
                             anchor_x="center")

        for planet in self.planets:
            planet.draw()

    @property
    def selection(self):
        return self._selection

    @selection.setter
    def selection(self, selection):
        if selection > 14:
            if self.current_page < self.page_count:
                self.current_page += 1
                self.selection = 0
                self.update()
            else:
                self._selection = 14
        elif selection < 0:
            if self.current_page > 1:
                self.current_page -= 1
                self.update()
                self.selection = 14
            else:
                self._selection = 0
        else:
            self._selection = selection if selection < len(self.levels) - 1 else len(self.levels) - 1
