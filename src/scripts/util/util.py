import math
import numpy
import arcade
from screeninfo import get_monitors, ScreenInfoError

# System Constants
try:
    for display in get_monitors():
        if display.is_primary:
            SCREEN_WIDTH = display.width
            SCREEN_HEIGHT = display.height
except ScreenInfoError:
    print('No monitors detected!')


# Game Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = 'IllumiGator'
COLORS = [arcade.color.AQUAMARINE, arcade.color.BLUE, arcade.color.CHERRY, arcade.color.DAFFODIL, arcade.color.EGGPLANT]


# Script Constants
MAX_RAY_DISTANCE = math.sqrt(WINDOW_WIDTH ** 2 + WINDOW_HEIGHT ** 2) # maximum distance a ray can travel before going off-screen
STARTING_DISTANCE_VALUE = WINDOW_WIDTH**2 + WINDOW_HEIGHT**2  # WINDOW_DIAGONAL_LENGTH**2. Large number for starting out min distance calculations


# Functions
def distance_squared(point1: numpy.array, point2: numpy.array) -> float:
    dx, dy = point1[0]-point2[0], point1[1]-point2[1]
    return dx*dx + dy*dy

def convert_angle_for_arcade(angle_rads: float) -> float:
    return angle_rads * 180 / numpy.pi

def rotate_around_center(point, angle, center):
    relative_point = point - center
    rotated_point = numpy.array([
        relative_point[0]*math.cos(angle) - relative_point[1]*math.sin(angle),
        relative_point[0]*math.sin(angle) + relative_point[1]*math.cos(angle)
    ])
    return rotated_point + center
