import time
import arcade
import pyglet.media
import numpy

from illumigator import util


class SpriteLoader:
    """
    Sprites manager and Iterator for a specific direction
    """

    def __init__(self):
        pass

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


class PlayerSpriteLoader(SpriteLoader):
    """
    Sprites manager and Iterator for a specific direction
    """

    def __init__(self, direction, sprite_format_string: str = util.PLAYER_SPRITE,
                 idle_sprite_format: str = util.PLAYER_IDLE_SPRITE,
                 dead_sprite_format_string: str = util.PLAYER_DEAD_SPRITE):
        self.suffix = direction

        self._sprites = []
        self._sprite_files = []
        self._index = -1

        self._dead_sprites = []
        self._dead_index = -1
        self._dead_frames_shown = 0
        self.dead = False

        self._idle_sprites = []
        self._idle_index = -1
        self.idle = True

        for i in range(6):
            fname = sprite_format_string.format(i=i, direction=direction)
            self._sprite_files.append(fname)
            sprite = util.load_texture(fname)
            self._sprites.append(sprite)

        for i in range(1, 4):
            fname = dead_sprite_format_string.format(i=i, direction=direction)
            self._dead_sprites.append(util.load_texture(fname))

        for i in range(0, 3):
            fname = idle_sprite_format.format(i=i, direction=direction)
            self._idle_sprites.append(util.load_texture(fname))

        self.stationary = self._sprites[0]

    def __next__(self):
        if self.dead:
            # Show last death sprite for 5 frames
            if self._dead_index > len(self._dead_sprites) - 2:
                if self._dead_frames_shown > 5:
                    # If death animation over return None
                    return None
                self._dead_frames_shown += 1
            else:
                self._dead_index = (self._dead_index + 1) % len(self._dead_sprites)
            return self._dead_sprites[self._dead_index]
        elif self.idle:
            if self._idle_index > len(self._idle_sprites) - 2:
                return self._idle_sprites[-1]
            else:
                self._idle_index = (self._idle_index + 1) % len(self._idle_sprites)
            return self._idle_sprites[self._idle_index]
        else:
            self._idle_index = self._dead_index = -1
            return super().__next__()


class EnemySpriteLoader(SpriteLoader):
    """
    Sprites manager and Iterator for a specific direction
    """

    def __init__(self, direction, sprite_format_string: str = util.ENEMY_SPRITE):
        super().__init__()
        self.suffix = direction
        self._sprites = []
        self._sprite_files = []
        self._index = -1
        fnames = [sprite_format_string.format(i=i, direction=direction) for i in range(1, 5)]
        for fname in fnames:
            self._sprite_files.append(fname)
            sprite = util.load_texture(fname)
            self._sprites.append(sprite)
        self.stationary = util.load_texture(util.ENEMY_SLEEP_SPRITE)


class Character:
    def __init__(
            self,
            scale_factor=2,
            image_width=20,
            image_height=18,
            walking_volume=1
    ):

        self.world_object = None
        self.status = None
        self.left_character_loader = PlayerSpriteLoader("left")
        self.right_character_loader = PlayerSpriteLoader("right")

        # To check if gator is idle
        self.last_movement_timestamp = time.time()

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

        self.mirror_in_reach = None
        self.rotation_dir = 0
        self.player = pyglet.media.player.Player()

        self.walking_sound = util.load_sound("new_walk.wav")
        self.rotation_factor = 0

        self.walking_volume = walking_volume

    def draw(self):
        if self.mirror_in_reach is not None:
            self.mirror_in_reach.draw_outline()
        self.character_sprite.draw(pixelated=True)

    def update(self, level, walking_volume, enemy):
        self.walking_volume = walking_volume

        # Idle state animation
        if any([self.up, self.down, self.left, self.right]):
            self.last_movement_timestamp = time.time()
            self.right_character_loader.idle = False
            self.left_character_loader.idle = False
        elif time.time() - self.last_movement_timestamp > util.PLAYER_IDLE_TIME:
            # IDLE after PLAYER_IDLE_TIME seconds
            self.right_character_loader.idle = True
            self.left_character_loader.idle = True

        # Walking. Return False if player died
        if self.walk(level, enemy) is False:
            return False

        # Rotation
        if self.rotation_dir == 0:
            self.rotation_factor = 0

        if self.mirror_in_reach is None:
            self.rotation_factor = 0
        elif self.rotation_factor < 3.00:
            self.rotation_factor += 1 / 15

        self.mirror_in_reach = self.get_mirror_in_reach(level)
        if self.mirror_in_reach is not None:
            self.mirror_in_reach.move_if_safe(
                self,
                numpy.zeros(2),
                self.rotation_dir
                * util.OBJECT_ROTATION_AMOUNT
                * (2 ** self.rotation_factor),
            )

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

    def update_sprite(self, direction=None):
        if self.right:
            next_sprite = next(self.right_character_loader)
            if next_sprite is None:
                return False
            self.character_sprite.texture = next_sprite
            if direction is not None:
                direction[0] += 1
        if self.left:
            next_sprite = next(self.left_character_loader)
            if next_sprite is None:
                return False
            self.character_sprite.texture = next_sprite
            if direction is not None:
                direction[0] -= 1

    def walk(self, level, enemy):
        direction = numpy.zeros(2)
        if getattr(self.right_character_loader, "dead", False):
            if "_right.png" in self.character_sprite.texture.name:
                self.right = True
                self.left = False
            else:
                self.right = True
                self.left = False

        if self.update_sprite(direction) is False:
            return False

        if getattr(self.right_character_loader, "dead", False):
            return
        dir_is_right = "_right" in self.character_sprite.texture.name
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
                    direction * util.PLAYER_MOVEMENT_SPEED / direction_mag
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

    def get_mirror_in_reach(self, level):
        closest_distance_squared = float('inf')
        closest_mirror = None
        for mirror in level.mirror_list:
            distance_squared = mirror.distance_squared_to_center(
                self.character_sprite.center_x,
                self.character_sprite.center_y
            )
            if distance_squared < closest_distance_squared:
                closest_mirror = mirror
                closest_distance_squared = distance_squared
        return closest_mirror if closest_distance_squared <= util.PLAYER_REACH_DISTANCE_SQUARED else None


class Enemy(Character):
    def __init__(
            self,
            scale_factor=2.5,
            image_width=20,
            image_height=18,
    ):
        super().__init__(scale_factor, image_width, image_height)
        self.state = "asleep"

        self.left_character_loader = EnemySpriteLoader("left")
        self.right_character_loader = EnemySpriteLoader("right")

        self.character_sprite = util.load_sprite(
            util.ENEMY_SLEEP_SPRITE,
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
        if self.update_sprite() is False:
            return False
        self.right = self.left = False

        if self.state == "asleep":
            self.character_sprite.texture = self.left_character_loader.stationary
        elif self.state == "aggro":
            x_diff = (player.character_sprite.center_x - self.character_sprite.center_x)
            if x_diff < 0:
                self.right = False
                self.left = True
            elif x_diff > 0:
                self.left = False
                self.right = True

            direction_to_player = numpy.array([
                player.character_sprite.center_x - self.character_sprite.center_x,
                player.character_sprite.center_y - self.character_sprite.center_y,
            ])
            direction_to_player = direction_to_player.astype(float)
            direction_to_player = direction_to_player / numpy.linalg.norm(direction_to_player)

            nearest_obstacle = self.find_nearest_obstacle(level)

            direction_from_obstacle = numpy.array([
                self.character_sprite.center_x - nearest_obstacle._position[0],
                self.character_sprite.center_y - nearest_obstacle._position[1],
            ])
            direction_from_obstacle = direction_from_obstacle / numpy.linalg.norm(direction_from_obstacle)

            direction = 0.7 * direction_to_player + 0.3 * direction_from_obstacle
            direction = direction / numpy.linalg.norm(direction)

            direction *= util.ENEMY_MOVEMENT_SPEED
            self.move_and_check(direction, level)

            if self.character_sprite.collides_with_sprite(player.character_sprite):
                player.kill()
