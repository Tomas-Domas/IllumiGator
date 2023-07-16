import arcade
from illumigator import util

x_midpoint = util.WORLD_WIDTH // 2
y_midpoint = util.WORLD_HEIGHT // 2


class LevelSelector:
    def __init__(self, selection=0):
        self._selection = selection
        util.update_community_metadata()
        self.levels = util.get_community_metadata()

        self.level_names = []

        # max one page of data (shouldn't be expensive)
        for i in range(0, len(self.levels)):
            self.level_names.append(self.levels[i]["level_name"])

    def draw(self):
        for index, name in enumerate(self.level_names):
            arcade.draw_text(name if len(name) < 15 else name[:12] + "...",
                             index % 5 * util.WORLD_WIDTH // 5,
                             # Replace util.BODY_FONT_SIZE to use sprite size of planet instead
                             util.WORLD_HEIGHT - index // 5 * (util.WORLD_HEIGHT // 3) - 2 * util.BODY_FONT_SIZE,
                             font_size=util.BODY_FONT_SIZE,
                             font_name=util.MENU_FONT)
