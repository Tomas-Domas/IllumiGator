import math
import numpy
import arcade
from screeninfo import get_monitors, ScreenInfoError



# ========================= System Constants =========================
try:
    for display in get_monitors():
        if display.is_primary:
            SCREEN_WIDTH = display.width
            SCREEN_HEIGHT = display.height
except ScreenInfoError:
    print('No monitors detected!')



# ========================= Game Constants =========================
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = 'IllumiGator'
COLORS = [arcade.color.AQUAMARINE, arcade.color.BLUE, arcade.color.CHERRY, arcade.color.DAFFODIL, arcade.color.EGGPLANT]

# ========================= Sprite Constants =========================
WALL_SPRITE_INFO = ("../../assets/wall.png", 1, 16, 16)
MIRROR_SPRITE_INFO = ("../../assets/mirror.png", 1, 9, 48)
RECEIVER_SPRITE_INFO = ("../../assets/light_receiver.png", 1, 32, 32)

# ========================= Script Constants =========================
# Ray Casting Constants
MAX_RAY_DISTANCE = math.sqrt(WINDOW_WIDTH ** 2 + WINDOW_HEIGHT ** 2) # maximum distance a ray can travel before going off-screen
STARTING_DISTANCE_VALUE = WINDOW_WIDTH**2 + WINDOW_HEIGHT**2  # WINDOW_DIAGONAL_LENGTH**2. Large number for starting out min distance calculations
MAX_DISTANCE: float = 1000
MAX_GENERATIONS: int = 5

# Light Source Constants
NUM_LIGHT_RAYS = 50

# Light Receiver Constants
CHARGE_DECAY = 0.95
LIGHT_INCREMENT = 0.1

# ========================= Functions =========================
def distance_squared(point1: numpy.array, point2: numpy.array) -> float:
    dx, dy = point1[0]-point2[0], point1[1]-point2[1]
    return dx*dx + dy*dy

def rotate_around_center(center: numpy.array, point: numpy.array, angle: float):
    relative_point = point - center
    rotated_point = numpy.array([
        relative_point[0]*math.cos(angle) - relative_point[1]*math.sin(angle),
        relative_point[0]*math.sin(angle) + relative_point[1]*math.cos(angle)
    ])
    return rotated_point + center
