import arcade
import pyglet.media
import numpy

from illumigator.util import WORLD_WIDTH, WORLD_HEIGHT, PLAYER_MOVEMENT_SPEED
from illumigator import util


class SpriteLoader:
    """
    Sprites manager and Iterator for a specific direction
    """

    def __init__(self, direction):
        self.suffix = direction
        self._sprites = []
        self._sprite_files = []
        self._index = -1
        for i in range(6):
            fname = util.PLAYER_SPRITE.format(i=i, direction=direction)
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
            center_x=WORLD_WIDTH // 2,
            center_y=WORLD_HEIGHT // 2,
    ):

        self.status = None
        self.left_character_loader = SpriteLoader("left")
        self.right_character_loader = SpriteLoader("right")

        self.character_sprite = util.load_sprite(
            self.right_character_loader._sprite_files[0],
            scale_factor,
            image_width=image_width,
            image_height=image_height,
            center_x=center_x,
            center_y=center_y,
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

    def draw(self):
        self.character_sprite.draw(pixelated=True)

    def update(self, level):
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
        self.character_sprite.texture = next(self.right_character_loader)

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
            )  # Normalize and scale with speed

            # Checking if x movement is valid
            self.character_sprite.center_x += direction[0]
            if level.check_collisions(self):
                self.character_sprite.center_x -= direction[0]

            # Checking if y movement is valid
            self.character_sprite.center_y += direction[1]
            if level.check_collisions(self):
                self.character_sprite.center_y -= direction[1]

            # Check if sound should be played
            if not arcade.Sound.is_playing(self.walking_sound, self.player):
                self.player = arcade.play_sound(self.walking_sound)

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
            scale_factor=2,
            image_width=24,
            image_height=24,
            center_x=WORLD_WIDTH - 200,
            center_y=WORLD_HEIGHT - 200,
    ):
        super().__init__(scale_factor, image_width, image_height, center_x, center_y)
        self.state = "asleep"

        self.left_character_loader = SpriteLoader("left")
        self.right_character_loader = SpriteLoader("right")

        self.character_sprite = util.load_sprite(
            self.right_character_loader.sprite_files[0],
            scale_factor,
            image_width=image_width,
            image_height=image_height,
            center_x=center_x,
            center_y=center_y,
            hit_box_algorithm="Simple",
        )

    def update(self, level, player):
        dist = numpy.sqrt((self.character_sprite.center_x - player.character_sprite.center_x) ** 2
                          + (self.character_sprite.center_y - player.character_sprite.center_y) ** 2)

        if self.state == "asleep" and dist < 300:
            self.state = "aggro"

        if self.state == "aggro":
            direction = numpy.array([player.character_sprite.center_x - self.character_sprite.center_x,
                                     player.character_sprite.center_y - self.character_sprite.center_y])

            direction_mag = numpy.linalg.norm(direction)
            if direction_mag > 0:
                direction = direction * PLAYER_MOVEMENT_SPEED / direction_mag  # Normalize and scale with speed

                prev_x = self.character_sprite.center_x
                prev_y = self.character_sprite.center_y

                self.character_sprite.center_x += direction[0]
                self.character_sprite.center_y += direction[1]

                if level.check_collisions(self):
                    self.character_sprite.center_x = prev_x
                    self.character_sprite.center_y = prev_y

                    perp_direction = numpy.array([-direction[1], direction[0]])
                    self.character_sprite.center_x += perp_direction[0]
                    self.character_sprite.center_y += perp_direction[1]

                    if level.check_collisions(self):
                        self.character_sprite.center_x -= 2 * perp_direction[0]
                        self.character_sprite.center_y -= 2 * perp_direction[1]

                if arcade.check_for_collision(self.character_sprite, player.character_sprite):
                    player.kill()

