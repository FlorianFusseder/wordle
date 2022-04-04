import datetime
from enum import Enum, unique

import pyautogui as gui
from PIL import Image, ImageOps, ImageChops

q_row_y = 770
a_row_y = 830
y_row_y = 896

pos = {
    "app": (185, 165),
    "play": (230, 700),
    "delete": (379, y_row_y),
    "submit": (235, 950),

    "q": (25, q_row_y),
    "w": (65, q_row_y),
    "e": (107, q_row_y),
    "r": (150, q_row_y),
    "t": (192, q_row_y),
    "z": (237, q_row_y),
    "u": (277, q_row_y),
    "i": (318, q_row_y),
    "o": (360, q_row_y),
    "p": (403, q_row_y),
    "ü": (445, q_row_y),

    "a": (25, a_row_y),
    "s": (65, a_row_y),
    "d": (107, a_row_y),
    "f": (150, a_row_y),
    "g": (192, a_row_y),
    "h": (237, a_row_y),
    "j": (277, a_row_y),
    "k": (318, a_row_y),
    "l": (360, a_row_y),
    "ö": (403, a_row_y),
    "ä": (445, a_row_y),

    "y": (90, y_row_y),
    "x": (131, y_row_y),
    "c": (172, y_row_y),
    "v": (214, y_row_y),
    "b": (254, y_row_y),
    "n": (297, y_row_y),
    "m": (341, y_row_y),
}

color_pos = [
    [(34, 60), (110, 60), (185, 60), (260, 60), (333, 60)],
    [(34, 135), (110, 135), (185, 135), (260, 135), (333, 135)],
    [(34, 205), (110, 205), (185, 205), (260, 205), (333, 205)],
    [(34, 280), (110, 280), (185, 280), (260, 280), (333, 280)],
    [(34, 355), (110, 355), (185, 355), (260, 355), (333, 355)],
    [(34, 430), (110, 430), (185, 430), (260, 430), (333, 430)],
]


@unique
class ColorCode(Enum):
    OK = (13, 188, 40),
    NOT_CONTAINED = (83, 83, 83),
    CONTAINED = (250, 217, 57),
    EMPTY = (146, 148, 150),


color_map = {
    (13, 188, 40): ColorCode.OK,
    (250, 217, 57): ColorCode.CONTAINED,
    (83, 83, 83): ColorCode.NOT_CONTAINED,
    (146, 148, 150): ColorCode.EMPTY,
}


def click_on(element: str, duration: int = .5):
    x, y = pos[element]
    gui.moveTo(x, y, duration=duration)
    gui.leftClick(x, y)


def type(word: str, duration: int = .5):
    for c in word:
        click_on(c, duration)


def screenshot(region=(52, 178, 367, 440), with_datetime=True, path="/home/florian/Pictures/wordles", file_name=None):
    if not file_name:
        file_name = "unnamed.png"
    date_string = str(datetime.datetime.now()) if with_datetime else ""
    date_string = date_string.replace(" ", "_")
    gui.screenshot(path + "/" + date_string + "_" + file_name, region=region)


def greyscale(path: str):
    gui_screenshot = Image.open(path)
    gray_image = ImageOps.grayscale(gui_screenshot)
    inv_img = ImageChops.invert(gray_image)
    new_path = path.replace(".png", "_edited.png")
    inv_img.save(new_path)


def get_colors(path: str):
    px = Image.open(path).load()

    for i in range(0, 5):
        for j in range(0, 5):
            x, y = color_pos[i][j]
            pixel = px[x, y]
            color = color_map[pixel]
            print(f"{i}|{j}: " + color.name, end=", ")
            if j == 4:
                print("")
