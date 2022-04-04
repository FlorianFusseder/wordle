import datetime
import json
import subprocess
import time
from collections.abc import Iterable
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

    def set_solved(self, solution):
        self.solution = solution

        with open("game_history.json", mode='r') as file:
            history = json.load(file)

        with open("game_history.json", mode='w') as file:
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
            history.append(class_dict)
            file.write(json.dumps(history))

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
@click.argument("path", type=click.Path(exists=True), required=True)
@click.option('-psm', "--psm", default=6)
def read(path, psm):
    text = gui.read(path, psm)
    click.echo(text)


@cli.command()
@click.option('-p', '--path', type=click.Path(exists=True))
def get_colors(path):
    gui.get_colors(path)


@cli.command()
def phone_start():
    phone()


def wait(s: int, el: str):
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
        wait(5, "app to start")
        gui.click_on("play")

    current_solution = start_word
    put_solution(current_solution)

    for i in range(count):
        print(f"Play game {i + 1}/{count}")
        wordle_container = WordleContainer()
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

    for i in range(count):
        print("Play game " + str(i))
        wordle_container = WordleContainer()
        play(wordle_container)
    print("Ended!")


def play(wordle_container: WordleContainer):
    while not wordle_container.is_solved():
        current_text, current_colors = get_current_game_state()
        wordle_container.update(current_text, current_colors)
        if is_solved(current_colors):
            words = current_text.split("\n")
            i = len(words) - 2
            print(f"Already solved with {words[i]}")
            wordle_container.set_solved(words[i])
            gui.click_on("next_word")
            wait(5, "next game to start")
            break

        words = wordle_container.find()
        next_solution = words[0]
        put_solution(next_solution)
        _, next_colors = get_current_game_state()

        if is_solved(next_colors):
            print(f"Solution was {next_solution}")
            wordle_container.set_solved(next_solution)
            gui.click_on("next_word")
            wait(4, "next game to start")
            break
        elif not was_legit_input(next_colors, current_colors):
            print(f"Word {next_solution} seems not to be wordle word, removing...")
            wh.remove_word(next_solution)
            [gui.click_on("delete") for _ in range(5)]


def is_solved(colors: List[List[gui.WordleColor]]) -> bool:
    for color in colors:
        if all(solution == gui.WordleColor.OK for solution in color):
            return True


def was_legit_input(new_colors, old_colors):
    last_row_number = solution_number(old_colors)
    new_row_number = solution_number(new_colors)
    return last_row_number == new_row_number - 1


def put_solution(next_word):
    gui.type(next_word.lower())
    gui.click_on("submit")
    wait(4, "app solution")


def get_current_game_state():
    _, path = gui.screenshot()
    colors = gui.get_colors(path)
    _, processed_path = gui.preprocess_img(path)
    text = gui.read(processed_path).lower()
    return text, colors


def phone():
    command = ["scrcpy", "--always-on-top", "--window-width", "470", "--window-height", "1015", "--window-x", "0",
               "--window-y", "0"]
    subprocess.Popen(command, shell=False,
                     stdin=None, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)


if __name__ == '__main__':
    cli()
