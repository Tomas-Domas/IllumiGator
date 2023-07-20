import numpy

from illumigator import worldobjects, entity, util, light
from util import WALL_SIZE, PLAYER_SPRITE_INFO, Timer


class Level:
    def __init__(
            self,
            character: entity.Character,
            enemy: entity.Enemy,
            wall_coordinate_list: list[list] = None,
            mirror_coordinate_list: list[list] = None,
            light_receiver_coordinate_list: list[list] = None,
            light_source_coordinate_list: list[list] = None,
            animated_wall_coordinate_list: list[list] = None,
            lens_coordinate_list: list[list] = None,
            character_coordinates: list = None,
            enemy_coordinates: list = None,
            name="default"
    ):

        self.background = None
        self.name = name
        self.line_segments = []
        self.arcs = []

        self.mirror_list = []
        self.lens_list = []
        self.light_receiver_list = []
        self.light_sources_list = []
        self.entity_world_object_list = []
        self.wall_list: list[worldobjects.WorldObject] = [
            worldobjects.Wall(
                numpy.array([WALL_SIZE / 2, 720 / 2]),
                numpy.array([1, 720 / WALL_SIZE]),
                0,
            ),
            worldobjects.Wall(
                numpy.array([1280 - WALL_SIZE / 2, 720 / 2]),
                numpy.array([1, 720 / WALL_SIZE]),
                0,
            ),
            worldobjects.Wall(
                numpy.array([1280 / 2, WALL_SIZE / 2]),
                numpy.array([1280 / WALL_SIZE - 2, 1]),
                0,
            ),
            worldobjects.Wall(
                numpy.array([1280 / 2, 720 - WALL_SIZE / 2]),
                numpy.array([1280 / WALL_SIZE - 2, 1]),
                0,
            )
        ]

        character.character_sprite.position = numpy.array([character_coordinates[0], character_coordinates[1]])
        character.world_object = worldobjects.WorldObject(
            numpy.array([character_coordinates[0], character_coordinates[1]]),
            0
        )
        character.world_object.initialize_geometry(PLAYER_SPRITE_INFO)
        character.status = "alive"

        enemy.character_sprite.position = numpy.array([enemy_coordinates[0], enemy_coordinates[1]])
        enemy.world_object = worldobjects.WorldObject(
            numpy.array([enemy_coordinates[0], enemy_coordinates[1]]),
            0
        )
        enemy.world_object.initialize_geometry(PLAYER_SPRITE_INFO)
        enemy.state = "asleep"

        self.entity_world_object_list.append(character.world_object)
        self.entity_world_object_list.append(enemy.world_object)

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
            self.wall_list.append(
                worldobjects.Wall(
                    numpy.array([
                        animated_wall_coordinates[0],
                        animated_wall_coordinates[1]
                    ]),
                    numpy.array([
                        animated_wall_coordinates[2],
                        animated_wall_coordinates[3]
                    ]),
                    animated_wall_coordinates[4]
                )
            )
            self.wall_list[-1].create_animation(numpy.array([animated_wall_coordinates[5], animated_wall_coordinates[6]]),
                                           animated_wall_coordinates[7], animated_wall_coordinates[8])

        for lens_coordinates in lens_coordinate_list:
            print(lens_coordinates)
            self.lens_list.append(
                worldobjects.Lens(
                    numpy.array([
                        lens_coordinates[0],
                        lens_coordinates[1]
                    ]),
                    lens_coordinates[2]
                )
            )

        #  Append line segments and arcs to geometry lists
        for world_object in (self.wall_list + self.mirror_list + self.light_receiver_list + self.entity_world_object_list):
            self.line_segments.extend(world_object._geometry_segments)
        for world_object in self.lens_list:
            self.arcs.extend(world_object._geometry_segments)


    def update(self, character: entity.Character):
        for wall in self.wall_list:
            if wall.obj_animation is not None:
                wall.apply_object_animation(character)

        receiverT = Timer("Receivers")
        for light_receiver in self.light_receiver_list:
            light_receiver.charge *= util.CHARGE_DECAY
        receiverT.stop()

        if util.DEBUG_LIGHTS:
            for source in self.light_sources_list:
                source.move(numpy.array([util.mouseX - source._position[0], util.mouseY - source._position[1]]))


        #  ==================== Raycasting and update rays ====================
        raysT = Timer("RAYCAST")

        line_p1 = numpy.ndarray((len(self.line_segments), 2))
        line_p2 = numpy.ndarray((len(self.line_segments), 2))
        for line_i in range(len(self.line_segments)):
            line_p1[line_i], line_p2[line_i] = self.line_segments[line_i]._point1, self.line_segments[line_i]._point2
        arc_center = numpy.ndarray((len(self.arcs), 2))
        arc_radius = numpy.ndarray((len(self.arcs),  ))
        arc_angles = numpy.ndarray((len(self.arcs), 2))
        for arc_i in range(len(self.arcs)):
            arc_center[arc_i], arc_radius[arc_i], arc_angles[arc_i][0], arc_angles[arc_i][1] = self.arcs[arc_i].center, self.arcs[arc_i].radius, self.arcs[arc_i]._start_angle, self.arcs[arc_i]._end_angle

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

                nearest_line_distances, nearest_line_indices = light.get_raycast_results(ray_p1, ray_dir, line_p1, line_p2)

                raysT.lap("  Line Raycast")

                if len(self.arcs) > 0:
                    nearest_arc_distance, nearest_arc_indices = light.get_arc_raycast_results(ray_p1[:, 0], ray_p1[:, 1], ray_dir[:, 0], ray_dir[:, 1], arc_center[:, 0], arc_center[:, 1], arc_radius, arc_angles[:, 0], arc_angles[:, 1])
                    raysT.lap("  Arc Raycast")
                else:
                    nearest_arc_distance, nearest_arc_indices = numpy.full_like(nearest_line_distances, float('inf')), numpy.full_like(nearest_line_distances, -1)

                for i in range(queue_length):
                    ray = ray_queue[i]
                    if nearest_line_distances[i] <= nearest_arc_distance[i]:
                        ray._end = ray._origin + ray._direction * nearest_line_distances[i]
                        nearest_line = self.line_segments[int(nearest_line_indices[i])]
                        if nearest_line.is_reflective and ray._generation < util.MAX_GENERATIONS:  # if the ray hit a mirror, create child and cast it
                            ray._generate_child_ray(nearest_line.get_reflected_direction(ray))
                            # ray._generate_child_ray(numpy.array([-0.8, -0.6]))
                            ray_queue.append(ray._child_ray)
                        elif nearest_line.is_receiver:  # Charge receiver when a light ray hits it
                            nearest_line.parent_object.charge += util.LIGHT_INCREMENT
                        else:
                            ray._child_ray = None
                    else:
                        ray._end = ray._origin + ray._direction * nearest_arc_distance[i]
                        nearest_arc = self.arcs[int(nearest_arc_indices[i])]
                        if nearest_arc.is_refractive and ray._generation < util.MAX_GENERATIONS:  # if the ray hit a lens, create child and cast it
                            try:
                                ray._generate_child_ray(nearest_arc.get_refracted_direction(ray))
                                ray_queue.append(ray._child_ray)
                            except:
                                ray._child_ray = None
                        else:
                            ray._child_ray = None

                raysT.lap("  Rays Update")

                ray_queue = ray_queue[queue_length:]
                queue_length = len(ray_queue)

                raysT.lap("  Queue Update")
                print()
        del ray

    def draw(self):
        for light_source in self.light_sources_list:
            light_source.draw()
        for wall in self.wall_list:
            wall.draw()
        for mirror in self.mirror_list:
            mirror.draw()
        for lens in self.lens_list:
            lens.draw()
        for light_receiver in self.light_receiver_list:
            light_receiver.draw()
        for entity_world_object in self.entity_world_object_list:
            entity_world_object.draw()

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


def load_level(level: dict, character: entity.Character, enemy: entity.Enemy) -> Level:
    level_data = level["level_data"]
    return Level(character,
                 enemy,
                 level_data["wall_coordinate_list"],
                 level_data["mirror_coordinate_list"],
                 level_data["light_receiver_coordinate_list"],
                 level_data["light_source_coordinate_list"],
                 level_data["animated_wall_coordinate_list"],
                 level_data["lens_coordinate_list"],
                 level_data["character_coordinates"],
                 level_data["enemy_coordinates"],
                 level["level_name"])
