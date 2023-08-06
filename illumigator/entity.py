import itertools
import time

import arcade
import numpy
import pyglet.media

from illumigator import util, worldobjects


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
        self._idle_frames_shown = 0
        self.idle = False

        for i in range(6):
            fname = sprite_format_string.format(i=i, direction=direction)
            self._sprite_files.append(fname)
            sprite = util.load_texture(fname)
            self._sprites.append(sprite)

        for i in range(1, 4):
            fname = dead_sprite_format_string.format(i=i, direction=direction)
            self._dead_sprites.append(util.load_texture(fname))

        for i in range(0, 4):
            fname = idle_sprite_format.format(i=i, direction=direction)
            self._idle_sprites.append(util.load_texture(fname))

        fname = idle_sprite_format.format(i=1, direction=direction)
        self._idle_sprites.append(util.load_texture(fname))

        self.stationary = self._sprites[0]

    def __next__(self):
        if self.dead:
            # Show last death sprite for 20 frames
            if self._dead_index > len(self._dead_sprites) - 2:
                if self._dead_frames_shown > 20:
                    # If death animation over return None
                    return None
                self._dead_frames_shown += 1
            else:
                self._dead_index = (self._dead_index + 1) % len(self._dead_sprites)
            return self._dead_sprites[self._dead_index]
        elif self.idle:
            if self._idle_index in [0] and self._idle_frames_shown < 15:
                self._idle_frames_shown += 1
                return self._idle_sprites[self._idle_index] 
            elif self._idle_index in [1] and self._idle_frames_shown < 2:
                self._idle_frames_shown += 1
                return self._idle_sprites[self._idle_index] 
            elif self._idle_index in [2] and self._idle_frames_shown < 15:
                self._idle_frames_shown += 1
                return self._idle_sprites[self._idle_index]
            elif self._idle_index in [3] and self._idle_frames_shown < 2:
                self._idle_frames_shown += 1
                return self._idle_sprites[self._idle_index]
            self._idle_frames_shown = 0
            self._idle_index = (self._idle_index + 1) % len(self._idle_sprites)
            return self._idle_sprites[self._idle_index]
        else:
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
        self._sleep_sprites_files = []
        self._index = -1
        fnames = [sprite_format_string.format(i=i, direction=direction) for i in range(1, 5)]
        for fname in fnames:
            self._sprite_files.append(fname)
            sprite = util.load_texture(fname)
            self._sprites.append(sprite)
        self.stationary = []
        for i in range(2):
            fname = util.ENEMY_SLEEP_SPRITE.format(i=i)
            self._sleep_sprites_files.append(fname)
            self.stationary.append(util.load_texture(fname))

    def iter_sleep_sprite(self):
        for texture in itertools.cycle(self.stationary):
            for _ in range(6):
                yield texture


class Gator:
    def __init__(
            self,
            position,
            walking_volume
    ):

        self.status = "alive"

        self.left_character_loader = PlayerSpriteLoader("left")
        self.right_character_loader = PlayerSpriteLoader("right")
        self.sprite = util.load_sprite(
            filename=self.right_character_loader._sprite_files[0],
            scale=util.GATOR_SPRITE_INFO[1],
            center_x=position[0],
            center_y=position[1],
            image_width=util.GATOR_SPRITE_INFO[2],
            image_height=util.GATOR_SPRITE_INFO[3],
            hit_box_algorithm="Simple",
        )

        self.world_object = worldobjects.WorldObject(
            numpy.array([position[0], position[1]]),
            0
        )
        self.world_object.initialize_geometry(
            (util.GATOR_SPRITE_INFO[0],
             util.GATOR_SPRITE_INFO[1],
             util.GATOR_SPRITE_INFO[2] - 10,
             util.GATOR_SPRITE_INFO[3] - 4)
        )

        # To check if gator is idle
        self.last_movement_timestamp = time.time()

        self.left = False
        self.right = False
        self.up = False
        self.down = False

        self.mirror_in_reach = None
        self.rotation_dir = 0
        self.rotation_factor = 0
        self.player = pyglet.media.player.Player()


        self.walking_sound = util.load_sound("new_walk.wav")
        self.walking_volume = walking_volume

    def draw(self):
        if self.mirror_in_reach is not None:
            self.mirror_in_reach.draw_outline()
            self.mirror_in_reach.draw()
        self.sprite.draw(pixelated=True)
        self.world_object.draw()

    def update(self, level, walking_volume, enemy):
        # Play death animation if dead
        if self.status == "dead":
            if "_right" in self.sprite.texture.name:  # Facing right
                next_sprite = next(self.right_character_loader)
            else:
                next_sprite = next(self.left_character_loader)

            if next_sprite is not None:
                self.sprite.texture = next_sprite
                return
            else:
                return False  # Return False when animation is finished playing

        self.walking_volume = walking_volume
        self.walk(level, enemy)

        mirror, dist_squared = worldobjects.find_nearest_world_object(self.world_object.position, level.mirror_list)
        self.mirror_in_reach = mirror if dist_squared < util.PLAYER_REACH_DISTANCE_SQUARED else None

        # Rotation
        if self.rotation_dir == 0 or self.mirror_in_reach is None:
            self.rotation_factor = 0
            return

        self.rotation_factor = self.rotation_factor+0.1 if self.rotation_factor < 2.0 else 2.0
        if not self.mirror_in_reach.move_if_safe(
            self,
            enemy,
            numpy.zeros(2),
            self.rotation_dir * util.OBJECT_ROTATION_AMOUNT * (2 ** self.rotation_factor - 0.9),
        ):
            self.rotation_factor = 0


    def walk(self, level, enemy):
        # Determine movement direction
        direction = numpy.zeros(2)
        if self.right and not self.left:
            direction[0] = 1
        elif self.left and not self.right:
            direction[0] = -1
        if self.up and not self.down:
            direction[1] = 1
        elif self.down and not self.up:
            direction[1] = -1

        # If player isn't moving
        if numpy.array_equal(direction, numpy.zeros(2)):
            # Check if sound should be stopped
            if arcade.Sound.is_playing(self.walking_sound, self.player):
                arcade.stop_sound(self.player)

            # Check timer for idling
            if time.time() - self.last_movement_timestamp > util.PLAYER_IDLE_TIME:
                self.right_character_loader.idle = True
                self.left_character_loader.idle = True

            # Update Animation
            if "_right" in self.sprite.texture.name:  # Current animation is right-facing:
                self.right_character_loader.reset()
                self.sprite.texture = next(self.right_character_loader)
            else:
                self.left_character_loader.reset()
                self.sprite.texture = next(self.left_character_loader)

        # If player is moving
        else:
            # Check if sound should be played
            if not arcade.Sound.is_playing(self.walking_sound, self.player) and self.walking_volume > 0:
                self.player = arcade.play_sound(self.walking_sound, float(self.walking_volume))

            # Reset timer for idling
            self.unidle()

            # Update Animation
            if direction[0] == 1:  # Moving right
                next_sprite = next(self.right_character_loader)
            elif direction[0] == -1:  # Moving left
                next_sprite = next(self.left_character_loader)
            elif "_right" in self.sprite.texture.name:  # Current animation is right-facing
                next_sprite = next(self.right_character_loader)
            else:
                next_sprite = next(self.left_character_loader)
            if next_sprite is None:
                return False
            self.sprite.texture = next_sprite

            # Move (while checking for collisions)
            direction = util.PLAYER_MOVEMENT_SPEED * direction / numpy.linalg.norm(direction)
            self.sprite.center_x += direction[0]
            if level.check_collisions(self) or (enemy is not None and self.sprite.collides_with_sprite(enemy.sprite)):
                self.sprite.center_x -= direction[0]
            else:
                self.world_object.move_geometry(numpy.array([direction[0], 0]), 0)
            self.sprite.center_y += direction[1]

            if level.check_collisions(self) or (enemy is not None and self.sprite.collides_with_sprite(enemy.sprite)):
                self.sprite.center_y -= direction[1]
            else:
                self.world_object.move_geometry(numpy.array([0, direction[1]]), 0)

    def unidle(self):
        self.last_movement_timestamp = time.time()
        self.left_character_loader.idle = False
        self.right_character_loader.idle = False


class Enemy:
    def __init__(
            self,
            position,
    ):
        self.status = "asleep"

        self.left_character_loader = EnemySpriteLoader("left")
        self.right_character_loader = EnemySpriteLoader("right")
        self.sleep_texture_iter = self.left_character_loader.iter_sleep_sprite()
        self.sprite = util.load_sprite(
            filename=self.left_character_loader._sleep_sprites_files[0],
            scale=util.ENEMY_SPRITE_INFO[1],
            center_x=position[0],
            center_y=position[1],
            image_width=util.ENEMY_SPRITE_INFO[2],
            image_height=util.ENEMY_SPRITE_INFO[3],
            hit_box_algorithm="Simple",
        )

        self.world_object = worldobjects.WorldObject(
            numpy.array([position[0]-2*util.ENEMY_SPRITE_INFO[1], position[1]-6*util.ENEMY_SPRITE_INFO[1]]),
            0
        )
        self.world_object.initialize_geometry(
            (util.ENEMY_SPRITE_INFO[0],
             util.ENEMY_SPRITE_INFO[1],
             14,
             8),
            is_enemy=True
        )

    def update(self, level, player):
        if self.status == "asleep":
            self.sprite.texture = next(self.sleep_texture_iter)

        elif self.status == "aggro":
            # Determine movement direction
            direction_to_player = player.world_object.position - self.world_object.position

            direction_from_obstacle = self.world_object.position - worldobjects.find_nearest_world_object(
                self.world_object.position,
                level.wall_list + level.mirror_list + level.lens_list + level.light_receiver_list + level.light_source_list
            )[0].position

            direction = (0.7/numpy.linalg.norm(direction_to_player)) * direction_to_player + (0.3/numpy.linalg.norm(direction_from_obstacle)) * direction_from_obstacle
            direction = util.ENEMY_MOVEMENT_SPEED * direction / numpy.linalg.norm(direction)

            # Update Sprite
            if direction[0] > 0:
                next_sprite = next(self.right_character_loader)
            else:
                next_sprite = next(self.left_character_loader)
            if next_sprite is None:
                return False
            self.sprite.texture = next_sprite

            # Update X and Y positions (while checking for collisions)
            self.sprite.center_x += direction[0]
            if level.check_collisions(self):
                self.sprite.center_x -= direction[0]
            else:
                self.world_object.move_geometry(numpy.array([direction[0], 0]), 0)

            self.sprite.center_y += direction[1]
            if level.check_collisions(self):
                self.sprite.center_y -= direction[1]
            else:
                self.world_object.move_geometry(numpy.array([0, direction[1]]), 0)

            if self.sprite.collides_with_sprite(player.sprite):
                player.status = "dead"

    def update_geometry_shape(self):
        wo = self.world_object
        sprite_path, sprite_scale, sprite_width, sprite_height = util.ENEMY_SPRITE_INFO
        wo.position += numpy.array([2 * sprite_scale, 6 * sprite_scale])
        axis1 = numpy.array([0.5 * (sprite_width-2) * sprite_scale, 0])
        axis2 = numpy.array([0, 0.5 * (sprite_height-6) * sprite_scale])
        wo.geometry_segments[0]._point1 = wo.position - axis1 - axis2
        wo.geometry_segments[0]._point2 = wo.position + axis1 + axis2
        wo.geometry_segments[1]._point1 = wo.position - axis1 + axis2
        wo.geometry_segments[1]._point2 = wo.position + axis1 - axis2


    def draw(self):
        self.sprite.draw(pixelated=True)
        self.world_object.draw()
