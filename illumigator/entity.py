import arcade
import pyglet.media
import numpy

from illumigator.util import PLAYER_MOVEMENT_SPEED, ENEMY_MOVEMENT_SPEED, PLAYER_SPRITE_INFO
from illumigator import util


class SpriteLoader:
    """
    Sprites manager and Iterator for a specific direction
    """

    def __init__(self, direction, sprite_format_string: str = util.PLAYER_SPRITE):
        self.suffix = direction
        self._sprites = []
        self._sprite_files = []
        self._index = -1
        for i in range(6):
            fname = sprite_format_string.format(i=i, direction=direction)
            self._sprite_files.append(fname)
            sprite = util.load_texture(fname)
            self._sprites.append(sprite)
        self.stationary = self._sprites[0]

    def reset(self):
        self._index = -1

    def get_stationary(self):
        self.reset()
        return next(self)

    def __iter__(self):
        return self

    def __next__(self):
        self._index = (self._index + 1) % len(self._sprites)
        return self._sprites[self._index]

    @property
    def sprite_files(self):
        return self._sprite_files


class Character:
    def __init__(
            self,
            scale_factor=2,
            image_width=24,
            image_height=24,
            walking_volume=1
    ):

        self.world_object = None
        self.status = None
        self.left_character_loader = SpriteLoader("left")
        self.right_character_loader = SpriteLoader("right")

        self.character_sprite = util.load_sprite(
            self.right_character_loader._sprite_files[0],
            scale_factor,
            image_width=image_width,
            image_height=image_height,
            hit_box_algorithm="Simple",
        )

        self.left = False
        self.right = False
        self.up = False
        self.down = False

        self.interactive_line = None
        self.rotation_dir = 0
        self.player = pyglet.media.player.Player()

        self.walking_sound = util.load_sound("new_walk.wav")
        self.rotation_factor = 0

        self.walking_volume = walking_volume

    def draw(self):
        self.character_sprite.draw(pixelated=True)

    def update(self, level, walking_volume):
        self.walking_volume = walking_volume
        self.walk(level)
        if self.rotation_dir == 0:
            self.rotation_factor = 0
            return

        self.rotate_surroundings(level)
        if self.rotation_factor < 3.00:
            self.rotation_factor += 1 / 15

    def reset_pos(self, c_x, c_y):
        self.character_sprite.center_x = c_x
        self.character_sprite.center_y = c_y
        # Makes sure character is facing right upon reset.
        self.right_character_loader.reset()
        self.status = None
        self.character_sprite.texture = next(self.right_character_loader)

    def move_and_check(self, direction, level):
        self.character_sprite.center_x += direction[0]
        self.world_object.move_geometry(numpy.array([direction[0], 0]), 0)
        if level.check_collisions(self):
            self.character_sprite.center_x -= direction[0]
            self.world_object.move_geometry(numpy.array([-direction[0], 0]), 0)

        self.character_sprite.center_y += direction[1]
        self.world_object.move_geometry(numpy.array([0, direction[1]]), 0)
        if level.check_collisions(self):
            self.character_sprite.center_y -= direction[1]
            self.world_object.move_geometry(numpy.array([0, -direction[1]]), 0)

    def walk(self, level):
        direction = numpy.zeros(2)
        if self.right:
            self.character_sprite.texture = next(self.right_character_loader)
            direction[0] += 1
        if self.left:
            self.character_sprite.texture = next(self.left_character_loader)
            direction[0] -= 1

        dir_is_right = "_right.png" in self.character_sprite.texture.name
        if self.up or self.down:
            if dir_is_right:
                self.character_sprite.texture = next(self.right_character_loader)
            else:
                self.character_sprite.texture = next(self.left_character_loader)
        if self.up:
            direction[1] += 1
        if self.down:
            direction[1] -= 1

        if not self.up and not self.down and not self.left and not self.right:
            if dir_is_right:
                self.right_character_loader.reset()
                self.character_sprite.texture = next(self.right_character_loader)
            else:
                self.left_character_loader.reset()
                self.character_sprite.texture = next(self.left_character_loader)

        direction_mag = numpy.linalg.norm(direction)
        if direction_mag > 0:
            direction = (
                    direction * PLAYER_MOVEMENT_SPEED / direction_mag
            )
            self.move_and_check(direction, level)

            # Check if sound should be played
            if not arcade.Sound.is_playing(self.walking_sound, self.player):
                self.player = arcade.play_sound(self.walking_sound, self.walking_volume)

        else:
            # Check if sound should be stopped
            if arcade.Sound.is_playing(self.walking_sound, self.player):
                arcade.stop_sound(self.player)

    def kill(self):
        print("YOU DIED")
        self.status = "dead"

    def rotate_surroundings(self, level):
        closest_distance_squared = (
            util.STARTING_DISTANCE_VALUE
        )  # arbitrarily large number
        closest_mirror = None
        for mirror in level.mirror_list:
            distance = mirror.distance_squared_to_center(
                self.character_sprite.center_x, self.character_sprite.center_y
            )
            if distance < closest_distance_squared:
                closest_mirror = mirror
                closest_distance_squared = distance

        if (
                closest_mirror is not None
                and closest_distance_squared <= util.PLAYER_REACH_DISTANCE_SQUARED
        ):
            closest_mirror.move_if_safe(
                self,
                numpy.zeros(2),
                self.rotation_dir
                * util.OBJECT_ROTATION_AMOUNT
                * (2 ** self.rotation_factor),
            )


class Enemy(Character):
    def __init__(
            self,
            scale_factor=2.5,
            image_width=24,
            image_height=24,
    ):
        super().__init__(scale_factor, image_width, image_height)
        self.state = "asleep"

        # Change util.ENEMY_SPRITE to use enemy sprite
        self.left_character_loader = SpriteLoader("left", util.ENEMY_SPRITE)
        self.right_character_loader = SpriteLoader("right", util.ENEMY_SPRITE)

        self.character_sprite = util.load_sprite(
            self.right_character_loader.sprite_files[0],
            scale_factor,
            image_width=image_width,
            image_height=image_height,
            hit_box_algorithm="Simple",
        )

    def find_nearest_obstacle(self, level):
        nearest_distance_squared = float('inf')
        nearest_obstacle = None
        for obstacle in level.wall_list + level.mirror_list + level.light_receiver_list:
            distance_squared = (obstacle._position[0] - self.character_sprite.center_x) ** 2 + (
                        obstacle._position[1] - self.character_sprite.center_y) ** 2
            if distance_squared < nearest_distance_squared:
                nearest_distance_squared = distance_squared
                nearest_obstacle = obstacle
        return nearest_obstacle

    def update(self, level, player):
        self.walk(level)
        if self.state == "aggro":
            direction_to_player = numpy.array([
                player.character_sprite.center_x - self.character_sprite.center_x,
                player.character_sprite.center_y - self.character_sprite.center_y,
            ])
            direction_to_player = direction_to_player.astype(float)
            direction_to_player /= numpy.linalg.norm(direction_to_player)

            nearest_obstacle = self.find_nearest_obstacle(level)

            direction_from_obstacle = numpy.array([
                self.character_sprite.center_x - nearest_obstacle._position[0],
                self.character_sprite.center_y - nearest_obstacle._position[1],
            ])
            direction_from_obstacle /= numpy.linalg.norm(direction_from_obstacle)

            direction = 0.7 * direction_to_player + 0.3 * direction_from_obstacle
            direction /= numpy.linalg.norm(direction)

            direction *= ENEMY_MOVEMENT_SPEED
            self.move_and_check(direction, level)

            if arcade.check_for_collision(
                    self.character_sprite, player.character_sprite
            ):
                player.kill()
