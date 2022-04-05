import datetime
import json
import os
import subprocess
import time
from typing import List

import click

import gui_helper as gui
import word_list as wh
import wordle


class WordleState:

    def __init__(self) -> None:
        self.word_glob = "." * 5
        self.char_contained_list = []
        self.char_not_contained = ""

    def add_solved(self, c, i):
        self.word_glob = self.word_glob[:i] + c + self.word_glob[i + 1:]

    def add_contained(self, c, i):
        contained_word = "." * 5
        contained_word = contained_word[:i] + c + contained_word[i + 1:]
        self.char_contained_list.append(contained_word)

    def add_not_contained(self, c):
        self.char_not_contained = self.char_not_contained + c


class WordleContainer:

    def __init__(self) -> None:
        self.state = WordleState()
        self.solution = None
        self.states = []
        self.word_list = []

    def update(self, text, colors):
        self.states.append(self.state)
        self.state = WordleState()

        number = solution_number(colors)
        if number == 0:
            raise Exception("Cannot update if no rows are solved yet...")

        for i in range(number):
            for j in range(0, 5):
                c = text[j]
                color_code = colors[i][j]

                if color_code == gui.WordleColor.OK:
                    self.state.add_solved(c, j)
                elif color_code == gui.WordleColor.CONTAINED:
                    self.state.add_contained(c, j)
                elif color_code == gui.WordleColor.NOT_CONTAINED:
                    self.state.add_not_contained(c)
                elif color_code == gui.WordleColor.EMPTY:
                    break
            text = text[6:]

    def find(self) -> List[str]:
        words = wordle.find_words(self.state.word_glob, self.state.char_contained_list, self.state.char_not_contained,
                                  False)
        if not words:
            raise Exception("No Words could be found!")
        return words

    def set_solved(self, solution, path=None):
        self.solution = solution
        file_name = "game_data.json"

        path = path + "/" + file_name if path else file_name

        with open(path, mode='w') as file:
            def class2dict(instance):
                if isinstance(instance, list):
                    li = []
                    for i in instance:
                        if isinstance(i, str):
                            return instance
                        li.append(class2dict(i))
                    return li

                if not hasattr(instance, "__dict__"):
                    return instance

                new_subdic = vars(instance)
                for key, value in new_subdic.items():
                    new_subdic[key] = class2dict(value)
                return new_subdic

            class_dict = class2dict(self)
            class_dict['timestamp'] = str(datetime.datetime.now())
            file.write(json.dumps(class_dict))

    def is_solved(self) -> bool:
        return self.solution is not None


def solution_number(colors):
    count = 0
    for row in range(len(colors)):
        row_ = colors[row][0]
        if row_ != gui.WordleColor.EMPTY:
            count = count + 1
        else:
            break
    return count


@click.group()
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.option('--gui-pause', default=0.5, required=False)
@click.option('--typing-speed', default=0.5, required=False)
@click.pass_context
def cli(ctx, verbose, gui_pause, typing_speed):
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['gui_pause'] = gui_pause
    ctx.obj['typing_speed'] = typing_speed
    gui.PAUSE = gui_pause


@cli.command("click")
@click.argument("element")
@click.pass_context
def click_on(ctx, element):
    gui.click_on(element, ctx.obj["typing_speed"])


@cli.command("type")
@click.argument("word")
@click.pass_context
def type(ctx, word):
    gui.type(word, ctx.obj["typing_speed"])


@cli.command()
@click.option('-p', '--path', required=False, type=click.Path(exists=True))
def screenshot(path):
    if not path:
        gui.screenshot()
    else:
        gui.screenshot(True, path)


@cli.command()
@click.option('-p', '--path', type=click.Path(exists=True))
def preprocess_img(path):
    gui.preprocess_img(path)


@cli.command()
@click.argument("in_p", type=click.Path(exists=True))
@click.argument("out_p", type=click.Path(exists=False))
def crop_img(in_p, out_p):
    gui.crop_img(in_p, out_p)


@cli.command()
@click.argument("path", type=click.Path(exists=True), required=True)
@click.option('-psm', "--psm", default=6)
def read(path, psm):
    text = gui.read(path, psm)
    click.echo(text)


@cli.command()
@click.argument("path", type=click.Path(exists=True))
def get_colors(path):
    gui.get_colors(path)


@cli.command()
def phone_start():
    phone()


def wait(s: float, el: str):
    if el:
        click.echo(f"Wait {s} sec for {el}...")
    time.sleep(s)


@cli.command()
@click.argument("start_word")
@click.option("-o", "--open", is_flag=True, default=False)
@click.option("-c", "--count", default=1)
@click.pass_context
def start(ctx, start_word, open, count):
    if open:
        click.echo("Opening phone...")
        phone()
        wait(2, "phone")
        gui.click_on("app")
        wait(4, "app to start")
        gui.click_on("play")

    for i in range(count):
        put_solution(start_word)
        print(f"Play game {i + 1}/{count}")
        wordle_container = WordleContainer()
        wordle_container.word_list.append(start_word)
        play(wordle_container)
    print("Ended!")


@cli.command()
@click.option("-o", "--open", is_flag=True, default=False)
@click.option("-c", "--count", default=1)
@click.pass_context
def resume(ctx, open, count):
    if open:
        click.echo("Opening phone...")
        phone()
        wait(2, "phone")
    else:
        gui.move_to("submit")

    for i in range(count):
        print("Play game " + str(i))

        wordle_container = WordleContainer()
        play(wordle_container)
    print("Ended!")


def play(wordle_container: WordleContainer):
    session_path = "/home/florian/Pictures/wordles/" + str(datetime.datetime.now()).replace(" ", "_")
    os.mkdir(session_path)
    while not wordle_container.is_solved():
        current_text, current_colors = get_current_game_state(session_path)
        wordle_container.update(current_text, current_colors)
        if is_solved(current_colors):
            words = current_text.split()
            i = len(words) - 1
            print(f"Already solved with {words[i]}")
            wordle_container.set_solved(words[i], session_path)
            gui.click_on("next_word")
            wait(4, "next game to start")
            break

        words = wordle_container.find()
        next_solution = words[0]
        put_solution(next_solution)
        _, next_colors = get_current_game_state(session_path)

        if is_solved(next_colors):
            print(f"Solution was {next_solution}")
            wordle_container.set_solved(next_solution, session_path)
            gui.click_on("next_word")
            wait(4, "next game to start")
            break
        elif not was_legit_input(next_colors, current_colors):
            print(f"Word {next_solution} seems not to be wordle word, removing...")
            wh.remove_word(next_solution)
            [gui.click_on("delete", duration=0) for _ in range(5)]
        else:
            print(f"Word '{next_solution}' was not solution, starting next iteration...")
            wordle_container.word_list.append(next_solution)


def is_solved(colors: List[List[gui.WordleColor]]) -> bool:
    for color in colors:
        if all(solution == gui.WordleColor.OK for solution in color):
            return True


def was_legit_input(new_colors, old_colors):
    last_row_number = solution_number(old_colors)
    new_row_number = solution_number(new_colors)
    return last_row_number == new_row_number - 1


def put_solution(next_word):
    w = next_word.lower()
    print(f"Put word: {next_word}")
    gui.type(w[:1], echo=False)
    gui.type(w[1:], duration=.1, echo=False)
    gui.click_on("submit")


def get_current_game_state(data_path: str):
    again = True
    threshold = 5
    while again:
        print(f"Threshold {threshold}")
        _, path = gui.screenshot(path=data_path)
        try:
            colors = gui.get_colors(path)
        except gui.ColorStateException:
            """Solution is not yet done.."""
            os.remove(path)
            wait(.5, "for valid game state")
            continue
        processed_path = gui.preprocess_img(path, threshold=threshold)
        # os.remove(path) remove first screenshot
        text = gui.read(processed_path).lower()

        again = False
        text_split = text.split()
        for i, word in enumerate(text_split):
            if len(word) != 5:
                again = True
                break
            if not all([char in "abcdefghijklmnopqrstuvwxyzöäü" for char in word]):
                again = True

        if again:
            if 20 > threshold >= 5:
                threshold = threshold + 1
            elif threshold >= 20:
                threshold = 4
            elif 5 > threshold > 0:
                threshold = threshold - 1
            elif threshold < 1:
                raise Exception("Could not read words from screenshot")

    return text, colors


def phone():
    command = ["scrcpy", "--always-on-top", "--window-width", "470", "--window-height", "1015", "--window-x", "0",
               "--window-y", "0"]
    subprocess.Popen(command, shell=False,
                     stdin=None, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)


if __name__ == '__main__':
    cli()
