import datetime
from enum import Enum, unique, auto

import pyautogui as gui
from pytesseract import image_to_string
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
class WordleColor(Enum):
    OK = auto()
    NOT_CONTAINED = auto()
    CONTAINED = auto()
    EMPTY = auto()

    @classmethod
    def code(cls, code: tuple):
        if code == (13, 188, 40):
            return WordleColor.OK
        elif code == (250, 217, 57):
            return WordleColor.CONTAINED
        elif code == (83, 83, 83):
            return WordleColor.NOT_CONTAINED
        elif code == (146, 148, 150):
            return WordleColor.EMPTY
        else:
            raise NotImplementedError("Color tuple " + str(code) + " unknown")


def click_on(element: str, duration: int = .5):
    print(f"Click on {element}...")
    x, y = pos[element]
    gui.moveTo(x, y, duration=duration)
    gui.leftClick(x, y)


def type(word: str, duration: int = .5):
    print(f"Type word {word}...")
    for c in word:
        click_on(c, duration)


def screenshot(region=(52, 178, 367, 440), with_datetime=True, path="/home/florian/Pictures/wordles", file_name=None):
    print("Take screenshot")
    if not file_name:
        file_name = "unnamed.png"
    date_string = str(datetime.datetime.now()) if with_datetime else ""
    date_string = date_string.replace(" ", "_")
    gui.screenshot(path + "/" + date_string + "_" + file_name, region=region)


def preprocess_img(path: str):
    print("Preprocess Image")
    gui_screenshot = Image.open(path)
    gray_image = ImageOps.grayscale(gui_screenshot)
    gray = ImageChops.invert(gray_image)
    black_white = gray.point(lambda x: 0 if x < 5 else 255, '1')
    new_path = path.replace(".png", "_edited.png")
    return black_white.save(new_path)


def get_colors(path: str):
    print("Get Colors...")
    px = Image.open(path).load()

    for i in range(0, 5):
        for j in range(0, 5):
            x, y = color_pos[i][j]
            pixel = px[x, y]
            color = WordleColor.code(pixel)
            print(f"{i}|{j}: " + color.name, end=", ")
            if j == 4:
                print("")


def read(path, psm=6):
    print(f"Read characters from {path}")
    text = image_to_string(Image.open(path), lang="deu",
                           config=f'--psm {psm} -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZÖÄÜ')
    print(f"Found word {text}")
    return text
