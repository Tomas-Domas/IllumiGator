import numpy
import math

from illumigator import worldobjects, entity, util, light
from util import WALL_SIZE


class Level:
    def __init__(
        self,
        wall_coordinate_list: list[list] = None,
        mirror_coordinate_list: list[list] = None,
        light_receiver_coordinate_list: list[list] = None,
        light_source_coordinate_list: list[list] = None,
        animated_wall_coordinate_list: list[list] = None,
        lenses_coordinate_list: list[list] = None,
        name="default",
    ):
        self.background = None
        self.name = name
        self.line_segments = []
        self.arcs = []

        self.mirror_list = []
        self.lens_list = []
        self.light_receiver_list = []
        self.light_sources_list = []
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

        for lens_coordinates in lenses_coordinate_list:
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
        for world_object in (self.wall_list + self.mirror_list + self.light_receiver_list):
            self.line_segments.extend(world_object._geometry_segments)

        for world_object in self.lens_list:
            self.arcs.extend(world_object._geometry_segments)


    def update(self, character: entity.Character):
        for wall in self.wall_list:
            if wall.obj_animation is not None:
                wall.apply_object_animation(character)

        for light_receiver in self.light_receiver_list:
            light_receiver.charge *= util.CHARGE_DECAY


        #  ==================== Raycasting and update rays ====================
        line_coordinates = numpy.ndarray((len(self.line_segments), 4))
        arc_coordinates = numpy.ndarray((len(self.arcs), 5))
        for line_i in range(len(self.line_segments)):
            line_coordinates[line_i, :] = self.line_segments[line_i]._point1[0], self.line_segments[line_i]._point1[1], self.line_segments[line_i]._point2[0], self.line_segments[line_i]._point2[1]
        for arc_i in range(len(self.arcs)):
            arc_coordinates[arc_i, :] = self.arcs[arc_i].center[0], self.arcs[arc_i].center[1], self.arcs[arc_i].radius, self.arcs[arc_i]._start_angle, self.arcs[arc_i]._end_angle
        line_x1, line_y1, line_x2, line_y2 = line_coordinates.T
        arc_x, arc_y, arc_r, arc_angle1, arc_angle2 = arc_coordinates.T


        for light_source in self.light_sources_list:
            ray_queue = light_source.light_rays[:]
            queue_length = len(ray_queue)

            while queue_length > 0:
                ray_coordinates = numpy.ndarray((queue_length, 4))
                for ray_i in range(queue_length):
                    ray_coordinates[ray_i, :] = ray_queue[ray_i]._origin[0], ray_queue[ray_i]._origin[1], ray_queue[ray_i]._origin[0] + ray_queue[ray_i]._direction[0], ray_queue[ray_i]._origin[1] + ray_queue[ray_i]._direction[1]
                ray_x1, ray_y1, ray_x2, ray_y2 = ray_coordinates[:, 0], ray_coordinates[:, 1], ray_coordinates[:, 2], ray_coordinates[:, 3]

                # nearest_line_distances, nearest_line_indices = light.get_line_raycast_results(ray_x1, ray_y1, ray_x2, ray_y2, line_x1, line_y1, line_x2, line_y2)






                temp_calculation1_list = [0] * len(ray_queue)
                temp_calculation2_list = [0] * len(ray_queue)
                nabla_list = [0] * len(ray_queue)
                nabla_sqrt_list = [0] * len(ray_queue)
                intersection_distance1_list = [0] * len(ray_queue)
                intersection_distance2_list = [0] * len(ray_queue)
                point1_list = [0] * len(ray_queue)
                point2_list = [0] * len(ray_queue)

                for ray_i in range(len(ray_queue)):
                    ray = ray_queue[ray_i]

                    temp_calculation1 = [0] * len(self.arcs)
                    temp_calculation2 = [0] * len(self.arcs)
                    nabla = [0] * len(self.arcs)
                    nabla_sqrt = [0] * len(self.arcs)
                    intersection_distance1 = [0] * len(self.arcs)
                    intersection_distance2 = [0] * len(self.arcs)
                    point1 = [0] * len(self.arcs)
                    point2 = [0] * len(self.arcs)
                    for arc_i in range(len(self.arcs)):
                        arc = self.arcs[arc_i]

                        temp_calculation1[arc_i] = ray._direction @ (ray._origin - arc.center)
                        temp_calculation2[arc_i] = numpy.linalg.norm(ray._origin - arc.center)
                        nabla[arc_i] = (temp_calculation1[arc_i] * temp_calculation1[arc_i]) - (
                                (temp_calculation2[arc_i] * temp_calculation2[arc_i]) - arc.radius * arc.radius
                        )
                        if nabla[arc_i] < 0:
                            nabla[arc_i] = float('inf')

                        nabla_sqrt[arc_i] = math.sqrt(nabla[arc_i])
                        intersection_distance1[arc_i] = -nabla_sqrt[arc_i] - temp_calculation1[arc_i]
                        intersection_distance2[arc_i] = nabla_sqrt[arc_i] - temp_calculation1[arc_i]

                        point1_angle, point2_angle = None, None

                        if intersection_distance1[arc_i] > 0:
                            point1[arc_i] = ray._origin + intersection_distance1[arc_i] * ray._direction
                            point1_angle = math.atan2(
                                point1[arc_i][1] - arc.center[1], point1[arc_i][0] - arc.center[0]
                            )
                            if not ((arc._start_angle < point1_angle < arc._end_angle) or
                                    (arc._end_angle < arc._start_angle and
                                     (0 <= arc._start_angle <= point1_angle or point1_angle <= arc._end_angle <= 0))):
                                point1[arc_i] = None
                        if intersection_distance2[arc_i] > 0:
                            point2[arc_i] = ray._origin + intersection_distance2[arc_i] * ray._direction
                            point2_angle = math.atan2(
                                point2[arc_i][1] - arc.center[1], point2[arc_i][0] - arc.center[0]
                            )
                            if not ((arc._start_angle < point2_angle < arc._end_angle) or
                                    (arc._end_angle < arc._start_angle and
                                     (0 <= arc._start_angle <= point2_angle or point2_angle <= arc._end_angle <= 0))):
                                point2[arc_i] = None

                    temp_calculation1_list[ray_i] = temp_calculation1
                    temp_calculation2_list[ray_i] = temp_calculation2
                    nabla_list[ray_i] = nabla
                    nabla_sqrt_list[ray_i] = nabla_sqrt
                    intersection_distance1_list[ray_i] = intersection_distance1
                    intersection_distance2_list[ray_i] = intersection_distance2
                    point1_list[ray_i] = point1
                    point2_list[ray_i] = point2



                print("CORRECT:\ntemp1")
                # print(temp_calculation1_list)
                # print("temp2")
                # print(temp_calculation2_list)
                # print("nabla")
                # print(nabla_list)
                print("nabla_sqrt")
                print(nabla_sqrt_list)
                print("intersect1")
                print(intersection_distance1_list)
                print("point1 x, y")
                print(point1_list)

                # print("intersect2")
                # print(intersection_distance2_list)
                print()






                nearest_arc_distances, nearest_arc_indices = light.get_arc_raycast_results(ray_x1, ray_y1, ray_x2, ray_y2, arc_x, arc_y, arc_r, arc_angle1, arc_angle2)
                return



                # for i in range(queue_length):
                #     ray = ray_queue[i]
                #     if nearest_distances[i] is float('inf'):
                #         ray._end = ray._origin + ray._direction * util.MAX_RAY_DISTANCE
                #         ray._child_ray = None  # TODO: Make delete bloodline function
                #         continue
                #     nearest_line = self.line_segments[nearest_line_indices[i]]
                #     ray._end = ray._origin + ray._direction * nearest_distances[i]
                #     if nearest_line.is_reflective and ray._generation < util.MAX_GENERATIONS:  # if the ray hit a mirror, create child and cast it
                #         ray._generate_child_ray(nearest_line.get_reflected_direction(ray))
                #         ray_queue.append(ray._child_ray)
                #     # elif nearest_line_index.is_refractive and ray._generation < util.MAX_GENERATIONS:  # if the ray hit a lens, create child and cast it
                #     #     ray._generate_child_ray(nearest_line_index.get_refracted_direction(ray))
                #     #     # ADD TO QUEUE
                #     elif nearest_line.is_receiver:  # Charge receiver when a light ray hits it
                #         nearest_line.parent_object.charge += util.LIGHT_INCREMENT
                #     else:
                #         ray._child_ray = None

                ray_queue = ray_queue[queue_length:]
                queue_length = len(ray_queue)



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
    return Level(
        level_data["wall_coordinate_list"],
        level_data["mirror_coordinate_list"],
        level_data["light_receiver_coordinate_list"],
        level_data["light_source_coordinate_list"],
        level_data["animated_wall_coordinate_list"],
        level_data["lenses_coordinate_list"],
        level["level_name"]
    )
