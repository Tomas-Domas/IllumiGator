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
STARTING_DISTANCE_VALUE = (WINDOW_WIDTH+WINDOW_HEIGHT)**2  # Very large number to start min_distance calculations at


# Functions
def distance_squared(point1: numpy.array, point2: numpy.array) -> float:
    return (point1[0]-point2[0])*(point1[0]-point2[0]) + (point1[1]-point2[1])*(point1[1]-point2[1])

def convert_angle_for_arcade(angle_rads: float) -> float:
    return -angle_rads * 180 / numpy.pi
