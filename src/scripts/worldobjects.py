import random
import light
from util.util import *
import geometry


class WorldObject:
    position: numpy.array
    rotation_angle: float
    is_interactable: bool
    is_receiver: bool
    geometry_segments: list[geometry.Geometry]

    sprite_list: arcade.SpriteList
    color: tuple[int, int, int]

    def __init__(self, position, rotation_angle, color=random.choice(COLORS), is_interactable=False, is_receiver=False):
        self.position = position
        self.rotation_angle = rotation_angle
        self.is_interactable = is_interactable
        self.is_receiver = is_receiver
        self.geometry_segments = []

        self.sprite_list = arcade.SpriteList()
        self.color = color

    def draw(self):
        for sprite in self.sprite_list:
            sprite.draw()
        for segment in self.geometry_segments:
            segment.draw()

    def move(self, move_distance: numpy.array, rotate_angle: float = 0):
        self.position = self.position + move_distance
        self.rotation_angle = self.rotation_angle + rotate_angle
        for segment in self.geometry_segments:
            segment.move(self.position, move_distance, rotate_angle=rotate_angle)
        for sprite in self.sprite_list:
            new_position = numpy.array([sprite.center_x, sprite.center_y]) + move_distance
            new_position = rotate_around_center(self.position, new_position, rotate_angle)
            sprite.center_x, sprite.center_y = new_position[0], new_position[1]
            sprite.radians += rotate_angle


class Wall(WorldObject):
    def __init__(self, center_position: numpy.array, dimensions: numpy.array, rotation_angle, is_interactable=False):
        super().__init__(center_position, rotation_angle, is_interactable=is_interactable)

        sprite_path, scale_factor, image_width, image_height = WALL_SPRITE_INFO
        side_lengths = dimensions * image_width

        axis1_norm = numpy.array([math.cos(rotation_angle), math.sin(rotation_angle)])
        axis2_norm = numpy.array([-math.sin(rotation_angle), math.cos(rotation_angle)])
        axis1 = side_lengths[0] * 0.5 * axis1_norm
        axis2 = side_lengths[1] * 0.5 * axis2_norm
        self.geometry_segments = [
            geometry.Line(center_position - axis1 - axis2, center_position - axis1 + axis2),
            geometry.Line(center_position - axis1 + axis2, center_position + axis1 + axis2),
            geometry.Line(center_position + axis1 + axis2, center_position + axis1 - axis2),
            geometry.Line(center_position + axis1 - axis2, center_position - axis1 - axis2),
        ]

        for col in range(dimensions[0]):
            for row in range(dimensions[1]):
                sprite_center = center_position - axis1 - axis2 + axis1_norm * (
                        image_width / 2 + col * image_width) + axis2_norm * (image_height / 2 + row * image_height)

                self.sprite_list.append(
                    arcade.Sprite(sprite_path, scale_factor, image_width=image_width, image_height=image_height,
                                  center_x=sprite_center[0], center_y=sprite_center[1],
                                  angle=numpy.rad2deg(rotation_angle), hit_box_algorithm="Simple"
                                  )
                )


class Mirror(WorldObject):
    def __init__(self, center_position: numpy.array, rotation_angle, is_interactable=False):
        super().__init__(center_position, rotation_angle, is_interactable=is_interactable)

        sprite_path, scale_factor, image_width, image_height = MIRROR_SPRITE_INFO
        side_lengths = numpy.array([image_width, image_height])

        axis1_norm = numpy.array([math.cos(rotation_angle), math.sin(rotation_angle)])
        axis2_norm = numpy.array([-math.sin(rotation_angle), math.cos(rotation_angle)])
        axis1 = side_lengths[0] * 0.5 * axis1_norm
        axis2 = side_lengths[1] * 0.5 * axis2_norm
        self.geometry_segments = [
            geometry.Line(center_position - axis1 - axis2, center_position - axis1 + axis2, is_reflective=True),
            geometry.Line(center_position - axis1 + axis2, center_position + axis1 + axis2),
            geometry.Line(center_position + axis1 + axis2, center_position + axis1 - axis2, is_reflective=True),
            geometry.Line(center_position + axis1 - axis2, center_position - axis1 - axis2),
        ]

        sprite_center = center_position - axis1 - axis2 + (image_width / 2) * axis1_norm + (
                image_height / 2) * axis2_norm
        self.sprite_list.append(
            arcade.Sprite(sprite_path, scale_factor, image_width=image_width, image_height=image_height,
                          center_x=sprite_center[0], center_y=sprite_center[1],
                          angle=numpy.rad2deg(rotation_angle), hit_box_algorithm="Simple"
                          )
        )


class LightReceiver(WorldObject):
    def __init__(self, center_position: numpy.array, rotation_angle, is_interactable=False):
        super().__init__(center_position, rotation_angle, is_interactable=is_interactable)

        self.charge = 0
        sprite_path, scale_factor, image_width, image_height = RECEIVER_SPRITE_INFO
        side_lengths = numpy.array([image_width, image_height])

        axis1_norm = numpy.array([math.cos(rotation_angle), math.sin(rotation_angle)])
        axis2_norm = numpy.array([-math.sin(rotation_angle), math.cos(rotation_angle)])
        axis1 = side_lengths[0] * 0.5 * axis1_norm
        axis2 = side_lengths[1] * 0.5 * axis2_norm
        self.geometry_segments = [
            geometry.Line(center_position - axis1 - axis2, center_position - axis1 + axis2),
            geometry.Line(center_position - axis1 + axis2, center_position + axis1 + axis2),
            geometry.Line(center_position + axis1 + axis2, center_position + axis1 - axis2),
            geometry.Line(center_position + axis1 - axis2, center_position - axis1 - axis2),
        ]

        sprite_center = center_position - axis1 - axis2 + (image_width / 2) * axis1_norm + (
                image_height / 2) * axis2_norm
        self.sprite_list.append(
            arcade.Sprite(sprite_path, scale_factor, image_width=image_width, image_height=image_height,
                          center_x=sprite_center[0], center_y=sprite_center[1],
                          angle=numpy.rad2deg(rotation_angle), hit_box_algorithm="Simple"
                          )
        )


class RadialLightSource(WorldObject):
    def __init__(self, position, rotation_angle, angular_spread):
        super().__init__(position, rotation_angle, arcade.color.BLACK)
        self.light_rays = [light.LightRay(numpy.array([0, 0]), numpy.array([0, 0])) for _ in
                           range(NUM_LIGHT_RAYS)]
        self.angular_spread = angular_spread
        self.calculate_light_ray_positions()

    def cast_rays(self, world_objects):
        for ray in self.light_rays:
            ray.cast_ray(world_objects)

    def move(self, move_distance: numpy.array, rotate_angle: float = 0):
        super().move(move_distance, rotate_angle)
        self.calculate_light_ray_positions()

    def calculate_light_ray_positions(self):
        num_rays = len(self.light_rays)
        for n in range(num_rays):
            ray_angle = (n / num_rays) * (self.rotation_angle - self.angular_spread / 2) + (1 - n / num_rays) * (
                    self.rotation_angle + self.angular_spread / 2)
            ray_direction = numpy.array([math.cos(ray_angle), math.sin(ray_angle)])
            self.light_rays[n].origin = self.position
            self.light_rays[n].direction = ray_direction

    def draw(self):
        for ray in self.light_rays:
            ray.draw()
        arcade.draw_circle_filled(self.position[0], self.position[1], 15, arcade.color.BLACK)
        arcade.draw_line(self.position[0], self.position[1], self.position[0] + 50 * math.cos(self.rotation_angle),
                         self.position[1] + 50 * math.sin(self.rotation_angle), arcade.color.BLUE)
