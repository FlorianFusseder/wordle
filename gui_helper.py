import datetime

import pyautogui as gui

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
    date_string = datetime.datetime.now() if with_datetime else ""
    gui.screenshot(path + "/" + str(date_string) + "_" + file_name, region=region)
