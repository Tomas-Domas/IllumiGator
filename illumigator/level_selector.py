from illumigator import util

x_midpoint = util.WORLD_WIDTH // 2
y_midpoint = util.WORLD_HEIGHT // 2


class LevelSelector:
    def __init__(self, selection=0):
        self._selection = selection
        util.update_community_metadata()
