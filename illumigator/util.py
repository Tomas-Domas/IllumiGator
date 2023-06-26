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
    print('No monitors detected!')



# ========================= Game Constants =========================
WINDOW_WIDTH: int = 1280
WINDOW_HEIGHT: int = 720
WINDOW_TITLE: str = 'IllumiGator'
COLORS: list[arcade.color] = [arcade.color.AQUAMARINE, arcade.color.BLUE, arcade.color.CHERRY, arcade.color.DAFFODIL, arcade.color.EGGPLANT]



# ========================= Sprite Constants =========================
# World Objects
WALL_SPRITE_INFO: tuple = ("assets/wall.png", 2, 16, 16)  # path, scale, width, height
MIRROR_SPRITE_INFO: tuple = ("assets/mirror.png", 1.3, 9, 48)
RECEIVER_SPRITE_INFO: tuple = ("assets/light_receiver.png", 2, 32, 32)
PLACEHOLDER_SPRITE_INFO: tuple = ("assets/light_source.png", 2, 16, 16)

# Player
PLAYER_SPRITE_RIGHT = 'assets/character_right.png'
PLAYER_SPRITE_LEFT = 'assets/character_left.png'



# ========================= Script Constants =========================
# Ray Casting Constants
MAX_RAY_DISTANCE = math.sqrt(WINDOW_WIDTH ** 2 + WINDOW_HEIGHT ** 2) # maximum distance a ray can travel before going off-screen
STARTING_DISTANCE_VALUE = WINDOW_WIDTH**2 + WINDOW_HEIGHT**2  # WINDOW_DIAGONAL_LENGTH**2. Large number for starting out min distance calculations
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



# ========================= Functions =========================
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
