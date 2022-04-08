import datetime
import os
import subprocess
import time
from abc import ABC
from enum import Enum, unique, auto
from typing import Dict, Any, Tuple

import numpy as numpy
import pyautogui as gui
from PIL import Image, ImageOps, ImageChops
from pytesseract import image_to_string

q_row_y = 770
a_row_y = 830
y_row_y = 896

positions = {
    "app": (185, 165),
    "play": (230, 700),
    "delete": (379, y_row_y),
    "submit": (235, 950),
    "next_word": (228, 743),

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


class ColorStateException(Exception):
    pass


class Interface(ABC):
    class Position:
        class Elem(Enum):
            KEYBOARD = auto()
            NEXT_GAME = auto()
            MATRIX = auto()

    def __init__(self, commands: [str], screen_elements: Dict[Enum, Any]) -> None:
        self._locations: Dict[Interface.Position.Elem, Any] = dict()
        self.commands = commands
        for element in Interface.Position.Elem:
            self._locations[element] = {
                "path": screen_elements[element]
            }

    def is_empty(self, rgb) -> bool:
        pass

    def is_ok(self, rgb) -> bool:
        pass

    def is_not_contained(self, rgb) -> bool:
        pass

    def is_contained(self, rgb) -> bool:
        pass

    def wait_next_game(self):
        print("Wait until next game can be started...")
        while not self._next_game_pixel_exists():
            time.sleep(.5)

    def _next_game_pixel_exists(self):
        pass

    def open_(self):
        subprocess.Popen(self.commands, shell=False, stdin=None, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, close_fds=True)
        print(f"Wait 2 seconds for process to open...")
        time.sleep(2)

    def setup(self):
        move_to("submit", 1)

    @classmethod
    def init(cls, model: str = None):
        interface: Interface
        elements = {
            Interface.Position.Elem.KEYBOARD: "locatables/keyboard.png",
            Interface.Position.Elem.NEXT_GAME: "locatables/next_game.png",
            Interface.Position.Elem.MATRIX: "locatables/matrix.png",
        }
        if model == "P30":
            interface = P30(elements)
        elif model == 'PSMART2019':
            interface = PSMART2019(elements)
        else:
            interface = PSMART2019(elements)
        ColorCode.init(interface)
        return interface


class P30(Interface):

    def __init__(self, elements: Dict[Interface.Position.Elem, Any]) -> None:
        commands = ["scrcpy", "--always-on-top", "--window-width", "470", "--window-height", "1015", "--window-x", "0",
                    "--window-y", "0"]
        super().__init__(commands, elements)

    def is_empty(self, rgb) -> bool:
        return rgb == (146, 148, 150)

    def is_ok(self, rgb) -> bool:
        return rgb == (13, 188, 40)

    def is_not_contained(self, rgb) -> bool:
        return rgb == (83, 83, 83)

    def is_contained(self, rgb) -> bool:
        return rgb == (250, 217, 57)

    def _next_game_pixel_exists(self):
        # color code just copy pasted! check with p30
        rgb = get_pixel_color_by_element("next_word")
        return rgb[0] in range(242, 252) and rgb[1] in range(143, 153) and rgb[2] in range(26, 36)


class PSMART2019(Interface):

    def __init__(self, elements: Dict[Interface.Position.Elem, Any]) -> None:
        commands = ["scrcpy", "--always-on-top", "--window-width", "470", "--window-height", "1015", "--window-x", "0",
                    "--window-y", "0", "-m", "1024"]
        super().__init__(commands, elements)

    def is_empty(self, rgb) -> bool:
        return rgb[0] in range(141, 152) and rgb[1] in range(143, 154) and rgb[2] in range(147, 158)

    def is_ok(self, rgb) -> bool:
        return rgb[0] in range(0, 11) and rgb[1] in range(155, 165) and rgb[2] in range(35, 45)

    def is_not_contained(self, rgb) -> bool:
        return all([val in range(78, 89) for val in rgb])

    def is_contained(self, rgb) -> bool:
        return rgb[0] in range(245, 256) and rgb[1] in range(205, 215) and rgb[2] in range(50, 66)

    def _next_game_pixel_exists(self):
        rgb = get_pixel_color_by_element("next_word")
        return rgb[0] in range(242, 252) and rgb[1] in range(143, 153) and rgb[2] in range(26, 36)


@unique
class ColorCode(Enum):
    OK = auto()
    NOT_CONTAINED = auto()
    CONTAINED = auto()
    EMPTY = auto()

    _model: Interface
    color_name_max_length: int

    @classmethod
    def init(cls, interface: Interface):
        cls._model = interface
        cls.color_name_max_length = max([len(color.name) for color in ColorCode])

    @classmethod
    def code(cls, code: tuple):
        if cls._model.is_ok(code):
            return ColorCode.OK
        elif cls._model.is_contained(code):
            return ColorCode.CONTAINED
        elif cls._model.is_not_contained(code):
            return ColorCode.NOT_CONTAINED
        elif cls._model.is_empty(code):
            return ColorCode.EMPTY
        else:
            raise ColorStateException("Color tuple " + str(code) + " unknown")


def click_on(element: str, duration: float = .5, echo: bool = True):
    if echo:
        print(f"Click on {element}...")
    x, y = positions[element]
    gui.moveTo(x, y, duration=duration)
    gui.leftClick(x, y)


def type(word: str, duration: float = .5, echo: bool = True):
    if echo:
        print(f"Type word {word}...")
    for c in word:
        click_on(c, duration, False)


def move_to(element: str, duration: float = .5):
    print(f"Move to {element}")
    x, y = positions[element]
    gui.moveTo(x, y, duration=duration)


def screenshot(region=(52, 178, 367, 440), with_datetime=True, path="/home/florian/Pictures/wordles", file_name=None):
    print("Take screenshot")
    if not file_name:
        file_name = "unnamed.png"
    date_string = str(datetime.datetime.now()) + "_" if with_datetime else ""
    date_string = date_string.replace(" ", "_")
    path = path + "/" + date_string + file_name
    return gui.screenshot(path, region=region), path


def preprocess_img(path: str, threshold: int = 5):
    print(f"Preprocess Image with threshold value: {threshold}")
    gui_screenshot = Image.open(path)
    gray_image = ImageOps.grayscale(gui_screenshot)
    gray = ImageChops.invert(gray_image)
    black_white = gray.point(lambda x: 0 if x < threshold else 255, '1')
    new_path = path.replace(".png", "_processed.png")
    black_white.save(new_path)
    crop_img(new_path)
    return new_path


def crop_img(in_p, out_p=None):
    img = Image.open(in_p)
    arr = numpy.array(img)
    arr = numpy.delete(arr, range(52, 90), 1)
    arr = numpy.delete(arr, range(90, 130), 1)
    arr = numpy.delete(arr, range(132, 167), 1)
    arr = numpy.delete(arr, range(167, 205), 1)
    img = Image.fromarray(arr)
    out = out_p if out_p else in_p
    img.save(out)
    return img


def get_colors(path: str) -> [[ColorCode]]:
    px = Image.open(path).load()

    color_matrix: [] = [None] * 6
    for i in range(6):
        color_matrix[i] = [ColorCode.EMPTY] * 5

    x, y = color_pos[0][0]
    pixel = px[x, y]
    if ColorCode.EMPTY == ColorCode.code(pixel):
        print(f"First position was {ColorCode.EMPTY.name}, returning immediately...")
        return color_matrix

    color_string = ""
    for i in range(0, 6):
        for j in range(0, 5):
            x, y = color_pos[i][j]
            pixel = px[x, y]
            try:
                color = ColorCode.code(pixel)
            except ColorStateException as e:
                raise ColorStateException(str(e) + f" at location ({i}|{j})")
            color_string += f"{i}|{j}: " + color.name + (
                    (ColorCode.color_name_max_length - len(color.name)) * " ") + " "
            color_matrix[i][j] = color
            if j == 4 and i != 5:
                color_string += "\n"

    print(color_string)
    return color_matrix


def read(path, psm=6):
    print(f"Read characters from {path}")
    text = image_to_string(Image.open(path), lang="deu",
                           config=f'--psm {psm} -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZÖÄÜ')
    print(f"Found words: [{', '.join(text.split())}]")
    return text


def scr_read(threshold: int = 5):
    _, path = screenshot()
    new_path = preprocess_img(path, threshold)
    text = read(new_path)
    os.remove(new_path)
    os.remove(path)
    return text


def get_pixel_color_by_element(element: str):
    element_position = positions[element]
    return get_pixel_color_by_position(element_position)


def get_pixel_color_by_position(pos: Tuple[int, int]):
    x, y = pos
    _, path = screenshot((x - 1, y - 1, 3, 3))
    px = Image.open(path).load()
    pixel = px[1, 1]
    os.remove(path)
    return pixel
