import numpy

from illumigator import worldobjects, entity, util, light
from util import WALL_SIZE, Timer


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


    def update(self, character: entity.Character):
        wallsT = Timer("Walls")
        for wall in self.wall_list:
            if wall.obj_animation is not None:
                wall.apply_object_animation(character)
        wallsT.stop()



        raysT = Timer("RAYCAST")

        line_p1 = numpy.ndarray((len(self.line_segments), 2))
        line_p2 = numpy.ndarray((len(self.line_segments), 2))
        line_reflect = [False] * len(self.line_segments)
        line_len = [0] * len(self.line_segments)
        for line_i in range(len(self.line_segments)):
            line_p1[line_i], line_p2[line_i], line_reflect[line_i], line_len[line_i] = \
                self.line_segments[line_i]._point1, self.line_segments[line_i]._point2, self.line_segments[line_i].is_reflective, self.line_segments[line_i]._length

        raysT.lap("Lines Prep")

        for light_source in self.light_sources_list:
            ray_queue = light_source.light_rays[:]
            queue_length = len(ray_queue)

            while queue_length > 0:
                ray_p1 = numpy.ndarray((queue_length, 2))
                ray_dir = numpy.ndarray((queue_length, 2))
                for ray_i in range(queue_length):
                    ray_p1[ray_i], ray_dir[ray_i] = ray_queue[ray_i]._origin, ray_queue[ray_i]._direction

                raysT.lap("  Rays Prep")
                nearest_distances, nearest_line_indeces = light.get_raycast_results(ray_p1, ray_dir, line_p1, line_p2, line_reflect, line_len)
                raysT.lap("  Raycast Results")

                new_ray_endpoints = ray_p1 + (nearest_distances * ray_dir.T).T

                for i in range(queue_length):
                    ray = ray_queue[i]
                    nearest_line = self.line_segments[nearest_line_indeces[i]]
                    ray._end = new_ray_endpoints[i]
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

                raysT.lap("  Rays Update")

                ray_queue = ray_queue[queue_length:]
                queue_length = len(ray_queue)

                raysT.lap("  Queue Update")
                print()
        del raysT


        receiverT = Timer("Receivers")
        for light_receiver in self.light_receiver_list:
            light_receiver.charge *= util.CHARGE_DECAY
        receiverT.stop()
        print()

    def draw(self):
        for light_source in self.light_sources_list:
            light_source.draw()
        for wall in self.wall_list:
            wall.draw()
        for mirror in self.mirror_list:
            mirror.draw()
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
