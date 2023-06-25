import arcade
import pyglet.media

from menus import draw_title_menu, InGameMenu, WinScreen
import util.util as util
from util.util import WINDOW_WIDTH, WINDOW_HEIGHT
import worldobjects
import numpy

class Character:
    def __init__(self, sprite_path, scale_factor=2, image_width=24, image_height=24,
                 center_x=WINDOW_WIDTH // 2, center_y=WINDOW_HEIGHT // 2, velocity=10):
        self.character_sprite = arcade.Sprite(sprite_path, scale_factor, image_width=image_width,
                                              image_height=image_height, center_x=center_x, center_y=center_y,
                                              hit_box_algorithm="Simple")
        self.velocity = velocity
        self.textures = []
        texture_right = arcade.load_texture('../../assets/character_right.png')
        texture_left = arcade.load_texture('../../assets/character_left.png')
        self.textures.append(texture_right)
        self.textures.append(texture_left)
        self.texture = texture_right
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.interactive_line = None
        self.is_walking = False
        self.counter_clockwise = False
        self.clockwise = False
        self.player = pyglet.media.Player()

        self.walking_sound = arcade.load_sound("../../assets/new_walk.wav")

        self.closest_interactable = None

    def draw(self):
        self.character_sprite.draw(pixelated=True)

    def update(self, level):
        if self.left and not self.right:
            self.character_sprite.center_x -= self.velocity
            self.character_sprite.texture = self.textures[1]
            if level.check_collisions(self):
                self.character_sprite.center_x += self.velocity
        elif self.right and not self.left:
            self.character_sprite.texture = self.textures[0]
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

        closest_distance = util.STARTING_DISTANCE_VALUE  # arbitrarily large number
        for mirror in level.mirror_list:
            distance = mirror.distance_squared_to_center(self.character_sprite.center_x, self.character_sprite.center_y)
            if distance < closest_distance:
                self.closest_interactable = mirror
                closest_distance = distance

        if self.closest_interactable is None or closest_distance > util.PLAYER_REACH_DISTANCE_SQUARED:
            return

        if self.counter_clockwise and self.closest_interactable and not self.clockwise:
            self.closest_interactable.move(numpy.zeros(2), util.OBJECT_ROTATION_AMOUNT)
        elif self.clockwise and self.closest_interactable and not self.counter_clockwise:
            self.closest_interactable.move(numpy.zeros(2), -util.OBJECT_ROTATION_AMOUNT)



class Level:
    def __init__(
            self,
            wall_coordinate_list: list[list],
            mirror_coordinate_list: list[list],
            light_receiver_coordinate_list: list[list],
            light_source_coordinate_list: list[list],
            name='default'
    ):
        self.background = None
        self.name = name

        self.mirror_list = []
        self.light_receiver_list = []
        self.light_sources_list = []

        wall_size = util.WALL_SPRITE_INFO[1] * util.WALL_SPRITE_INFO[2]
        self.wall_list: list[worldobjects.WorldObject] = [
            worldobjects.Wall(
                numpy.array([wall_size*0.5, WINDOW_HEIGHT*0.5 - wall_size*0.25]),
                numpy.array([1, WINDOW_HEIGHT//wall_size + 1]), 0
            ),
            worldobjects.Wall(
                numpy.array([WINDOW_WIDTH - wall_size*0.5, WINDOW_HEIGHT*0.5 - wall_size*0.25]),
                numpy.array([1, WINDOW_HEIGHT//wall_size + 1]), 0
            ),
            worldobjects.Wall(
                numpy.array([WINDOW_WIDTH*0.5, wall_size*0.5]),
                numpy.array([WINDOW_WIDTH//wall_size - 2, 1]), 0
            ),
            worldobjects.Wall(
                numpy.array([WINDOW_WIDTH*0.5, WINDOW_HEIGHT - wall_size*0.5]),
                numpy.array([WINDOW_WIDTH//wall_size - 2, 1]), 0
            ),
        ]

        for wall_coordinates in wall_coordinate_list:
            self.wall_list.append(worldobjects.Wall(
                numpy.array([wall_coordinates[0], wall_coordinates[1]]),
                numpy.array([wall_coordinates[2], wall_coordinates[3]]),
                wall_coordinates[4]
            ))

        for mirror_coordinates in mirror_coordinate_list:
            self.mirror_list.append(worldobjects.Mirror(
                numpy.array([mirror_coordinates[0], mirror_coordinates[1]]),
                mirror_coordinates[2]
            ))

        for light_receiver_coordinates in light_receiver_coordinate_list:
            self.light_receiver_list.append(worldobjects.LightReceiver(
                numpy.array([light_receiver_coordinates[0], light_receiver_coordinates[1]]),
                light_receiver_coordinates[2]
            ))

        for light_source_coordinates in light_source_coordinate_list:
            if len(light_source_coordinates) == 4:  # Has an angular spread argument
                self.light_sources_list.append(worldobjects.RadialLightSource(
                    numpy.array([light_source_coordinates[0], light_source_coordinates[1]]),
                    light_source_coordinates[2],
                    light_source_coordinates[3])
                )
            else:
                self.light_sources_list.append(worldobjects.ParallelLightSource(
                    numpy.array([light_source_coordinates[0], light_source_coordinates[1]]),
                    light_source_coordinates[2]))

    def draw(self):
        for wall in self.wall_list:
            wall.draw()
        for mirror in self.mirror_list:
            mirror.draw()
        for light_receiver in self.light_receiver_list:
            light_receiver.draw()
            light_receiver.charge *= util.CHARGE_DECAY
        for light_source in self.light_sources_list:
            light_source.cast_rays(self.wall_list + self.mirror_list + self.light_receiver_list + self.light_sources_list)
            light_source.draw()

    def check_collisions(self, character: Character):
        for wall in self.wall_list:
            if wall.check_collision(character.character_sprite):
                return True
        for mirror in self.mirror_list:
            if mirror.check_collision(character.character_sprite):
                return True
        for light_receiver in self.light_receiver_list:
            if light_receiver.check_collision(character.character_sprite):
                return True



class GameObject(arcade.Window):
    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, util.WINDOW_TITLE)
        self.elem_list = None
        self.mirror = None
        self.wall = None
        self.game_state = None
        self.set_mouse_visible(False)
        arcade.set_background_color(arcade.color.BROWN)
        self.game_menu = None
        self.win_screen = None
        self.tile_map = None
        self.character = None
        self.current_level = None

    def setup(self):
        self.game_state = 'menu'
        self.game_menu = InGameMenu()
        self.win_screen = WinScreen()
        self.character = Character('../../assets/character_right.png')
        self.elem_list = arcade.SpriteList()

        # TODO: eventually JSON file
        mirror_coordinate_list = [
            [WINDOW_WIDTH / 4, (WINDOW_HEIGHT / 3) * 2, -numpy.pi / 4],
            [(WINDOW_WIDTH / 2) + 50, WINDOW_HEIGHT - 100, 0],
            [WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4, numpy.pi / 2],
            [((WINDOW_WIDTH / 4) * 3) + 20, WINDOW_HEIGHT / 5, 0]
        ]
        wall_coordinate_list = [
            [784, 176, 1, 9, 0],
            [496, WINDOW_HEIGHT - 176, 1, 9, 0],
            [880, WINDOW_HEIGHT - 176, 1, 9, 0]
        ]
        light_receiver_coordinate_list = [
            [WINDOW_WIDTH - 128, WINDOW_HEIGHT - 128, 0],
            # [WINDOW_WIDTH / 3, (WINDOW_HEIGHT / 2), 0]
        ]
        light_source_coordinate_list = [
            # A 4th argument will make RadialLightSource with that angular spread instead of ParallelLightSource
            [WINDOW_WIDTH / 4, 48, numpy.pi / 2]
        ]

        self.current_level = Level(
            wall_coordinate_list,
            mirror_coordinate_list,
            light_receiver_coordinate_list,
            light_source_coordinate_list
        )

    def on_update(self, delta_time):
        self.character.update(self.current_level)
        if any(light_receiver.charge >= util.RECEIVER_THRESHOLD for light_receiver in self.current_level.light_receiver_list):
            self.game_state = 'win'

    def on_draw(self):
        self.clear()

        if self.game_state == 'menu':
            draw_title_menu()
        elif self.game_state == 'game' or self.game_state == 'paused':
            self.current_level.draw()
            self.character.draw()

            if self.game_state == 'paused':
                self.game_menu.draw()

        if self.game_state == 'win':
            self.win_screen.draw()

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

            if key == arcade.key.Q:
                if self.character.closest_interactable:
                    self.character.counter_clockwise = True
            if key == arcade.key.E:
                if self.character.closest_interactable:
                    self.character.clockwise = True

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

        elif self.game_state == 'win':
            if key == arcade.key.DOWN:
                self.win_screen.increment_selection()
            if key == arcade.key.UP:
                self.win_screen.decrement_selection()
            if key == arcade.key.ENTER:
                if self.win_screen.selection == 0:
                    self.setup()
                elif self.win_screen.selection == 1:
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

        if key == arcade.key.Q:
            self.character.counter_clockwise = False
        if key == arcade.key.E:
            self.character.clockwise = False



def main():
    window = GameObject()
    window.setup()
    arcade.run()


if __name__ == '__main__':
    main()
