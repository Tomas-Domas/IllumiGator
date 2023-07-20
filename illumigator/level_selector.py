import arcade
from illumigator import util
from illumigator.level import Level, load_level

x_midpoint = util.WORLD_WIDTH // 2
y_midpoint = util.WORLD_HEIGHT // 2
planet_size = 64


class LevelSelector:
    def __init__(self, selection=0, is_community=False):
        self._selection = selection
        self.is_community = is_community
        self.title = "COMMUNITY LEVELS" if is_community else "OFFICIAL LEVELS"

        if is_community:
            util.update_community_metadata()
            metadata = util.get_level_metadata(is_community=True)
        else:
            metadata = util.get_level_metadata()

        self.page_count = metadata[0]
        self.levels = metadata[1]
        self.filenames = metadata[2]

        self.current_page = 1

        self.level_names = []
        self.planet_filenames = []
        self.planets = []
        self.keys = []
        self.key_text = [("ESC", "RETURN TO MENU"), ("ENTER", "LOAD LEVEL")]
        if is_community:
            self.key_text.append(("R", "REFRESH LEVELS"))

        for index in range(0, len(self.key_text)):
            starting_point = 100
            self.keys.append(util.load_sprite("key.png",
                             1,
                             center_x=starting_point + index * util.WORLD_WIDTH // 3,
                             center_y=util.WORLD_HEIGHT - 120))

        for i in range(0, len(self.levels)):
            self.level_names.append(self.levels[i]["level_name"])

        for i in range(0, len(self.levels)):
            self.planet_filenames.append(self.levels[i]["planet_name"] + ".png")

        for index in range(0, len(self.levels)):
            column = index % 5
            row = index // 5
            y_start_point = util.WORLD_HEIGHT - util.WORLD_HEIGHT // 4 - (3/2 * planet_size)
            self.planets.append(util.load_sprite(
                self.planet_filenames[index],
                scale=2,
                center_x=column * util.WORLD_WIDTH // 5 + (3/2 * planet_size),
                center_y=y_start_point - row * util.WORLD_HEIGHT // 4))

    def update(self):
        self.level_names = []
        self.planets = []
        self.planet_filenames = []
        self.filenames = []

        if self.is_community:
            metadata = util.get_level_metadata(page=self.current_page, is_community=True)
        else:
            metadata = util.get_level_metadata(page=self.current_page)

        self.levels = metadata[1]
        self.filenames = metadata[2]

        for i in range(0, len(self.levels)):
            self.level_names.append(self.levels[i]["level_name"])

        for i in range(0, len(self.levels)):
            self.planet_filenames.append(self.levels[i]["planet_name"] + ".png")

        for index in range(0, len(self.levels)):
            column = index % 5
            row = index // 5
            y_start_point = util.WORLD_HEIGHT - util.WORLD_HEIGHT // 4 - (3 / 2 * planet_size)
            self.planets.append(util.load_sprite(
                self.planet_filenames[index],
                scale=2,
                center_x=column * util.WORLD_WIDTH // 5 + (3 / 2 * planet_size),
                center_y=y_start_point - row * util.WORLD_HEIGHT // 4))

    def draw(self):
        arcade.draw_text(self.title,
                         util.WORLD_WIDTH // 2,
                         util.WORLD_HEIGHT - util.H3_FONT_SIZE,
                         font_size=util.H3_FONT_SIZE,
                         anchor_x="center",
                         anchor_y="top",
                         color=arcade.color.RED,
                         font_name=util.MENU_FONT
                         )

        for index, key in enumerate(self.keys):
            key.draw()
            arcade.draw_text(self.key_text[index][0],
                             start_x=key.center_x,
                             start_y=key.center_y,
                             anchor_x="center",
                             anchor_y="center",
                             color=arcade.color.GRAY,
                             font_name=util.MENU_FONT,
                             font_size=util.BODY_FONT_SIZE if index != 1 else util.BODY_FONT_SIZE-4)
            arcade.draw_text(self.key_text[index][1],
                             start_x=key.center_x + 32 + 10,
                             start_y=key.center_y,
                             anchor_x="left",
                             anchor_y="center",
                             color=arcade.color.YELLOW,
                             font_name=util.MENU_FONT,
                             font_size=util.BODY_FONT_SIZE)

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

    def load_selection(self) -> Level:
        is_system = not self.is_community
        print(self.filenames[self.selection])
        return load_level(util.load_data(self.filenames[self.selection], True, is_system), character, enemy)
