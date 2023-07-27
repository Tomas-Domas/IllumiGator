import heapq
import json
import math
import os
import subprocess

import arcade
import numpy
from screeninfo import get_monitors


# ========================= Game Constants =========================
# Window
FRAME_RATE = 40
UNIVERSAL_SPEED_MULTIPLIER = 60/FRAME_RATE
WORLD_WIDTH: int = 1280  # Width of the game for calculating coordinates and positions
WORLD_HEIGHT: int = 720  # Height of the game
WINDOW_TITLE: str = "IllumiGator"
X_MIDPOINT = WORLD_WIDTH // 2
Y_MIDPOINT = WORLD_HEIGHT // 2

# Monitor
for m in get_monitors():
    if m.is_primary:
        SCREEN_WIDTH = m.width
        SCREEN_HEIGHT = m.height



# ========================= Asset Constants =========================
# World Objects
WALL_SPRITE_INFO: tuple = ("wall.png", 2.5, 16, 16)  # path, scale, width, height
MIRROR_SPRITE_INFO: tuple = ("mirror.png", 1.3, 9, 48)
LENS_SPRITE_INFO: tuple = ("lens.png", 1.3, 9, 48)
SOURCE_SPRITE_INFO: tuple = ("sun.png", 1, 32, 32)
RECEIVER_SPRITE_INFO: tuple = ("<PLANET NAME>", 2, 32, 32)
PLAYER_SPRITE_INFO: tuple = ("00_gator_left.png", 1, 24, 24)
PLACEHOLDER_SPRITE_INFO: tuple = ("sprite.png", 0.25, 128, 128)
WALL_SIZE = WALL_SPRITE_INFO[1] * WALL_SPRITE_INFO[2]

# Player
PLAYER_IDLE_TIME = 4
PLAYER_SPRITE = "0{i}_gator_{direction}.png"
PLAYER_DEAD_SPRITE = "Gator_death_{direction}{i}.png"
PLAYER_IDLE_SPRITE = "Gator_idle_{direction}{i}.png"
ENEMY_SPRITE = "FLman_running_{direction}{i}.png"
ENEMY_SLEEP_SPRITE = "FLman_sleeping{i}.png"

# Paths
ENVIRON_ASSETS_PATH = os.path.join(os.path.split(__file__)[0], "assets/")
VENV_ASSETS_PATH = os.path.join(os.path.split(__file__)[0], "assets/")
ENVIRON_DATA_PATH = os.path.join(os.path.split(__file__)[0], "data/")
VENV_DATA_PATH = "./venv/Lib/site-packages/illumigator/data/"

# Fonts
MENU_FONT = "Press Start 2P"
BODY_FONT_SIZE = 12
H3_FONT_SIZE = 24
H2_FONT_SIZE = 36
H1_FONT_SIZE = 48



# ========================= Script Constants =========================
# Ray Casting Constants
MAX_RAY_DISTANCE = math.sqrt(WORLD_WIDTH**2 + WORLD_HEIGHT**2)  # Max distance before ray goes off-screen
MAX_GENERATIONS: int = 20
INDEX_OF_REFRACTION: float = 1.5

# Light Source Constants
NUM_LIGHT_RAYS: int = 30

# Light Receiver Constants
CHARGE_DECAY: float = 0.99
LIGHT_INCREMENT: float = 0.012 / NUM_LIGHT_RAYS
RECEIVER_THRESHOLD: float = 0.55

# Player Constants
PLAYER_REACH_DISTANCE_SQUARED: int = 150 ** 2
PLAYER_MOVEMENT_SPEED = 8 * UNIVERSAL_SPEED_MULTIPLIER
OBJECT_ROTATION_AMOUNT: float = 0.01 * UNIVERSAL_SPEED_MULTIPLIER

# Enemy Constants
ENEMY_MOVEMENT_SPEED = 4 * UNIVERSAL_SPEED_MULTIPLIER

MASTER_VOLUME = 1
MUSIC_VOLUME = 1
EFFECTS_VOLUME = 1



# ========================= Physics Functions =========================
def distance_squared(point1: numpy.ndarray, point2: numpy.ndarray) -> float:
    dx, dy = point1[0] - point2[0], point1[1] - point2[1]
    return dx * dx + dy * dy

def rotate_around_point(center: numpy.ndarray, point: numpy.ndarray, angle: float) -> numpy.ndarray:
    cosine = math.cos(angle)
    sine = math.sin(angle)
    relative_point = point - center
    rotated_point = numpy.array(
        [
            relative_point[0] * cosine - relative_point[1] * sine,
            relative_point[0] * sine + relative_point[1] * cosine,
        ]
    )
    return rotated_point + center

def rotate(point: numpy.ndarray, angle: float) -> numpy.ndarray:
    cosine = math.cos(angle)
    sine = math.sin(angle)
    return numpy.array(
        [
            point[0] * cosine - point[1] * sine,
            point[0] * sine + point[1] * cosine,
        ]
    )


def two_d_cross_product(vector1: numpy.ndarray, vector2: numpy.ndarray) -> float:
    return vector1[0] * vector2[1] - vector1[1] * vector2[0]



# ========================= File Handling Functions =========================
def load_sprite(
        filename: str | None = None,
        scale: float = 1,
        image_x: float = 0, image_y: float = 0,
        image_width: float = 0, image_height: float = 0,
        center_x: float = 0, center_y: float = 0,
        repeat_count_x: int = 1, repeat_count_y: int = 1,
        flipped_horizontally: bool = False, flipped_vertically: bool = False, flipped_diagonally: bool = False,
        hit_box_algorithm: str | None = "Simple", hit_box_detail: float = 4.5,
        texture: arcade.Texture | None = None,
        angle: float = 0,
) -> arcade.Sprite:
    try:
        return arcade.Sprite(
            ENVIRON_ASSETS_PATH + filename,
            scale,
            image_x, image_y,
            image_width, image_height,
            center_x, center_y,
            repeat_count_x, repeat_count_y,
            flipped_horizontally, flipped_vertically, flipped_diagonally,
            hit_box_algorithm, hit_box_detail,
            texture,
            angle,
        )
    except FileNotFoundError:
        return arcade.Sprite(
            VENV_ASSETS_PATH + filename,
            scale,
            image_x, image_y,
            image_width, image_height,
            center_x, center_y,
            repeat_count_x, repeat_count_y,
            flipped_horizontally, flipped_vertically, flipped_diagonally,
            hit_box_algorithm, hit_box_detail,
            texture,
            angle,
        )


def load_sound(filename: str, streaming=False) -> arcade.Sound:
    try:
        return arcade.load_sound(ENVIRON_ASSETS_PATH + filename, streaming)
    except FileNotFoundError:
        return arcade.load_sound(VENV_ASSETS_PATH + filename, streaming)


def load_texture(filename: str) -> arcade.Texture:
    try:
        return arcade.load_texture(ENVIRON_ASSETS_PATH + filename)
    except FileNotFoundError:
        return arcade.load_texture(VENV_ASSETS_PATH + filename)


def load_data(filename: str, is_level=False, is_system_level=True) -> dict:
    if is_level and is_system_level:
        addon_path = "levels/system/"
    elif is_level and not is_system_level:
        addon_path = "levels/community/"
    else:
        addon_path = ""

    try:
        file = open(ENVIRON_DATA_PATH + addon_path + filename)
    except FileNotFoundError:
        file = open(VENV_DATA_PATH + addon_path + filename)

    obj = json.load(file)
    file.close()
    return obj


def write_data(filename: str, obj: dict) -> None:
    json_obj = json.dumps(obj)

    if os.path.exists(ENVIRON_DATA_PATH):
        with open(ENVIRON_DATA_PATH + filename, "w") as outfile:
            outfile.write(json_obj)
    else:
        with open(VENV_DATA_PATH + filename, "w") as outfile:
            outfile.write(json_obj)


def update_community_metadata() -> None:
    last_modified_dict = {}
    addon_path = "levels/community/"

    # Get file names and modification date from community directory
    try:
        files = os.scandir(ENVIRON_DATA_PATH + addon_path)
    except FileNotFoundError:
        files = os.scandir(VENV_DATA_PATH + addon_path)

    for file in files:
        if not file.name == "levels.json":
            last_modified_dict[file.name] = os.path.getmtime(file)

    # Get levels.json metadata file from community directory
    try:
        metadata_file = open(ENVIRON_DATA_PATH + addon_path + "levels.json")
    except FileNotFoundError:
        metadata_file = open(VENV_DATA_PATH + addon_path + "levels.json")

    json_obj = json.load(metadata_file)
    metadata_file.close()

    # Add datapoint (new file) to levels.json if necessary
    for filename in last_modified_dict:
        if not (filename in json_obj["levels"]):
            json_obj["levels"][filename] = {
                "date_modified": last_modified_dict[filename],
                "level_name": load_data(filename, True, False)["level_name"],
                "planet_name": load_data(filename, True, False)["planet"]
            }

    # Update levels.json with new data if necessary
    for filename in last_modified_dict:
        if last_modified_dict[filename] != json_obj["levels"][filename]["date_modified"]:
            json_obj["levels"][filename] = {
                "date_modified": last_modified_dict[filename],
                "level_name": load_data(filename, True, False)["level_name"],
                "planet_name": load_data(filename, True, False)["planet"]
            }

    # Remove old datapoints (deleted file) in levels.json if necessary
    list_of_datapoints_to_delete = []

    for filename in json_obj["levels"]:
        if not (filename in last_modified_dict):
            list_of_datapoints_to_delete.append(filename)

    for i in range(0, len(list_of_datapoints_to_delete)):
        del json_obj["levels"][list_of_datapoints_to_delete[i]]

    write_data("levels/community/levels.json", json_obj)


# Returns the total number of levels and a page of levels
def get_level_metadata(page_size: int = 15, page: int = 1, is_community=False) -> tuple[int, list, list]:
    addon_path = "levels/community/" if is_community else "levels/system/"
    level_list_unsorted = []
    level_list_sorted = []
    filenames_unsorted = []
    filenames_sorted = []
    min_at_page = (page-1) * page_size
    max_at_page = page * page_size

    try:
        metadata_file = open(ENVIRON_DATA_PATH + addon_path + "levels.json")
    except FileNotFoundError:
        metadata_file = open(VENV_DATA_PATH + addon_path + "levels.json")

    levels = json.load(metadata_file)["levels"]

    if is_community:
        for level in levels:
            heapq.heappush(filenames_unsorted, (-1 * levels[level]["date_modified"], level))

        for level in levels:
            heapq.heappush(level_list_unsorted, (-1 * levels[level]["date_modified"], levels[level]))

        for i in range(len(level_list_unsorted)):
            level_list_sorted.append(heapq.heappop(level_list_unsorted)[1])

        for i in range(len(filenames_unsorted)):
            filenames_sorted.append(heapq.heappop(filenames_unsorted)[1])

        return len(levels), level_list_sorted[min_at_page:max_at_page], filenames_sorted[min_at_page:max_at_page]

    for level in levels:
        filenames_sorted.append(level)
        level_list_sorted.append(levels[level])

    return len(levels), level_list_sorted[min_at_page:max_at_page], filenames_sorted[min_at_page:max_at_page]


def opendir(filename):
    try:
        os.startfile(filename)
    except FileNotFoundError:
        raise FileNotFoundError
    except:
        subprocess.Popen(['xdg-open', filename])
