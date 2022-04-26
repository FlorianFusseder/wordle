import datetime
import os
import subprocess
import tempfile
import time
from abc import ABC
from enum import Enum, unique, auto
from typing import Dict, Tuple

import numpy as numpy
import pyautogui as gui
from PIL import Image, ImageOps, ImageChops
from pytesseract import image_to_string


class ColorStateException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class MultipleColorMatches(Exception):
    pass


class RGB:

    @property
    def r(self):
        return self.__r

    @property
    def g(self):
        return self.__g

    @property
    def b(self):
        return self.__b

    @property
    def rgb(self) -> Tuple[int, int, int]:
        return self.__r, self.__g, self.__b

    def compare_with_range(self, other: 'RGB', _range: int = 5) -> bool:
        color_range = self.__get_as_range(_range)
        return other.rgb[0] in color_range[0] and \
               other.rgb[1] in color_range[1] and \
               other.rgb[2] in color_range[2]

    def __get_as_range(self, _range: int) -> Tuple[range, range, range]:
        return (range(self.r - _range, self.r + _range + 1),
                range(self.g - _range, self.g + _range + 1),
                range(self.b - _range, self.b + _range + 1))

    def __iter__(self):
        return RGBIterator(self)

    def __init__(self, code: Tuple[int, int, int] = (-1, -1, -1)) -> None:
        self.__r, self.__g, self.__b = code

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, RGB):
            return False
        return self.rgb == o.rgb

    def __str__(self) -> str:
        return f"RGB(R: {self.__r}, G: {self.__g}, B: {self.__b})"

    def __repr__(self):
        return str(self)


class RGBIterator:

    def __init__(self, rgb: RGB) -> None:
        self.__index: int = 0
        self.__element = rgb

    def __next__(self):
        color: int
        if self.__index == 0:
            color = self.__element.r
        elif self.__index == 1:
            color = self.__element.g
        elif self.__index == 2:
            color = self.__element.b
        else:
            raise StopIteration
        self.__index += 1
        return color


@unique
class ColorCode(Enum):
    OK = auto()
    NOT_CONTAINED = auto()
    CONTAINED = auto()
    EMPTY = auto()


class Interface(ABC):

    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, value):
        self._identifier = value

    @property
    def commands(self):
        return self._commands

    @commands.setter
    def commands(self, value):
        self._commands = value.split()

    @property
    def color_positions(self):
        return self._color_positions

    @color_positions.setter
    def color_positions(self, value):
        self._color_positions = value

    @property
    def color_codes(self):
        return self._color_codes

    @color_codes.setter
    def color_codes(self, value):
        self._color_codes = value

    @property
    def elements(self):
        return self._elements

    @elements.setter
    def elements(self, value):
        self._elements = value

    @property
    def endscreen_window(self):
        return self._endscreen_window

    @endscreen_window.setter
    def endscreen_window(self, value):
        self._endscreen_window = value

    @property
    def next_word_rgb(self):
        return self._next_word_rgb

    @next_word_rgb.setter
    def next_word_rgb(self, value):
        self._next_word_rgb = value

    def __init__(self) -> None:
        self._identifier: str = ""
        self._commands: [str] = ""
        self._color_positions: [[Tuple[int, int]]] = None
        self._color_codes: Dict[ColorCode, RGB] = {
            ColorCode.OK: RGB(),
            ColorCode.NOT_CONTAINED: RGB(),
            ColorCode.CONTAINED: RGB(),
            ColorCode.EMPTY: RGB()
        }
        self._elements: Dict[str, Tuple[int, int]] = {
            "delete": (-1, -1),
            "submit": (-1, -1),
            "q": (-1, -1),
            "w": (-1, -1),
            "e": (-1, -1),
            "r": (-1, -1),
            "t": (-1, -1),
            "z": (-1, -1),
            "u": (-1, -1),
            "i": (-1, -1),
            "o": (-1, -1),
            "p": (-1, -1),
            "ü": (-1, -1),
            "a": (-1, -1),
            "s": (-1, -1),
            "d": (-1, -1),
            "f": (-1, -1),
            "g": (-1, -1),
            "h": (-1, -1),
            "j": (-1, -1),
            "k": (-1, -1),
            "l": (-1, -1),
            "ö": (-1, -1),
            "ä": (-1, -1),
            "y": (-1, -1),
            "x": (-1, -1),
            "c": (-1, -1),
            "v": (-1, -1),
            "b": (-1, -1),
            "n": (-1, -1),
            "m": (-1, -1),
            "ß": (-1, -1),
            "next_word": (-1, -1),
            "home_button": (-1, -1),
        }
        self._next_word_rgb: RGB = None
        self._endscreen_window = (-1, -1, -1, -1)

    def wait_for_endscreen(self):
        x, y = self.elements["next_word"]
        rgb_next = self.get_pixel_color_by_position((x, y))
        print("Waiting for endscreen...")
        while not self.next_word_rgb.compare_with_range(rgb_next):
            time.sleep(.2)
            rgb_next = self.get_pixel_color_by_position((x, y))

    def make_endscreen_screenshot(self, _session_path):
        screenshot(self.endscreen_window, False, _session_path, "endscreen.png")

    def open_(self):
        subprocess.Popen(self.commands, shell=False, stdin=None, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, close_fds=True)
        print(f"Wait 2 seconds for process to open...")
        time.sleep(2)

    def click_on(self, element: str, duration: float = .5, echo: bool = True):
        x, y = self.elements[element]
        gui.moveTo(x, y, duration=duration)
        gui.leftClick(x, y)

    def type(self, word: str, duration: float = .5, echo: bool = True):
        if echo:
            print(f"Type word {word}...")
        for c in word:
            self.click_on(c, duration, False)

    def put_solution(self, next_word):
        w = next_word.lower()
        print(f"Put word: {next_word}")
        self.type(w[:1], echo=False)
        self.type(w[1:], duration=.1, echo=False)
        self.click_on("submit")

    def move_to(self, element: str, duration: float = .5):
        x, y = self.elements[element]
        gui.moveTo(x, y, duration=duration)

    def __get_pixel_matrix(self):
        left, top = self.color_positions[0][0]
        right, bottom = self.color_positions[len(self.color_positions) - 1][len(self.color_positions[0]) - 1]
        width = right - left
        height = bottom - top
        scr, path = screenshot((left, top, width + 1, height + 1))
        px = Image.open(path).load()
        os.remove(path)

        matrix = []
        for row_ in range(6):
            row = []
            for col_ in range(5):
                x, y = self.color_positions[row_][col_]
                x -= left
                y -= top
                pixel = px[x, y]
                row.append(RGB(pixel))
            matrix.append(row)
        return matrix

    def get_colors(self, attempt_row: int, check_if_some_empty_in_current_row: bool = True) -> [[ColorCode]]:
        color_matrix: [[ColorCode]] = []
        for _ in range(6):
            color_matrix.append([ColorCode.EMPTY] * 5)

        while True:
            matrix: [[Tuple[int, int]]] = self.__get_pixel_matrix()
            for row in range(attempt_row + 1):
                for col in range(5):
                    rgb: RGB = matrix[row][col]
                    try:
                        color: ColorCode = self.__get_rgb_code(rgb)
                    except ColorStateException as e:
                        raise ColorStateException(str(e) + f" at location ({col}|{row})")
                    color_matrix[row][col] = color
            if not check_if_some_empty_in_current_row:
                break
            elif color_matrix[attempt_row][0] != ColorCode.EMPTY and \
                    any([code == ColorCode.EMPTY for code in color_matrix[attempt_row]]):
                continue
            else:
                break
        return color_matrix

    @staticmethod
    def print_matrix(matrix: [[ColorCode]]):
        if matrix[0][0] == ColorCode.EMPTY:
            print(f"All {ColorCode.EMPTY.name}, skip printing...")
            return

        matrix_string = ""
        for row in range(len(matrix)):
            for col in range(len(matrix[row])):
                matrix_string += f"{col}|{row}: " + matrix[row][col].name + (
                        (13 - len(matrix[row][col].name)) * " ") + " "
            matrix_string += "\n"
        print(matrix_string)

    def get_pixel_color_by_element(self, element: str) -> RGB:
        element_position = self.elements[element]
        return self.get_pixel_color_by_position(element_position)

    @staticmethod
    def get_pixel_color_by_position(pos: Tuple[int, int]) -> RGB:
        x, y = pos
        path = tempfile.gettempdir() + f"/tmp_{int(round(datetime.datetime.now().timestamp()))}.png"
        gui.screenshot(path, region=(x - 1, y - 1, 3, 3))
        px = Image.open(path).load()
        pixel = px[1, 1]
        os.remove(path)
        return RGB(pixel)

    def get_color_code_by_position(self, pos: Tuple[int, int]) -> ColorCode:
        pixel_rgb: RGB = self.get_pixel_color_by_position(pos)
        return self.__get_rgb_code(pixel_rgb)

    def __get_rgb_code(self, rgb: RGB) -> ColorCode:
        color_codes = [color_code for color_code, rgb_ in self._color_codes.items() if rgb.compare_with_range(rgb_)]
        if len(color_codes) == 1:
            return color_codes[0]
        elif len(color_codes) > 1:
            raise MultipleColorMatches(f"{rgb} matched multiple colors {[code.name for code in color_codes]}")
        else:
            raise ColorStateException(f"Could not recognize color: {rgb})")

    def __str__(self) -> str:
        return self.identifier


def mouse_position():
    return gui.position()


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


def screenshot(region=(52, 178, 367, 440), with_datetime=True, path="/home/florian/Pictures/wordles", file_name=None):
    if not file_name:
        file_name = "unnamed.png"
    date_string = str(datetime.datetime.now()) + "_" if with_datetime else ""
    date_string = date_string.replace(" ", "_")
    path = path + "/" + date_string + file_name
    return gui.screenshot(path, region=region), path


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


def move_to(param, param1):
    gui.moveTo(param, param1)
