import numpy

from illumigator import worldobjects, geometry, entity, util
from util import WALL_SIZE


class Level:
    def __init__(
        self,
        wall_coordinate_list: list[list] = None,
        mirror_coordinate_list: list[list] = None,
        light_receiver_coordinate_list: list[list] = None,
        light_source_coordinate_list: list[list] = None,
        animated_wall_coordinate_list: list[list] = None,
        name="default",
    ):
        self.background = None
        self.name = name

        self.mirror_list = []
        self.light_receiver_list = []
        self.light_sources_list = []

        # ========================= Outer Walls =========================
        self.wall_list: list[worldobjects.WorldObject] = [
            worldobjects.Wall(
                numpy.array([WALL_SIZE/2, 720/2]),
                numpy.array([1, 720/WALL_SIZE]),
                0,
            ),
            worldobjects.Wall(
                numpy.array([1280 - WALL_SIZE/2, 720/2]),
                numpy.array([1, 720/WALL_SIZE]),
                0,
            ),
            worldobjects.Wall(
                numpy.array([1280/2, WALL_SIZE/2]),
                numpy.array([1280/WALL_SIZE - 2, 1]),
                0,
            ),
            worldobjects.Wall(
                numpy.array([1280/2, 720 - WALL_SIZE/2]),
                numpy.array([1280/WALL_SIZE - 2, 1]),
                0,
            ),
        ]

        for wall_coordinates in wall_coordinate_list:
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

        for animated_wall_coordinates in animated_wall_coordinate_list:
            animated_wall = worldobjects.Wall(
                    numpy.array([
                        animated_wall_coordinates[0],
                        animated_wall_coordinates[1]
                    ]),
                    numpy.array([
                        animated_wall_coordinates[2],
                        animated_wall_coordinates[3]
                    ]),
                    animated_wall_coordinates[4])

            animated_wall.create_animation(numpy.array([animated_wall_coordinates[5], animated_wall_coordinates[6]]),
                                           animated_wall_coordinates[7], animated_wall_coordinates[8])

            self.wall_list.append(animated_wall)



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


def load_test_level():
    mirror_coordinate_list = [
        [3.5 * WALL_SIZE, 14.5 * WALL_SIZE, -numpy.pi / 4],
        [8.5 * WALL_SIZE, 4.5 * WALL_SIZE, numpy.pi / 2],
        [18.5 * WALL_SIZE, 14.5 * WALL_SIZE, 0],
        [22.5 * WALL_SIZE, 4.5 * WALL_SIZE, 0]
    ]
    wall_coordinate_list = [

    ]
    light_receiver_coordinate_list = [

    ]
    light_source_coordinate_list = [
        # A 4th argument will make RadialLightSource with that angular spread instead of ParallelLightSource
        [3.5 * WALL_SIZE, 1.5 * WALL_SIZE, numpy.pi / 2]
    ]

    lvl = Level(
        wall_coordinate_list,
        mirror_coordinate_list,
        light_receiver_coordinate_list,
        light_source_coordinate_list
    )

    lvl.wall_list.append(worldobjects.Lens(
        numpy.array([8.5 * WALL_SIZE, 4.5 * WALL_SIZE]),
        0
    ))

    return lvl


def load_level(level: dict) -> Level:
    level_data = level["level_data"]
    return Level(level_data["wall_coordinate_list"],
                 level_data["mirror_coordinate_list"],
                 level_data["light_receiver_coordinate_list"],
                 level_data["light_source_coordinate_list"],
                 level_data["animated_wall_coordinate_list"],
                 level["level_name"])
