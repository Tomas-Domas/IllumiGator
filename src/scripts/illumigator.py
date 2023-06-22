import arcade
import pyglet.media

from menus import draw_title_menu, InGameMenu
from util.util import *
import worldobjects
import numpy


class Character:
    def __init__(self, sprite_path, scale_factor=2, image_width=24, image_height=24,
                 center_x=WINDOW_WIDTH // 2, center_y=WINDOW_HEIGHT // 2, velocity=10):
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
            if level.check_collisions(self):
                self.character_sprite.center_x += self.velocity
        elif self.right and not self.left:
            self.character_sprite.center_x += self.velocity
            if level.check_collisions(self):
                self.character_sprite.center_x -= self.velocity
        if self.up and not self.down:
            self.character_sprite.center_y += self.velocity
            if level.check_collisions(self):
                self.character_sprite.center_y -= self.velocity
        elif self.down and not self.up:
            self.character_sprite.center_y -= self.velocity
            if level.check_collisions(self):
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
        rotated_point1 = rotate_around_center(point1, rotation_amount, center)
        rotated_point2 = rotate_around_center(point2, rotation_amount, center)

        # update the mirror's points
        self.interactive_line.point1 = rotated_point1
        self.interactive_line.point2 = rotated_point2


class Level:
    def __init__(self, wall_coordinate_list: list[list], mirror_coordinate_list: list[list] = (),
                 name='default'):
        self.background = None
        self.name = name
        self.wall_list = []
        self.mirror_list = []
        self.level_border = [
            #                 center position                      width & height        rotation
            worldobjects.Wall(numpy.array([8, WINDOW_HEIGHT/2]),              numpy.array([80, 1]), numpy.pi / 2),
            worldobjects.Wall(numpy.array([WINDOW_WIDTH-8, WINDOW_HEIGHT/2]), numpy.array([80, 1]), numpy.pi / 2),
            worldobjects.Wall(numpy.array([WINDOW_WIDTH/2, WINDOW_HEIGHT-8]), numpy.array([80, 1]), 0),
            worldobjects.Wall(numpy.array([WINDOW_WIDTH/2, 8]),               numpy.array([80, 1]), 0),
        ]
        for wall_coordinate in wall_coordinate_list:
            self.wall_list.append(worldobjects.Wall(numpy.array([wall_coordinate[0], wall_coordinate[1]]),
                                                    numpy.array([wall_coordinate[2], wall_coordinate[3]]),
                                                    wall_coordinate[4]))

        for wall in self.level_border:
            self.wall_list.append(wall)

        for mirror_coordinate in mirror_coordinate_list:
            self.mirror_list.append(
                worldobjects.Mirror(numpy.array([mirror_coordinate[0], mirror_coordinate[1]]), mirror_coordinate[4]))

    def draw(self):
        for mirror in self.mirror_list:
            mirror.draw()
        for wall in self.wall_list:
            wall.draw()

    def check_collisions(self, character: Character):
        for wall in self.wall_list:
            if character.character_sprite.collides_with_list(wall.sprite_list):
                return True
        for mirror in self.mirror_list:
            if character.character_sprite.collides_with_list(mirror.sprite_list):
                return True


class GameObject(arcade.Window):
    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
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

        # TODO: eventually JSON file
        mirror_coordinate_list = [[WINDOW_WIDTH / 4, (WINDOW_HEIGHT / 3) * 2, 1, 1, numpy.pi / 2],
                                  [(WINDOW_WIDTH / 2) + 50, WINDOW_HEIGHT - 100, 1, 1, numpy.pi],
                                  [WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4, 1, 1, numpy.pi / 2],
                                  [((WINDOW_WIDTH / 4) * 3) + 20, WINDOW_HEIGHT / 5 , 1, 1, numpy.pi]]
        wall_coordinate_list = [[800, 150, 20, 1, numpy.pi / 2]]

        self.current_level = Level(wall_coordinate_list, mirror_coordinate_list)

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
