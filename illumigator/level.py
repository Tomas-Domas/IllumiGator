import numpy

from illumigator import worldobjects, entity, util, light, timer
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
        self.line_segments = []

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
            )
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

        for world_object in (self.wall_list + self.mirror_list + self.light_receiver_list):
            self.line_segments.extend(world_object._geometry_segments)


    def update(self, character: entity.Character, mouse_x, mouse_y):
        for wall in self.wall_list:
            if wall.obj_animation is not None:
                wall.apply_object_animation(character)

        line_coordinates = numpy.ndarray((len(self.line_segments), 4))
        for line_i in range(len(self.line_segments)):
            line_coordinates[line_i, :] = self.line_segments[line_i]._point1[0], self.line_segments[line_i]._point1[1], self.line_segments[line_i]._point2[0], self.line_segments[line_i]._point2[1]

        for light_source in self.light_sources_list:
            ray_queue = light_source.light_rays[:]
            queue_length = len(ray_queue)

            line_x1, line_y1, line_x2, line_y2 = line_coordinates[:, 0], line_coordinates[:, 1], line_coordinates[:, 2], line_coordinates[:, 3]

            while queue_length > 0:
                ray_coordinates = numpy.ndarray((queue_length, 4))
                for ray_i in range(queue_length):
                    ray_coordinates[ray_i, :] = ray_queue[ray_i]._origin[0], ray_queue[ray_i]._origin[1], ray_queue[ray_i]._origin[0] + ray_queue[ray_i]._direction[0], ray_queue[ray_i]._origin[1] + ray_queue[ray_i]._direction[1]
                ray_x1, ray_y1, ray_x2, ray_y2 = ray_coordinates[:, 0], ray_coordinates[:, 1], ray_coordinates[:, 2], ray_coordinates[:, 3]
                ray_casting_results = light.get_raycast_results(ray_x1, ray_y1, ray_x2, ray_y2, line_x1, line_y1, line_x2, line_y2)

                for i in range(queue_length):
                    ray = ray_queue[i]
                    if ray_casting_results[i][0] is float('inf'):
                        ray._end = ray._origin + ray._direction * util.MAX_RAY_DISTANCE
                        ray._child_ray = None  # TODO: Make delete bloodline function
                        continue
                    else:
                        nearest_distance, nearest_line_index = ray_casting_results[i]

                    nearest_line = self.line_segments[int(nearest_line_index)]

                    ray._end = ray._origin + ray._direction * nearest_distance
                    if nearest_line.is_reflective and ray._generation < util.MAX_GENERATIONS:  # if the ray hit a mirror, create child and cast it
                        ray._generate_child_ray(nearest_line.get_reflected_direction(ray))
                        ray_queue.append(ray._child_ray)
                    # elif nearest_line_index.is_refractive and ray._generation < util.MAX_GENERATIONS:  # if the ray hit a lens, create child and cast it
                    #     ray._generate_child_ray(nearest_line_index.get_refracted_direction(ray))
                    #     # ADD TO QUEUE
                    elif nearest_line.is_receiver:  # Charge receiver when a light ray hits it
                        nearest_line.parent_object.charge += util.LIGHT_INCREMENT
                    else:
                        ray._child_ray = None

                ray_queue = ray_queue[queue_length:]
                queue_length = len(ray_queue)


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

def load_level(level: dict) -> Level:
    level_data = level["level_data"]
    return Level(level_data["wall_coordinate_list"],
                 level_data["mirror_coordinate_list"],
                 level_data["light_receiver_coordinate_list"],
                 level_data["light_source_coordinate_list"],
                 level_data["animated_wall_coordinate_list"],
                 level["level_name"])
