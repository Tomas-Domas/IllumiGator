from abc import abstractmethod
import arcade
import numpy
import random
import math

from illumigator import light
from illumigator import util
from illumigator import geometry
from illumigator import object_animation


class WorldObject:
    _position: numpy.ndarray
    _rotation_angle: float
    _is_interactable: bool
    _is_receiver: bool
    _geometry_segments: list[geometry.Geometry]
    obj_animation: object_animation.ObjectAnimation

    _sprite_list: arcade.SpriteList
    color: tuple[int, int, int]


    def __init__(self, position: numpy.ndarray, dimensions: numpy.ndarray, rotation_angle: float, sprite_info: tuple,
                 color=random.choice(util.COLORS), is_interactable=False, is_receiver=False):
        self._position = position
        self._rotation_angle = rotation_angle
        self._is_interactable = is_interactable
        self._is_receiver = is_receiver
        self._geometry_segments = []
        self.obj_animation = None

        self._sprite_list = arcade.SpriteList()
        self.color = color

        sprite_path, sprite_scale, sprite_width, sprite_height = sprite_info

        side_lengths = numpy.array([
            sprite_width  * sprite_scale * dimensions[0],
            sprite_height * sprite_scale * dimensions[1]
        ])
        axis1_norm = numpy.array([math.cos(rotation_angle), math.sin(rotation_angle)])
        axis2_norm = numpy.array([-math.sin(rotation_angle), math.cos(rotation_angle)])
        axis1 = 0.5 * side_lengths[0] * axis1_norm
        axis2 = 0.5 * side_lengths[1] * axis2_norm
        self._geometry_segments = [
            geometry.Line(position - axis1 - axis2, position - axis1 + axis2),
            geometry.Line(position - axis1 + axis2, position + axis1 + axis2),
            geometry.Line(position + axis1 + axis2, position + axis1 - axis2),
            geometry.Line(position + axis1 - axis2, position - axis1 - axis2),
        ]

        for col in range(int(dimensions[0])):
            for row in range(int(dimensions[1])):
                sprite_center = (position-axis1-axis2) + sprite_scale * ((sprite_width*(col+0.5)*axis1_norm) + (sprite_height*(row+0.5)*axis2_norm))

                self._sprite_list.append( arcade.Sprite(
                    sprite_path, sprite_scale, image_width=sprite_width, image_height=sprite_height,
                    center_x=sprite_center[0], center_y=sprite_center[1],
                    angle=numpy.rad2deg(rotation_angle), hit_box_algorithm="Simple"
                ))


    def draw(self):
        self._sprite_list.draw(pixelated=True)


    def move_geometry(self, move_distance: numpy.ndarray = numpy.zeros(2), rotate_angle: float = 0):
        self._position = self._position + move_distance
        self._rotation_angle = self._rotation_angle + rotate_angle
        for segment in self._geometry_segments:
            segment.move(self._position, move_distance, rotate_angle=rotate_angle)


    def distance_squared_to_center(self, point_x, point_y):
        return util.distance_squared_ordered_pair(self._position, point_x, point_y)


    def check_collision(self, sprite: arcade.Sprite):
        return sprite.collides_with_list(self._sprite_list)


    def apply_object_animation(self, character):
        # Test for sprite collisions
        position_change = self.obj_animation.get_new_position() - self._position
        if not self.move_if_safe(character, move_distance=position_change):  # If move is unsafe
            self.obj_animation.backtrack()


    def move_if_safe(self, character, move_distance: numpy.ndarray = numpy.zeros(2), rotate_angle: float = 0) -> bool:
        for sprite in self._sprite_list:
            new_position = numpy.array([sprite.center_x, sprite.center_y]) + move_distance
            new_position = util.rotate_around_center(self._position, new_position, rotate_angle)
            sprite.center_x, sprite.center_y = new_position[0], new_position[1]
            sprite.radians += rotate_angle
        if self.check_collision(character.character_sprite):
            for sprite in self._sprite_list:
                new_position = numpy.array([sprite.center_x, sprite.center_y]) - move_distance
                new_position = util.rotate_around_center(self._position, new_position, rotate_angle)
                sprite.center_x, sprite.center_y = new_position[0], new_position[1]
                sprite.radians -= rotate_angle
            return False
        self.move_geometry(move_distance, rotate_angle)
        return True


    def create_animation(self, travel: numpy.ndarray, dt: float = 0.01):
        self.obj_animation = object_animation.ObjectAnimation(self._position, self._position+travel, dt)


class Wall(WorldObject):
    def __init__(self, position: numpy.ndarray, dimensions: numpy.ndarray, rotation_angle: float):
        super().__init__(position, dimensions, rotation_angle, util.WALL_SPRITE_INFO)



class Mirror(WorldObject):
    def __init__(self, position: numpy.ndarray, rotation_angle: float):
        super().__init__(position, numpy.ones(2), rotation_angle, util.MIRROR_SPRITE_INFO, is_interactable=True)
        self._geometry_segments[0].is_reflective = True
        self._geometry_segments[2].is_reflective = True



class LightSource(WorldObject):
    def __init__(self, position: numpy.ndarray, rotation_angle: float, sprite_info: tuple):
        super().__init__(position, numpy.ones(2), rotation_angle, sprite_info)
        self._light_rays = [light.LightRay(numpy.zeros(2), numpy.zeros(2)) for _ in range(util.NUM_LIGHT_RAYS)]
        self._geometry_segments = []  # TODO: do this better, don't just overwrite to get rid of geometry


    def cast_rays(self, world_objects):
        for ray in self._light_rays:
            ray.cast_ray(world_objects)


    def move(self, move_distance: numpy.ndarray, rotate_angle: float = 0):
        super().move_geometry(move_distance, rotate_angle)
        self.calculate_light_ray_positions()


    def draw(self):
        for ray in self._light_rays:
            ray.draw()
        super().draw()


    @abstractmethod
    def calculate_light_ray_positions(self):
        pass



class RadialLightSource(LightSource):
    def __init__(self, position: numpy.ndarray, rotation_angle: float, angular_spread: float):
        super().__init__(position, rotation_angle, util.PLACEHOLDER_SPRITE_INFO)
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



class ParallelLightSource(LightSource):
    def __init__(self, position: numpy.ndarray, rotation_angle: float):
        super().__init__(position, rotation_angle, util.PLACEHOLDER_SPRITE_INFO)  # TODO: Use actual sprite
        self._width = util.PLACEHOLDER_SPRITE_INFO[1] * util.PLACEHOLDER_SPRITE_INFO[2]
        self.calculate_light_ray_positions()


    def calculate_light_ray_positions(self):
        num_rays = len(self._light_rays)
        ray_direction = numpy.array([math.cos(self._rotation_angle), math.sin(self._rotation_angle)])
        spread_direction = numpy.array([math.cos(self._rotation_angle + 0.5*numpy.pi), math.sin(self._rotation_angle + 0.5*numpy.pi)])
        for n in range(num_rays):
            self._light_rays[n]._origin = self._position - (self._width * (n/(util.NUM_LIGHT_RAYS-1) - 0.5)) * spread_direction
            self._light_rays[n]._direction = ray_direction



class LightReceiver(WorldObject):
    def __init__(self, position: numpy.ndarray, rotation_angle: float):
        super().__init__(position, numpy.ones(2), rotation_angle, util.RECEIVER_SPRITE_INFO, is_receiver=True)
        self.charge = 0


    def draw(self):
        color = min(255 * self.charge / util.RECEIVER_THRESHOLD, 255)
        for sprite in self._sprite_list:
            sprite.color = (color, color, 70)
        super().draw()

        for segment in self._geometry_segments:
            segment.draw()
