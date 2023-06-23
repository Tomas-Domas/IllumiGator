from abc import abstractmethod
import random
import arcade
import math
import numpy
import light
import util.util as util
import geometry


class WorldObject:
    _position: numpy.array
    _rotation_angle: float
    _is_interactable: bool
    _is_receiver: bool
    _geometry_segments: list[geometry.Geometry]

    _sprite_list: arcade.SpriteList
    color: tuple[int, int, int]

    def __init__(self, position, rotation_angle, color=random.choice(util.COLORS), is_interactable=False, is_receiver=False):
        self._position = position
        self._rotation_angle = rotation_angle
        self._is_interactable = is_interactable
        self._is_receiver = is_receiver
        self._geometry_segments = []

        self._sprite_list = arcade.SpriteList()
        self.color = color

    def draw(self):
        self._sprite_list.draw(pixelated=True)
        for segment in self._geometry_segments:
            segment.draw()

    def move(self, move_distance: numpy.array, rotate_angle: float = 0):
        self._position = self._position + move_distance
        self._rotation_angle = self._rotation_angle + rotate_angle
        for segment in self._geometry_segments:
            segment.move(self._position, move_distance, rotate_angle=rotate_angle)
        for sprite in self._sprite_list:
            new_position = numpy.array([sprite.center_x, sprite.center_y]) + move_distance
            new_position = util.rotate_around_center(self._position, new_position, rotate_angle)
            sprite.center_x, sprite.center_y = new_position[0], new_position[1]
            sprite.radians += rotate_angle

    def distance_squared_to_center(self, point_x, point_y):
        return util.distance_squared_ordered_pair(self._position, point_x, point_y)

    def check_collision(self, sprite: arcade.Sprite):
        return sprite.collides_with_list(self._sprite_list)


class Wall(WorldObject):
    def __init__(self, center_position: numpy.array, dimensions: numpy.array, rotation_angle, is_interactable=False):
        super().__init__(center_position, rotation_angle, is_interactable=is_interactable)

        sprite_path, scale_factor, image_width, image_height = util.WALL_SPRITE_INFO
        side_lengths = dimensions * image_width

        axis1_norm = numpy.array([math.cos(rotation_angle), math.sin(rotation_angle)])
        axis2_norm = numpy.array([-math.sin(rotation_angle), math.cos(rotation_angle)])
        axis1 = side_lengths[0] * 0.5 * axis1_norm
        axis2 = side_lengths[1] * 0.5 * axis2_norm
        self._geometry_segments = [
            geometry.Line(center_position - axis1 - axis2, center_position - axis1 + axis2),
            geometry.Line(center_position - axis1 + axis2, center_position + axis1 + axis2),
            geometry.Line(center_position + axis1 + axis2, center_position + axis1 - axis2),
            geometry.Line(center_position + axis1 - axis2, center_position - axis1 - axis2),
        ]

        for col in range(dimensions[0]):
            for row in range(dimensions[1]):
                sprite_center = center_position - axis1 - axis2 + axis1_norm * (
                        image_width / 2 + col * image_width) + axis2_norm * (image_height / 2 + row * image_height)

                self._sprite_list.append(
                    arcade.Sprite(sprite_path, scale_factor, image_width=image_width, image_height=image_height,
                                  center_x=sprite_center[0], center_y=sprite_center[1],
                                  angle=numpy.rad2deg(rotation_angle), hit_box_algorithm="Simple"
                                  )
                )


class Mirror(WorldObject):
    def __init__(self, center_position: numpy.array, rotation_angle, is_interactable=False):
        super().__init__(center_position, rotation_angle, is_interactable=is_interactable)

        sprite_path, scale_factor, image_width, image_height = util.MIRROR_SPRITE_INFO
        side_lengths = numpy.array([image_width, image_height])

        axis1_norm = numpy.array([math.cos(rotation_angle), math.sin(rotation_angle)])
        axis2_norm = numpy.array([-math.sin(rotation_angle), math.cos(rotation_angle)])
        axis1 = side_lengths[0] * 0.5 * axis1_norm
        axis2 = side_lengths[1] * 0.5 * axis2_norm
        self._geometry_segments = [
            geometry.Line(center_position - axis1 - axis2, center_position - axis1 + axis2, is_reflective=True),
            geometry.Line(center_position - axis1 + axis2, center_position + axis1 + axis2),
            geometry.Line(center_position + axis1 + axis2, center_position + axis1 - axis2, is_reflective=True),
            geometry.Line(center_position + axis1 - axis2, center_position - axis1 - axis2),
        ]

        sprite_center = center_position - axis1 - axis2 + (image_width / 2) * axis1_norm + (
                image_height / 2) * axis2_norm
        self._sprite_list.append(
            arcade.Sprite(sprite_path, scale_factor, image_width=image_width, image_height=image_height,
                          center_x=sprite_center[0], center_y=sprite_center[1],
                          angle=numpy.rad2deg(rotation_angle), hit_box_algorithm="Simple"
                          )
        )


class LightReceiver(WorldObject):
    def __init__(self, center_position: numpy.array, rotation_angle, is_interactable=False):
        super().__init__(center_position, rotation_angle, is_interactable=is_interactable, is_receiver=True)
        self.charge = 0

        sprite_path, scale_factor, image_width, image_height = util.RECEIVER_SPRITE_INFO
        side_lengths = numpy.array([image_width, image_height])

        axis1_norm = numpy.array([math.cos(rotation_angle), math.sin(rotation_angle)])
        axis2_norm = numpy.array([-math.sin(rotation_angle), math.cos(rotation_angle)])
        axis1 = side_lengths[0] * 0.5 * axis1_norm
        axis2 = side_lengths[1] * 0.5 * axis2_norm
        self._geometry_segments = [
            geometry.Line(center_position - axis1 - axis2, center_position - axis1 + axis2),
            geometry.Line(center_position - axis1 + axis2, center_position + axis1 + axis2),
            geometry.Line(center_position + axis1 + axis2, center_position + axis1 - axis2),
            geometry.Line(center_position + axis1 - axis2, center_position - axis1 - axis2),
        ]

        sprite_center = center_position - axis1 - axis2 + (image_width / 2) * axis1_norm + (
                image_height / 2) * axis2_norm
        self._sprite_list.append(
            arcade.Sprite(sprite_path, scale_factor, image_width=image_width, image_height=image_height,
                          center_x=sprite_center[0], center_y=sprite_center[1],
                          angle=numpy.rad2deg(rotation_angle), hit_box_algorithm="Simple"
                          )
        )


class LightSource(WorldObject):
    def __init__(self, position, rotation_angle):
        super().__init__(position, rotation_angle, arcade.color.GOLD)
        self._light_rays = [light.LightRay(numpy.zeros(2), numpy.zeros(2)) for _ in range(util.NUM_LIGHT_RAYS)]

    def cast_rays(self, world_objects):
        for ray in self._light_rays:
            ray.cast_ray(world_objects)

    def move(self, move_distance: numpy.array, rotate_angle: float = 0):
        super().move(move_distance, rotate_angle)
        self.calculate_light_ray_positions()

    @abstractmethod
    def calculate_light_ray_positions(self):
        pass

    @abstractmethod
    def draw(self):
        pass



class RadialLightSource(LightSource):
    def __init__(self, position, rotation_angle, angular_spread):
        super().__init__(position, rotation_angle)
        self._angular_spread = angular_spread
        self.calculate_light_ray_positions()

    def calculate_light_ray_positions(self):
        num_rays = len(self._light_rays)
        for n in range(num_rays):
            ray_angle = (n / num_rays) * (self._rotation_angle - self._angular_spread / 2) + (1 - n / num_rays) * (
                    self._rotation_angle + self._angular_spread / 2)
            ray_direction = numpy.array([math.cos(ray_angle), math.sin(ray_angle)])
            self._light_rays[n]._origin = self._position
            self._light_rays[n]._direction = ray_direction

    def draw(self):
        for ray in self._light_rays:
            ray.draw()
        arcade.draw_circle_filled(self._position[0], self._position[1], 15, arcade.color.BLACK)
        # arcade.draw_line(self.position[0], self.position[1], self.position[0] + 50 * math.cos(self.rotation_angle),
        #                  self.position[1] + 50 * math.sin(self.rotation_angle), arcade.color.BLUE)



class ParallelLightSource(LightSource):
    def __init__(self, position, rotation_angle):
        super().__init__(position, rotation_angle)
        self._width = 30
        self.calculate_light_ray_positions()

    def calculate_light_ray_positions(self):
        num_rays = len(self._light_rays)
        ray_direction = numpy.array([math.cos(self._rotation_angle), math.sin(self._rotation_angle)])
        spread_direction = numpy.array([math.cos(self._rotation_angle + numpy.pi / 2), math.sin(self._rotation_angle + numpy.pi / 2)])
        for n in range(-num_rays//2, num_rays//2):

            self._light_rays[n]._origin = self._position + ((n / num_rays) * self._width) * spread_direction
            self._light_rays[n]._direction = ray_direction

    def draw(self):
        for ray in self._light_rays:
            ray.draw()
        arcade.draw_circle_outline(self._position[0], self._position[1], 15, arcade.color.BLACK)
        # arcade.draw_line(self.position[0], self.position[1], self.position[0] + 50 * math.cos(self.rotation_angle),
        #                  self.position[1] + 50 * math.sin(self.rotation_angle), arcade.color.BLUE)
