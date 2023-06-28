import arcade
import pyglet.media
import numpy

from illumigator.menus import draw_title_menu, InGameMenu, WinScreen
from illumigator.util import WINDOW_WIDTH, WINDOW_HEIGHT
from illumigator import util
from illumigator import worldobjects

class Character:
    def __init__(self,
                 scale_factor=2,
                 image_width=24,
                 image_height=24,
                 center_x=WINDOW_WIDTH // 2,
                 center_y=WINDOW_HEIGHT // 2):

        self.textures = [
            util.load_texture(util.PLAYER_SPRITE_RIGHT),
            util.load_texture(util.PLAYER_SPRITE_LEFT)
        ]

        self.character_sprite = util.load_sprite(util.PLAYER_SPRITE_RIGHT, scale_factor, image_width=image_width,
                                                 image_height=image_height, center_x=center_x, center_y=center_y,
                                                 hit_box_algorithm="Simple")
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
            self.rotation_factor += 1/15

    def walk(self, level):
        direction = numpy.zeros(2)
        if self.right:
            self.character_sprite.texture = self.textures[0]
            direction[0] += 1
        if self.left:
            self.character_sprite.texture = self.textures[1]
            direction[0] -= 1
        if self.up:
            direction[1] += 1
        if self.down:
            direction[1] -= 1

        direction_mag = numpy.linalg.norm(direction)
        if direction_mag > 0:
            direction = direction * util.PLAYER_MOVEMENT_SPEED / direction_mag  # Normalize and scale with speed

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

    def rotate_surroundings(self, level):
        closest_distance_squared = util.STARTING_DISTANCE_VALUE  # arbitrarily large number
        closest_mirror = None
        for mirror in level.mirror_list:
            distance = mirror.distance_squared_to_center(self.character_sprite.center_x, self.character_sprite.center_y)
            if distance < closest_distance_squared:
                closest_mirror = mirror
                closest_distance_squared = distance

        if closest_mirror is not None and closest_distance_squared <= util.PLAYER_REACH_DISTANCE_SQUARED:
            closest_mirror.move_if_safe(self, numpy.zeros(2),
                                        self.rotation_dir * util.OBJECT_ROTATION_AMOUNT * (2 ** self.rotation_factor))
