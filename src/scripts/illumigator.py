import arcade
import pyglet.media

from menus import draw_title_menu, InGameMenu
from util import util
import worldobjects
import numpy


class Character:
    def __init__(self, sprite_path, scale_factor=2, image_width=24, image_height=24,
                 center_x=util.WINDOW_WIDTH // 2, center_y=util.WINDOW_HEIGHT // 2, velocity=10):
        self.character_sprite = arcade.Sprite(sprite_path, scale_factor, image_width=image_width,
                                              image_height=image_height, center_x=center_x, center_y=center_y,
                                              hit_box_algorithm="Simple")
        self.velocity = velocity
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.interactive_line = None
        self.is_walking = False
        self.player = pyglet.media.Player()

        self.walking_sound = arcade.load_sound("../../assets/new_walk.wav")

    def draw(self):
        self.character_sprite.draw()

    def update(self, level):
        if self.left and not self.right:
            self.character_sprite.center_x -= self.velocity
            if level.check_wall_collisions(self):
                self.character_sprite.center_x += self.velocity
        elif self.right and not self.left:
            self.character_sprite.center_x += self.velocity
            if level.check_wall_collisions(self):
                self.character_sprite.center_x -= self.velocity
        if self.up and not self.down:
            self.character_sprite.center_y += self.velocity
            if level.check_wall_collisions(self):
                self.character_sprite.center_y -= self.velocity
        elif self.down and not self.up:
            self.character_sprite.center_y -= self.velocity
            if level.check_wall_collisions(self):
                self.character_sprite.center_y += self.velocity

        if self.is_walking and not arcade.Sound.is_playing(self.walking_sound, self.player):
            self.player = arcade.play_sound(self.walking_sound)
        elif not self.is_walking and arcade.Sound.is_playing(self.walking_sound, self.player):
            arcade.stop_sound(self.player)

    def rotate_world_object(self, direction):
        if self.interactive_line is None:
            return

        rotation_amount = numpy.deg2rad(1) * direction
        point1, point2 = self.interactive_line.point1, self.interactive_line.point2
        center = (point1 + point2) / 2

        # rotate the points around the center of the mirror
        rotated_point1 = util.rotate_around_center(point1, rotation_amount, center)
        rotated_point2 = util.rotate_around_center(point2, rotation_amount, center)

        # update the mirror's points
        self.interactive_line.point1 = rotated_point1
        self.interactive_line.point2 = rotated_point2


class Level:
    def __init__(self, wall_list: list[list[int]], mirror_list: list[list[int]] = (), name='default'):
        self.background = None
        self.physics_engine = None
        self.name = name
        self.wall_list = []
        self.mirror_list = []

        for wall in wall_list:
            wall_sprite = arcade.Sprite('../../assets/wall.png')
            wall_sprite.center_x = wall[0]
            wall_sprite.center_y = wall[1]
            self.wall_list.append(wall_sprite)

        for mirror in mirror_list:
            mirror_sprite = arcade.Sprite('../../assets/mirror.png')
            mirror_sprite.center_x = mirror[0]
            mirror_sprite.center_y = mirror[1]
            self.mirror_list.append(mirror_sprite)

    def draw(self):
        for mirror in self.mirror_list:
            mirror.draw()
        for wall in self.wall_list:
            wall.draw()

    def check_wall_collisions(self, character: Character):
        for wall in self.wall_list:
            if character.character_sprite.collides_with_sprite(wall):
                return True


class GameObject(arcade.Window):
    def __init__(self):
        super().__init__(util.WINDOW_WIDTH, util.WINDOW_HEIGHT, util.WINDOW_TITLE)
        self.elem_list = None
        self.mirror = None
        self.wall = None
        self.game_state = None
        self.set_mouse_visible(False)
        arcade.set_background_color(arcade.color.BROWN)
        self.game_menu = None
        self.tile_map = None
        self.character = None
        self.game_state = None
        self.current_level = None

    def setup(self):
        self.game_state = 'menu'
        self.game_menu = InGameMenu()
        self.character = Character('../../assets/character1.png')
        self.elem_list = arcade.SpriteList()
        self.wall = arcade.Sprite('../../assets/wall.png')
        self.mirror = arcade.Sprite('../../assets/mirror.png')

        mirror_list = [[100, 200]]
        wall_list = [[400, 500],
                     [470, 500],
                     [400, 570],
                     [470, 570]]  # temporary, eventually load in for maps from JSON

        self.current_level = Level(wall_list, mirror_list)

    def update(self, delta_time):
        self.character.update(self.current_level)

    def on_draw(self):
        self.clear()

        if self.game_state == 'menu':
            draw_title_menu()
        elif self.game_state == 'game' or self.game_state == 'paused':
            self.current_level.draw()
            self.character.draw()

            if self.game_state == 'paused':
                self.game_menu.draw()

    def on_key_press(self, key, key_modifiers):
        if self.game_state == 'menu':
            if key == arcade.key.ENTER:
                self.game_state = 'game'
            if key == arcade.key.ESCAPE:
                arcade.close_window()

        elif self.game_state == 'game':
            if key == arcade.key.ESCAPE:
                self.game_state = 'paused'
            if key == arcade.key.W or key == arcade.key.UP:
                self.character.up = True
                self.character.is_walking = True
            if key == arcade.key.A or key == arcade.key.LEFT:
                self.character.left = True
                self.character.is_walking = True
            if key == arcade.key.D or key == arcade.key.RIGHT:
                self.character.right = True
                self.character.is_walking = True
            if key == arcade.key.S or key == arcade.key.DOWN:
                self.character.down = True
                self.character.is_walking = True

        elif self.game_state == 'paused':
            if key == arcade.key.ESCAPE:
                self.game_state = 'game'
            if key == arcade.key.DOWN:
                self.game_menu.increment_selection()
            if key == arcade.key.UP:
                self.game_menu.decrement_selection()
            if key == arcade.key.ENTER:
                if self.game_menu.selection == 0:
                    self.game_state = 'game'
                elif self.game_menu.selection == 1:
                    self.game_state = 'menu'

    def on_key_release(self, key, key_modifiers):
        if key == arcade.key.W or key == arcade.key.UP:
            self.character.up = False
            self.character.is_walking = False
        if key == arcade.key.A or key == arcade.key.LEFT:
            self.character.left = False
            self.character.is_walking = False
        if key == arcade.key.D or key == arcade.key.RIGHT:
            self.character.right = False
            self.character.is_walking = False
        if key == arcade.key.S or key == arcade.key.DOWN:
            self.character.down = False
            self.character.is_walking = False
        self.character.update(self.current_level)


def main():
    window = GameObject()
    window.setup()
    arcade.run()


if __name__ == '__main__':
    main()
