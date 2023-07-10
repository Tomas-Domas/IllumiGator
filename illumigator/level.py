import numpy

from illumigator import worldobjects, geometry, entity, util


class Level:
    def __init__(
        self,
        wall_coordinate_list: list[list] = None,
        mirror_coordinate_list: list[list] = None,
        light_receiver_coordinate_list: list[list] = None,
        light_source_coordinate_list: list[list] = None,
        name="default",
        #TODO: implement scaling option for loading level
        scale=1
    ):
        self.background = None
        self.name = name

        self.mirror_list = []
        self.light_receiver_list = []
        self.light_sources_list = []

        wall_size = util.WALL_SPRITE_INFO[1] * util.WALL_SPRITE_INFO[2]
        self.wall_list: list[worldobjects.WorldObject] = [
            worldobjects.Wall(
                numpy.array(
                    [wall_size * 0.5, util.WINDOW_HEIGHT * 0.5 - wall_size * 0.25]
                ),
                numpy.array([1, util.WINDOW_HEIGHT // wall_size + 1]),
                0,
            ),
            worldobjects.Wall(
                numpy.array([util.WINDOW_WIDTH - wall_size * 0.5, util.WINDOW_HEIGHT * 0.5 - wall_size * 0.25]),
                numpy.array([1, util.WINDOW_HEIGHT // wall_size + 1]),
                0,
            ),
            worldobjects.Wall(
                numpy.array([util.WINDOW_WIDTH * 0.5, wall_size * 0.5]),
                numpy.array([util.WINDOW_WIDTH // wall_size - 2, 1]),
                0,
            ),
            worldobjects.Wall(
                numpy.array([util.WINDOW_WIDTH * 0.5, util.WINDOW_HEIGHT - wall_size * 0.5]),
                numpy.array([util.WINDOW_WIDTH // wall_size - 2, 1]),
                0,
            ),
        ]

        for wall_coordinates in wall_coordinate_list:  # TODO: Handle animated walls somehow. For now they're hand-made in the functions
            self.wall_list.append(
                worldobjects.Wall(
                    numpy.array([
                        wall_coordinates[0],
                        wall_coordinates[1]
                    ]),
                    numpy.array([
                        wall_coordinates[2],
                        wall_coordinates[3]
                    ]),
                    wall_coordinates[4],
                )
            )

        for mirror_coordinates in mirror_coordinate_list:
            self.mirror_list.append(
                worldobjects.Mirror(
                    numpy.array([
                        mirror_coordinates[0], mirror_coordinates[1]
                    ]),
                    mirror_coordinates[2],
                )
            )

        for light_receiver_coordinates in light_receiver_coordinate_list:
            self.light_receiver_list.append(
                worldobjects.LightReceiver(
                    numpy.array([
                        light_receiver_coordinates[0], light_receiver_coordinates[1]
                    ]),
                    light_receiver_coordinates[2]
                )
            )

        for light_source_coordinates in light_source_coordinate_list:
            if len(light_source_coordinates) == 4:  # Has an angular spread argument
                self.light_sources_list.append(
                    worldobjects.RadialLightSource(
                        numpy.array(
                            [light_source_coordinates[0], light_source_coordinates[1]]
                        ),
                        light_source_coordinates[2],
                        light_source_coordinates[3],
                    )
                )
            else:
                self.light_sources_list.append(
                    worldobjects.ParallelLightSource(
                        numpy.array(
                            [light_source_coordinates[0], light_source_coordinates[1]]
                        ),
                        light_source_coordinates[2],
                    )
                )

    def update(self, character: entity.Character, mouse_x, mouse_y):
        for wall in self.wall_list:
            if wall.obj_animation is not None:
                wall.apply_object_animation(character)
        for light_source in self.light_sources_list:
            if util.DEBUG_LIGHT_SOURCES:
                light_source.move(
                    numpy.array([
                        mouse_x - light_source._position[0],
                        mouse_y - light_source._position[1],
                    ])
                )
            light_source.cast_rays(
                self.wall_list +
                self.mirror_list +
                self.light_receiver_list +
                self.light_sources_list
            )
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


def load_level1() -> Level:  # TODO: Load from JSON files
    mirror_coordinate_list = [
        [util.WINDOW_WIDTH / 4, (util.WINDOW_HEIGHT / 3) * 2, -numpy.pi / 4],
        [(util.WINDOW_WIDTH / 2) + 50, util.WINDOW_HEIGHT - 100, 0],
        [util.WINDOW_WIDTH / 2, util.WINDOW_HEIGHT / 4, numpy.pi / 2],
        [((util.WINDOW_WIDTH / 4) * 3) + 20, util.WINDOW_HEIGHT / 5, 0]
    ]
    wall_coordinate_list = [
        [784, 176, 1, 9, 0],
        [496, util.WINDOW_HEIGHT - 176, 1, 9, 0],
        [880, util.WINDOW_HEIGHT - 176, 1, 9, 0]
    ]
    light_receiver_coordinate_list = [
        [util.WINDOW_WIDTH - 128, util.WINDOW_HEIGHT - 128, 0],
    ]
    light_source_coordinate_list = [
        # A 4th argument will make RadialLightSource with that angular spread instead of ParallelLightSource
        [util.WINDOW_WIDTH / 4, 48, numpy.pi / 2]
    ]

    lvl = Level(
        wall_coordinate_list,
        mirror_coordinate_list,
        light_receiver_coordinate_list,
        light_source_coordinate_list
    )

    # Animated Wall: # TODO: Handle animated walls with level generation. For now, they're hand-made
    animated_wall = worldobjects.Wall(
        numpy.array([util.WINDOW_WIDTH - 176, util.WINDOW_HEIGHT - 240]),
        numpy.array([1, 1]),
        0,
    )
    animated_wall.create_animation(numpy.array([128, 0]), 0.02, numpy.pi)
    lvl.wall_list.append(animated_wall)

    return lvl


def load_test_level():
    wall_coordinate_list = []
    light_source_coordinate_list = [
        [util.WINDOW_WIDTH / 4, 48, numpy.pi / 2, numpy.pi * 2]
    ]
    light_receiver_coordinate_list = []
    mirror_coordinate_list = []

    lvl = Level(
        wall_coordinate_list,
        mirror_coordinate_list,
        light_receiver_coordinate_list,
        light_source_coordinate_list
    )

    lvl.wall_list[0]._geometry_segments.append(
        geometry.Arc(numpy.array([util.WINDOW_WIDTH/2, util.WINDOW_HEIGHT/2]), 200, numpy.pi/2, numpy.pi)
    )
    lvl.wall_list[0]._geometry_segments.append(
        geometry.Arc(numpy.array([util.WINDOW_WIDTH/2, util.WINDOW_HEIGHT/2]), 200, -numpy.pi/2, numpy.pi)
    )

    return lvl
