import math
import arcade
import numpy
import random
import light
import util.util as util
import geometry


class WorldObject:
    sprite: arcade.Sprite  # TODO: load sprites and display them
    geometry_segments: list[geometry.Geometry]

    position: numpy.array
    rotation_angle: float
    color: tuple[int, int, int]
    is_interactable: bool  # TODO: use for player pushing calculations

    def __init__(self, position, rotation_angle, color=random.choice(util.COLORS), is_interactable=False):
        self.position = position
        self.rotation_angle = rotation_angle
        self.color = color
        self.is_interactable = is_interactable

    def draw(self):
        for segment in self.geometry_segments:
            segment.draw()


class Wall(WorldObject):
    def __init__(self, sprite_path, scale_factor, image_width, image_height, center_position: numpy.array,
                 side_lengths: numpy.array, rotation_angle: float = 0, color=random.choice(util.COLORS), is_interactable=True):
        super().__init__(center_position, rotation_angle, color)
        self.is_interactable = is_interactable # TODO: check this
        self.side_lengths = side_lengths
        self.wall_sprite = arcade.Sprite(sprite_path, scale_factor, image_width=image_width,
                                         image_height=image_height, hit_box_algorithm="Simple")

        axis1 = side_lengths[0] * 0.5 * numpy.array([
            math.cos(rotation_angle), math.sin(rotation_angle)
        ])
        axis2 = side_lengths[1] * 0.5 * numpy.array([
            -math.sin(rotation_angle), math.cos(rotation_angle)
        ])
        self.geometry_segments = [
            geometry.Line(center_position - axis1 - axis2, center_position - axis1 + axis2),
            geometry.Line(center_position - axis1 + axis2, center_position + axis1 + axis2),
            geometry.Line(center_position + axis1 + axis2, center_position + axis1 - axis2),
            geometry.Line(center_position + axis1 - axis2, center_position - axis1 - axis2),
        ]

    def draw(self):
        self.wall_sprite.draw()


class Mirror(Wall):
    def __init__(self, sprite_path, scale_factor, image_width, image_height, center_position: numpy.array,
                 side_lengths: numpy.array, rotation_angle: float = 0, color=random.choice(util.COLORS)):
        super().__init__(center_position, side_lengths, rotation_angle=rotation_angle, color=color)

        self.geometry_segments[2].is_reflective = True
        self.mirror_sprite = arcade.Sprite(sprite_path, scale_factor, image_width=image_width,
                                           image_height=image_height, hit_box_algorithm="Simple")

    def draw(self):
        self.mirror_sprite.draw()


class RadialLightSource:
    def __init__(self, position, rotation, angular_spread):
        self.position = position
        self.angle = rotation
        self.light_rays = []
        self.angular_spread = angular_spread

        for n in range(light.NUM_LIGHT_RAYS):
            ray_angle = (n/light.NUM_LIGHT_RAYS) * (rotation - angular_spread / 2) + (1 - n / light.NUM_LIGHT_RAYS) * (rotation + angular_spread / 2)
            ray_direction = numpy.array([math.cos(ray_angle), math.sin(ray_angle)])
            ray_angle = (n / light.NUM_LIGHT_RAYS) * (rotation - angular_spread / 2) + (
                    1 - n / light.NUM_LIGHT_RAYS) * (rotation + angular_spread / 2)
            ray_direction = numpy.array([numpy.cos(ray_angle), numpy.sin(ray_angle)])
            self.light_rays.append(light.LightRay(self.position, ray_direction))

    def cast_rays(self, world_objects):
        for ray in self.light_rays:
            ray.cast_ray(world_objects)

    def move_to(self, new_position):
        self.position[0] = new_position[0]
        self.position[1] = new_position[1]
        for ray in self.light_rays:
            ray.origin[0] = new_position[0]
            ray.origin[1] = new_position[1]

    def draw(self):
        for ray in self.light_rays:
            ray.draw()
        arcade.draw_circle_filled(self.position[0], self.position[1], 10, arcade.color.BLACK)
