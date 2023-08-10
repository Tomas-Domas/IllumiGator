import numpy

from illumigator import worldobjects, entity, util, light, geometry

class Level:
    def __init__(
            self,
            wall_coordinate_list=(),
            mirror_coordinate_list=(),
            light_receiver_coordinate_list=(),
            light_source_coordinate_list=(),
            animated_wall_coordinate_list=(),
            lens_coordinate_list=(),
            gator_coordinates=(640, 360),
            enemy_coordinates=(),
            name="default",
            background="space",
            planet="moon",
            walking_volume=1
    ):

        if name == "Level 1":
            background = "level1_background"

        self.background = background + ".png"
        self.background_sprite = util.load_sprite(self.background, scale=2/3, center_x=util.WORLD_WIDTH // 2, center_y=util.WORLD_HEIGHT // 2)
        self.background_sprite.alpha = 100  # out of 255
        self.planet = planet
        self.name = name

        self.line_segments = []

        self.wall_list = []
        self.mirror_list = []
        self.lens_list = []
        self.light_receiver_list = []
        self.light_source_list = []
        self.create_border_walls()


        for wall_coordinates in wall_coordinate_list:
            self.add_world_object(
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
            self.add_world_object(
                worldobjects.Mirror(
                    numpy.array([
                        mirror_coordinates[0], mirror_coordinates[1]
                    ]),
                    mirror_coordinates[2],
                )
            )
        for lens_coordinates in lens_coordinate_list:
            self.add_world_object(
                worldobjects.Lens(
                    numpy.array([
                        lens_coordinates[0],
                        lens_coordinates[1]
                    ]),
                    lens_coordinates[2]
                )
            )
        for light_receiver_coordinates in light_receiver_coordinate_list:
            self.add_world_object(
                worldobjects.LightReceiver(
                    numpy.array([
                        light_receiver_coordinates[0], light_receiver_coordinates[1]
                    ]),
                    light_receiver_coordinates[2],
                    planet=self.planet
                )
            )
        for light_source_coordinates in light_source_coordinate_list:
            if len(light_source_coordinates) == 4:  # Has an angular spread argument
                self.add_world_object(
                    worldobjects.RadialLightSource(
                        numpy.array(
                            [light_source_coordinates[0], light_source_coordinates[1]]
                        ),
                        light_source_coordinates[2],
                        light_source_coordinates[3],
                    )
                )
            else:
                self.add_world_object(
                    worldobjects.ParallelLightSource(
                        numpy.array(
                            [light_source_coordinates[0], light_source_coordinates[1]]
                        ),
                        light_source_coordinates[2],
                    )
                )
        for animated_wall_coordinates in animated_wall_coordinate_list:
            self.add_world_object(
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
            self.wall_list[-1].create_animation(
                numpy.array([animated_wall_coordinates[5], animated_wall_coordinates[6]]),
                animated_wall_coordinates[7], animated_wall_coordinates[8])

        # Create entities
        self.entity_world_object_list: list[worldobjects.WorldObject] = []
        if len(enemy_coordinates) == 0:
            self.enemy = None
        else:
            self.create_enemy(enemy_coordinates)
        self.gator = entity.Gator(gator_coordinates, walking_volume)
        self.entity_world_object_list.append(self.gator.world_object)
        self.line_segments.extend(self.gator.world_object.geometry_segments)


    def update(self, walking_volume, ignore_checks=False):
        if not ignore_checks:
            if self.enemy is not None:
                self.enemy.update(self, self.gator)

            self.gator.update(self, walking_volume, self.enemy)
            if self.gator.status == "dying":
                # Show dead animations
                self.gator.left_character_loader.dead = True
                self.gator.right_character_loader.dead = True

            for wall in self.wall_list:
                if wall.obj_animation is not None:
                    wall.apply_object_animation(self.gator, self.enemy)
            for light_receiver in self.light_receiver_list:
                light_receiver.charge *= util.CHARGE_DECAY

        self.raycast(ignore_checks)

    def raycast(self, ignore_checks: bool):
        # Prep coordinates for intersection calculations
        line_p1 = numpy.ndarray((len(self.line_segments), 2))
        line_p2 = numpy.ndarray((len(self.line_segments), 2))
        for line_i in range(len(self.line_segments)):
            line_p1[line_i], line_p2[line_i] = self.line_segments[line_i]._point1, self.line_segments[line_i]._point2

        for light_source in self.light_source_list:
            # Add Rays to a queue
            ray_queue = light_source.light_rays[:]
            queue_length = len(ray_queue)
            while queue_length > 0:
                # Prep coordinates for intersection calculations
                ray_origin = numpy.ndarray((queue_length, 2))
                ray_dir = numpy.ndarray((queue_length, 2))
                for ray_i in range(queue_length):
                    ray_origin[ray_i], ray_dir[ray_i] = ray_queue[ray_i].origin, ray_queue[ray_i].direction

                # Calculate intersections (lists of distance and intersection object for each light ray)
                nearest_distances, nearest_indices = light.calculate_intersections(ray_origin, ray_dir, line_p1, line_p2)

                for i in range(queue_length):
                    ray: light.LightRay = ray_queue[i]
                    nearest_line: geometry.Line = self.line_segments[int(nearest_indices[i])]
                    # Update ray endpoint
                    ray._end = ray.origin + ray.direction * nearest_distances[i]

                    # Decide light ray behavior based on intersection object
                    if ray.generation >= util.MAX_GENERATIONS:
                        ray.child_ray = None
                        continue
                    if nearest_line.is_reflective:  # if the ray hit a mirror, create child and cast it
                        ray.generate_child_ray(ray.get_reflected_direction(nearest_line))
                        ray_queue.append(ray.child_ray)
                        continue
                    elif nearest_line.is_refractive:
                        print("LENS!")
                        ray.child_ray = None
                        continue
                    ray.child_ray = None

                    # Update level based on intersection object
                    if ignore_checks:
                        continue

                    elif nearest_line.is_receiver:  # Charge receiver when a light ray hits it
                        nearest_line.parent_object.charge += util.LIGHT_INCREMENT
                    elif nearest_line.is_enemy and self.enemy.status != "aggro":
                        self.enemy.status = "aggro"
                        self.enemy.update_geometry_shape()


                ray_queue = ray_queue[queue_length:]
                queue_length = len(ray_queue)

    def draw(self):
        self.background_sprite.draw(pixelated=True)
        for light_source in self.light_source_list:
            light_source.draw()
        for wall in self.wall_list:
            wall.draw()
        for mirror in self.mirror_list:
            mirror.draw()
        for lens in self.lens_list:
            lens.draw()
        for light_receiver in self.light_receiver_list:
            light_receiver.draw()
        self.gator.draw()
        if self.enemy is not None:
            self.enemy.draw()

    def check_collisions(self, character: entity.Gator):
        for wo in self.wall_list + self.mirror_list + self.lens_list + self.light_receiver_list + self.light_source_list:
            if wo.check_collision_with_sprite(character.sprite):
                return True
        else:
            return False

    def add_world_object(self, world_object):
        match world_object:
            case worldobjects.Lens():  # Lens
                self.lens_list.append(world_object)
            case worldobjects.Wall():  # Wall
                self.wall_list.append(world_object)
            case worldobjects.Mirror():  # Mirror
                self.mirror_list.append(world_object)
            case worldobjects.ParallelLightSource():  # Source
                self.light_source_list.append(world_object)
            case worldobjects.LightReceiver():  # Receiver
                self.light_receiver_list.append(world_object)
        self.line_segments.extend(world_object.geometry_segments)

    def remove_world_object(self, world_object):
        match world_object:
            case worldobjects.Lens():  # Lens
                self.lens_list.remove(world_object)
            case worldobjects.Wall():  # Wall
                self.wall_list.remove(world_object)
            case worldobjects.Mirror():  # Mirror
                self.mirror_list.remove(world_object)
            case worldobjects.ParallelLightSource():  # Source
                self.light_source_list.remove(world_object)
            case worldobjects.LightReceiver():  # Receiver
                self.light_receiver_list.remove(world_object)
        for geometry_segment in world_object.geometry_segments:
            self.line_segments.remove(geometry_segment)

    def create_enemy(self, position):
        self.enemy = entity.Enemy(position)
        self.entity_world_object_list.append(self.enemy.world_object)
        self.line_segments.extend(self.enemy.world_object.geometry_segments)

    def delete_enemy(self):
        for geometry_segment in self.enemy.world_object.geometry_segments:
            self.line_segments.remove(geometry_segment)
        self.enemy = None

    def create_border_walls(self):
        self.add_world_object(worldobjects.Wall(
            numpy.array([util.WALL_SIZE / 2, 720 / 2]),
            numpy.array([1, 720 / util.WALL_SIZE]),
            0
        ))
        self.add_world_object(worldobjects.Wall(
            numpy.array([1280 - util.WALL_SIZE / 2, 720 / 2]),
            numpy.array([1, 720 / util.WALL_SIZE]),
            0
        ))
        self.add_world_object(worldobjects.Wall(
            numpy.array([1280 / 2, util.WALL_SIZE / 2]),
            numpy.array([1280 / util.WALL_SIZE - 2, 1]),
            0
        ))
        self.add_world_object(worldobjects.Wall(
            numpy.array([1280 / 2, 720 - util.WALL_SIZE / 2]),
            numpy.array([1280 / util.WALL_SIZE - 2, 1]),
            0
        ))


def load_level(level: dict, walking_volume) -> Level:
    level_data = level["level_data"]
    return Level(
        level_data["wall_coordinate_list"],
        level_data["mirror_coordinate_list"],
        level_data["light_receiver_coordinate_list"],
        level_data["light_source_coordinate_list"],
        level_data["animated_wall_coordinate_list"],
        level_data["lens_coordinate_list"],
        level_data["gator_coordinates"],
        level_data["enemy_coordinates"],
        level["level_name"],
        planet=level["planet"],
        walking_volume=walking_volume
    )



class LevelCreator:
    def __init__(self, level):
        self.level: Level = level
        self.selected_world_object: worldobjects.WorldObject | None = None

        self.wall_dimensions = numpy.ones(2)
        self.enemy_exists = False
        self.selected_entity: entity.Gator | entity.Enemy | None = None

        self.snap_to_grid: bool = True
        self.nearest_grid_position = None

        self.queued_type_selection = -1
        self.queued_rotation = 0

    def get_position(self, mouse_position: numpy.ndarray):
        if self.snap_to_grid:
            grid_pos = numpy.array([
                mouse_position[0] // util.WALL_SIZE + 1,
                mouse_position[1] // util.WALL_SIZE + 1
            ])
            if self.wall_dimensions[0] % 2 == 1:
                grid_pos[0] -= 0.5
            if self.wall_dimensions[1] % 2 == 1:
                grid_pos[1] -= 0.5
            return util.WALL_SIZE * grid_pos

        else:
            return mouse_position

    def resize_wall(self, mouse_position, dx, dy):
        if 1 <= self.wall_dimensions[0]+dx <= 34:
            self.wall_dimensions[0] += dx
        else:
            return
        if 1 <= self.wall_dimensions[1]+dy <= 20:
            self.wall_dimensions[1] += dy
        else:
            return
        self.level.wall_list.remove(self.selected_world_object)
        for geometry_segment in self.selected_world_object.geometry_segments:
            self.level.line_segments.remove(geometry_segment)
        self.selected_world_object = worldobjects.Wall(self.get_position(mouse_position), self.wall_dimensions, self.selected_world_object.rotation_angle)
        self.level.wall_list.append(self.selected_world_object)
        self.level.line_segments.extend(self.selected_world_object.geometry_segments)

    def on_click(self, mouse_position: numpy.ndarray, button):
        if button == 1:
            if self.selected_entity is None and self.selected_world_object is None:
                # Check for click on entities
                if self.level.gator.sprite.collides_with_point(mouse_position):
                    self.selected_entity = self.level.gator
                    return
                if self.level.enemy is not None and self.level.enemy.sprite.collides_with_point(mouse_position):
                    self.selected_entity = self.level.enemy
                    return

                # Check for click on world objects
                for wo in self.level.wall_list + self.level.mirror_list + self.level.lens_list + self.level.light_receiver_list + self.level.light_source_list:
                    if wo.check_collision_with_point(mouse_position):
                        self.selected_world_object = wo
                        match self.selected_world_object:
                            case worldobjects.Wall():  # Wall
                                self.selected_world_object_list = self.level.wall_list
                                self.selected_geometry_list = self.level.line_segments
                            case worldobjects.Mirror():  # Mirror
                                self.selected_world_object_list = self.level.mirror_list
                                self.selected_geometry_list = self.level.line_segments
                            case worldobjects.Lens():  # Lens
                                self.selected_world_object_list = self.level.lens_list
                                self.selected_geometry_list = self.level.line_segments
                            case worldobjects.ParallelLightSource():  # Source
                                self.selected_world_object_list = self.level.light_source_list
                                self.selected_geometry_list = self.level.line_segments
                            case worldobjects.LightReceiver():  # Receiver
                                self.selected_world_object_list = self.level.light_receiver_list
                                self.selected_geometry_list = self.level.line_segments
                        self.wall_dimensions = wo.dimensions if type(wo) == worldobjects.Wall else numpy.ones(2)
                        return
            else:
                self.selected_world_object = None
                self.selected_entity = None

        if button == 4:
            if self.selected_world_object is not None:
                self.level.remove_world_object(self.selected_world_object)
                self.selected_world_object = None
            elif self.selected_entity is not None:
                if self.selected_entity is self.level.enemy:
                    self.level.delete_enemy()
                self.selected_entity = None


    def update(self, mouse_position):
        cursor_position = self.get_position(mouse_position)

        # MOVE OBJECT TO MOUSE
        if self.selected_world_object is not None:
            if type(self.selected_world_object) == worldobjects.ParallelLightSource or type(self.selected_world_object) == worldobjects.RadialLightSource:
                self.selected_world_object.move(
                    cursor_position - self.selected_world_object.position,
                    self.queued_rotation * numpy.pi/12
                )
            else:
                self.selected_world_object.move_if_safe(
                    None, None,
                    cursor_position - self.selected_world_object.position,
                    self.queued_rotation * numpy.pi / 12,
                    ignore_checks=True
                )

        # MOVE ENTITY TO MOUSE
        elif self.selected_entity is not None:
            self.selected_entity.move_to(cursor_position)

        self.queued_rotation = 0
        # GENERATE OBJECT
        match self.queued_type_selection:
            case 6:  # Enemy
                if self.selected_world_object is not None:
                    self.level.remove_world_object(self.selected_world_object)
                    self.selected_world_object = None
                if not self.enemy_exists:
                    self.enemy_exists = True
                    self.level.create_enemy(cursor_position)
                self.selected_entity = self.level.enemy
                self.selected_world_object = None
                self.queued_type_selection = -1
                return
            case 1:  # Wall
                if self.selected_world_object is not None:
                    self.level.remove_world_object(self.selected_world_object)
                elif self.selected_entity is not None and self.selected_entity is self.level.enemy:
                    self.level.delete_enemy()
                self.wall_dimensions = numpy.ones(2)
                self.selected_world_object = worldobjects.Wall(cursor_position, self.wall_dimensions, 0)
            case 2:  # Mirror
                if self.selected_world_object is not None:
                    self.level.remove_world_object(self.selected_world_object)
                elif self.selected_entity is not None and self.selected_entity is self.level.enemy:
                    self.level.delete_enemy()
                self.selected_world_object = worldobjects.Mirror(cursor_position, 0)
            case 3:  # Lens
                if self.selected_world_object is not None:
                    self.level.remove_world_object(self.selected_world_object)
                elif self.selected_entity is not None and self.selected_entity is self.level.enemy:
                    self.level.delete_enemy()
                self.selected_world_object = worldobjects.Lens(cursor_position, 0)
            case 4:  # Source
                if self.selected_world_object is not None:
                    self.level.remove_world_object(self.selected_world_object)
                elif self.selected_entity is not None and self.selected_entity is self.level.enemy:
                    self.level.delete_enemy()
                self.selected_world_object = worldobjects.ParallelLightSource(cursor_position, 0)
            case 5:  # Receiver
                if self.selected_world_object is not None:
                    self.level.remove_world_object(self.selected_world_object)
                elif self.selected_entity is not None and self.selected_entity is self.level.enemy:
                    self.level.delete_enemy()
                self.selected_world_object = worldobjects.LightReceiver(cursor_position, 0)
            case _:  # No Selection
                return
        self.level.add_world_object(self.selected_world_object)
        self.selected_entity = None
        self.queued_type_selection = -1

    def export_level_as_file(self, level_name: str = "My Level", file_name: str = "my_level.json"):
        level_obj = {
            "level_name": level_name,
            "planet": "moon",
            "level_data": {
                "mirror_coordinate_list": [[*wo.position, wo.rotation_angle] for wo in self.level.mirror_list],
                "wall_coordinate_list": [[*wo.position, *wo.dimensions, wo.rotation_angle] for wo in self.level.wall_list],
                "light_receiver_coordinate_list": [[*wo.position, wo.rotation_angle] for wo in self.level.light_receiver_list],
                "light_source_coordinate_list": [[*wo.position, wo.rotation_angle] for wo in self.level.light_source_list],
                "animated_wall_coordinate_list": [],
                "lens_coordinate_list": [[*wo.position, wo.rotation_angle] for wo in self.level.lens_list],
                "gator_coordinates": [self.level.gator.sprite.center_x, self.level.gator.sprite.center_y],
                "enemy_coordinates":
                    [self.level.enemy.sprite.center_x, self.level.enemy.sprite.center_y] if self.level.enemy is not None else []
            }
        }
        util.write_data(f'levels/community/{file_name}', level_obj)
