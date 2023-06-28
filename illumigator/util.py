from screeninfo import get_monitors, ScreenInfoError
import arcade
import numpy
import math

# ========================= System Constants =========================
try:
    for display in get_monitors():
        if display.is_primary:
            SCREEN_WIDTH = display.width
            SCREEN_HEIGHT = display.height
except ScreenInfoError:
    print("No monitors detected!")


# ========================= Game Constants =========================
WINDOW_WIDTH: int = 1280
WINDOW_HEIGHT: int = 720
WINDOW_TITLE: str = "IllumiGator"
COLORS: list[arcade.color] = [arcade.color.AQUAMARINE, arcade.color.BLUE, arcade.color.CHERRY,
                              arcade.color.DAFFODIL, arcade.color.EGGPLANT]
ENVIRON_PATH = "assets/"
VENV_PATH = "./venv/Lib/site-packages/illumigator/assets/"

# ========================= Sprite Constants =========================
# World Objects
WALL_SPRITE_INFO: tuple = ("wall.png", 2, 16, 16)  # path, scale, width, height
MIRROR_SPRITE_INFO: tuple = ("mirror.png", 1.3, 9, 48)
RECEIVER_SPRITE_INFO: tuple = ("light_receiver.png", 2, 32, 32)
PLACEHOLDER_SPRITE_INFO: tuple = ("sprite.png", 0.25, 128, 128)

# Player
PLAYER_SPRITE_RIGHT = "character_right.png"
PLAYER_SPRITE_LEFT = "character_left.png"


# ========================= Script Constants =========================
# Ray Casting Constants
MAX_RAY_DISTANCE = math.sqrt(WINDOW_WIDTH ** 2 + WINDOW_HEIGHT ** 2)  # Max distance before ray goes off-screen
STARTING_DISTANCE_VALUE = WINDOW_WIDTH**2 + WINDOW_HEIGHT**2  # Large number for starting out min distance calculations
MAX_DISTANCE: float = 1000
MAX_GENERATIONS: int = 50

# Light Source Constants
NUM_LIGHT_RAYS: int = 10

# Light Receiver Constants
CHARGE_DECAY: float = 0.991
LIGHT_INCREMENT: float = 0.009085 / NUM_LIGHT_RAYS
RECEIVER_THRESHOLD: float = 0.7

# Player Constants
PLAYER_REACH_DISTANCE_SQUARED: int = 100 ** 2
PLAYER_MOVEMENT_SPEED = 10
OBJECT_ROTATION_AMOUNT: float = 0.004


# ========================= Physics Functions =========================
def distance_squared(point1: numpy.array, point2: numpy.array) -> float:
    dx, dy = point1[0]-point2[0], point1[1]-point2[1]
    return dx*dx + dy*dy


def distance_squared_ordered_pair(point: numpy.array, x: float, y: float) -> float:
    dx, dy = point[0]-x, point[1]-y
    return dx*dx + dy*dy


def rotate_around_center(center: numpy.array, point: numpy.array, angle: float) -> numpy.array:
    relative_point = point - center
    rotated_point = numpy.array([
        relative_point[0]*math.cos(angle) - relative_point[1]*math.sin(angle),
        relative_point[0]*math.sin(angle) + relative_point[1]*math.cos(angle)
    ])
    return rotated_point + center


# ========================= File Handling Functions =========================
def load_sprite(
    filename: str | None = None,
    scale: float = 1,
    image_x: float = 0,
    image_y: float = 0,
    image_width: float = 0,
    image_height: float = 0,
    center_x: float = 0,
    center_y: float = 0,
    repeat_count_x: int = 1,
    repeat_count_y: int = 1,
    flipped_horizontally: bool = False,
    flipped_vertically: bool = False,
    flipped_diagonally: bool = False,
    hit_box_algorithm: str | None = "Simple",
    hit_box_detail: float = 4.5,
    texture: arcade.Texture | None = None,
    angle: float = 0
) -> arcade.Sprite:

    try:
        return arcade.Sprite(ENVIRON_PATH + filename, scale, image_x, image_y, image_width, image_height, center_x,
                             center_y, repeat_count_x, repeat_count_y, flipped_horizontally, flipped_vertically,
                             flipped_diagonally, hit_box_algorithm, hit_box_detail, texture, angle)
    except FileNotFoundError:
        return arcade.Sprite(VENV_PATH + filename, scale, image_x, image_y,
                             image_width, image_height, center_x, center_y, repeat_count_x, repeat_count_y,
                             flipped_horizontally, flipped_vertically, flipped_diagonally, hit_box_algorithm,
                             hit_box_detail, texture, angle)


def load_sound(filename: str) -> arcade.Sound:
    try:
        return arcade.load_sound(ENVIRON_PATH + filename)
    except FileNotFoundError:
        return arcade.load_sound(VENV_PATH + filename)


def load_texture(filename: str) -> arcade.Texture:
    try:
        return arcade.load_texture(ENVIRON_PATH + filename)
    except FileNotFoundError:
        return arcade.load_texture(VENV_PATH + filename)
