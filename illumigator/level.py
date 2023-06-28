import numpy

from illumigator import util
from illumigator import worldobjects
from illumigator import entity
from illumigator import util


class Level:
    def __init__(
            self,
            wall_coordinate_list: list[list],
            mirror_coordinate_list: list[list],
            light_receiver_coordinate_list: list[list],
            light_source_coordinate_list: list[list],
            name='default'
    ):
        self.background = None
        self.name = name

        self.mirror_list = []
        self.light_receiver_list = []
        self.light_sources_list = []

        wall_size = util.WALL_SPRITE_INFO[1] * util.WALL_SPRITE_INFO[2]
        self.wall_list: list[worldobjects.WorldObject] = [
            worldobjects.Wall(
                numpy.array([wall_size*0.5, util.WINDOW_HEIGHT*0.5 - wall_size*0.25]),
                numpy.array([1, util.WINDOW_HEIGHT//wall_size + 1]), 0
            ),
            worldobjects.Wall(
                numpy.array([util.WINDOW_WIDTH - wall_size*0.5, util.WINDOW_HEIGHT*0.5 - wall_size*0.25]),
                numpy.array([1, util.WINDOW_HEIGHT//wall_size + 1]), 0
            ),
            worldobjects.Wall(
                numpy.array([util.WINDOW_WIDTH*0.5, wall_size*0.5]),
                numpy.array([util.WINDOW_WIDTH//wall_size - 2, 1]), 0
            ),
            worldobjects.Wall(
                numpy.array([util.WINDOW_WIDTH*0.5, util.WINDOW_HEIGHT - wall_size*0.5]),
                numpy.array([util.WINDOW_WIDTH//wall_size - 2, 1]), 0
            ),
        ]
        # Animated Wall:
        animated_wall = worldobjects.Wall(
                numpy.array([util.WINDOW_WIDTH-176, util.WINDOW_HEIGHT-240]),
                numpy.array([1, 1]), 0
            )
        animated_wall.create_animation(numpy.array([128, 0]), 0.02)
        self.wall_list.append(animated_wall)

        for wall_coordinates in wall_coordinate_list:
            self.wall_list.append(worldobjects.Wall(
                numpy.array([wall_coordinates[0], wall_coordinates[1]]),
                numpy.array([wall_coordinates[2], wall_coordinates[3]]),
                wall_coordinates[4]
            ))

        for mirror_coordinates in mirror_coordinate_list:
            self.mirror_list.append(worldobjects.Mirror(
                numpy.array([mirror_coordinates[0], mirror_coordinates[1]]),
                mirror_coordinates[2]
            ))

        for light_receiver_coordinates in light_receiver_coordinate_list:
            self.light_receiver_list.append(worldobjects.LightReceiver(
                numpy.array([light_receiver_coordinates[0], light_receiver_coordinates[1]]),
                light_receiver_coordinates[2]
            ))

        for light_source_coordinates in light_source_coordinate_list:
            if len(light_source_coordinates) == 4:  # Has an angular spread argument
                self.light_sources_list.append(worldobjects.RadialLightSource(
                    numpy.array([light_source_coordinates[0], light_source_coordinates[1]]),
                    light_source_coordinates[2],
                    light_source_coordinates[3])
                )
            else:
                self.light_sources_list.append(worldobjects.ParallelLightSource(
                    numpy.array([light_source_coordinates[0], light_source_coordinates[1]]),
                    light_source_coordinates[2]))

    def update(self, character: entity.Character):
        for wall in self.wall_list:
            if wall.obj_animation is not None:
                wall.apply_object_animation(character)
        for light_source in self.light_sources_list:
            light_source.cast_rays(self.wall_list + self.mirror_list + self.light_receiver_list +
                                   self.light_sources_list)
        for light_receiver in self.light_receiver_list:
            light_receiver.charge *= util.CHARGE_DECAY

    def draw(self):
        for wall in self.wall_list:
            wall.draw()
        for mirror in self.mirror_list:
            mirror.draw()
        for light_source in self.light_sources_list:
            light_source.draw()
        for light_receiver in self.light_receiver_list:
            light_receiver.draw()

    def check_collisions(self, character: entity.Character):
        for wall in self.wall_list:
            if wall.check_collision(character.character_sprite):
                return True
        for mirror in self.mirror_list:
            if mirror.check_collision(character.character_sprite):
                return True
        for light_receiver in self.light_receiver_list:
            if light_receiver.check_collision(character.character_sprite):
                return True
