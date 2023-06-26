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
            arcade.load_texture(util.PLAYER_SPRITE_RIGHT),
            arcade.load_texture(util.PLAYER_SPRITE_LEFT)
        ]

        self.character_sprite = arcade.Sprite(util.PLAYER_SPRITE_RIGHT, scale_factor, image_width=image_width,
                                              image_height=image_height, center_x=center_x, center_y=center_y,
                                              hit_box_algorithm="Simple")
        self.left = False
        self.right = False
        self.up = False
        self.down = False

        self.interactive_line = None
        self.rotation_dir = 0
        self.player = pyglet.media.player.Player()

        self.walking_sound = arcade.load_sound("assets/new_walk.wav")

        self.rotation_factor = 0.00

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
            closest_mirror.move(numpy.zeros(2), self.rotation_dir * util.OBJECT_ROTATION_AMOUNT * self.rotation_factor)



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
        # Animated Wall:
        animated_wall = worldobjects.Wall(
                numpy.array([WINDOW_WIDTH-176, WINDOW_HEIGHT-240]),
                numpy.array([1, 1]), 0
            )
        animated_wall.make_animation(numpy.array([128, 0]), 0.02)
        self.wall_list.append(animated_wall)

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


    def update(self, character: Character):
        for wall in self.wall_list:
            if wall.obj_animation is not None:
                wall.apply_object_animation(character)
        for light_source in self.light_sources_list:
            light_source.cast_rays(self.wall_list + self.mirror_list + self.light_receiver_list + self.light_sources_list)
        for light_receiver in self.light_receiver_list:
            light_receiver.charge *= util.CHARGE_DECAY


    def draw(self):
        for wall in self.wall_list:
            wall.draw()
        for mirror in self.mirror_list:
            mirror.draw()
        for light_source in self.light_sources_list:
            light_source.draw()
        for light_receiver in self.light_receiver_list:
            light_receiver.draw()


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
        arcade.set_background_color(arcade.color.BLACK)
        self.game_menu = None
        self.win_screen = None
        self.tile_map = None
        self.character = None
        self.current_level = None
        self.background = None


    def setup(self):
        self.game_state = 'menu'
        self.background = arcade.Sprite('assets/flowers.jpg', 0.333333, center_x = util.WINDOW_WIDTH / 2, center_y = util.WINDOW_HEIGHT / 2)
        self.background.alpha = 100
        self.game_menu = InGameMenu()
        self.win_screen = WinScreen()
        self.character = Character()
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
        if self.game_state == 'game':
            self.character.update(self.current_level)
            self.current_level.update(self.character)
            if any(light_receiver.charge >= util.RECEIVER_THRESHOLD for light_receiver in self.current_level.light_receiver_list):
                self.game_state = 'win'


    def on_draw(self):
        self.clear()

        if self.game_state == 'menu':
            draw_title_menu()
        elif self.game_state == 'game' or self.game_state == 'paused':
            self.background.draw()
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
            if key == arcade.key.A or key == arcade.key.LEFT:
                self.character.left = True
            if key == arcade.key.S or key == arcade.key.DOWN:
                self.character.down = True
            if key == arcade.key.D or key == arcade.key.RIGHT:
                self.character.right = True

            if key == arcade.key.Q:
                self.character.rotation_dir += 1
            if key == arcade.key.E:
                self.character.rotation_dir -= 1

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
                    self.game_state = 'menu'
                elif self.win_screen.selection == 1:
                    self.setup()

    def on_key_release(self, key, key_modifiers):
        if key == arcade.key.W or key == arcade.key.UP:
            self.character.up = False
        if key == arcade.key.A or key == arcade.key.LEFT:
            self.character.left = False
        if key == arcade.key.S or key == arcade.key.DOWN:
            self.character.down = False
        if key == arcade.key.D or key == arcade.key.RIGHT:
            self.character.right = False
        self.character.update(self.current_level)

        if key == arcade.key.Q:
            self.character.rotation_dir -= 1
        if key == arcade.key.E:
            self.character.rotation_dir += 1



def main():
    window = GameObject()
    window.setup()
    arcade.run()


if __name__ == '__main__':
    main()
