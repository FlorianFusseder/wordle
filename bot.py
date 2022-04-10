import datetime
import json
import os
import pickle
import re
import sys
import time
import typing
from typing import List, Callable

import click

import gui_helper as gui
import word_list as wt
import wordle


class WordleState:

    def __init__(self) -> None:
        self.regex = None
        self.word_glob = "." * 5
        self.char_contained_list = []
        self.char_not_contained = ""

    def add_solved(self, c, i):
        self.word_glob = self.word_glob[:i] + c + self.word_glob[i + 1:]

    def add_contained(self, c, contain_list: [int], not_list: [int], ignore_list: [int]):
        contained_word = ""
        for j in range(5):
            if j in not_list:
                contained_word += wordle.WordleRegex.not_character
            elif j in ignore_list:
                contained_word += wordle.WordleRegex.ignore_character
            elif j in contain_list:
                contained_word += c
            else:
                contained_word += wordle.WordleRegex.any_character

        self.char_contained_list.append(contained_word)

    def add_not_contained(self, c):
        self.char_not_contained = self.char_not_contained + c

    def add_regex(self, regex):
        self.regex = regex


class WordleContainer:

    def __init__(self, word_list: [str] = None, colors: [[gui.ColorCode]] = None) -> None:
        self.solution = None
        self.remaining = None
        self.states = []
        if word_list and colors:
            self.word_list = word_list[:-1]
            self.state = None
            self.update(word_list[len(word_list) - 1], colors)
        else:
            self.state = WordleState()
            self.word_list = []

    def update(self, new_word, colors):
        if self.state:
            self.states.append(self.state)
        self.state = WordleState()
        self.word_list.append(new_word.lower())

        for row, word in enumerate(self.word_list):
            color_row = colors[row]
            for column, char in enumerate(word):
                color_code = color_row[column]
                if color_code == gui.ColorCode.OK:
                    self.state.add_solved(char, column)
                elif color_code == gui.ColorCode.CONTAINED:
                    def get_index_list(color: gui.ColorCode):
                        return [match.start() for match in re.finditer(char, word) if color_row[match.start()] == color]

                    # make list where the containing character cannot occur
                    not_list = get_index_list(gui.ColorCode.NOT_CONTAINED)
                    # make list where the containing character is already occurring
                    ignore_list = get_index_list(gui.ColorCode.OK)
                    # make list how often the character occurs
                    character_occurrences_list = get_index_list(gui.ColorCode.CONTAINED)
                    self.state.add_contained(char, character_occurrences_list, not_list, ignore_list)
                elif color_code == gui.ColorCode.NOT_CONTAINED:
                    self.state.add_not_contained(char)
                elif color_code == gui.ColorCode.EMPTY:
                    break

    def find(self) -> List[str]:
        words, regex = wordle.find_words(self.state.word_glob, self.state.char_contained_list,
                                         self.state.char_not_contained,
                                         False)
        self.state.add_regex(regex)
        if not words:
            raise Exception("No Words could be found!")
        return words

    def set_solved(self, path: str = None):
        self.__game_solution(path, self.word_list[len(self.word_list) - 1], None)

    def set_unsolved(self, path: str = None):
        remaining = self.find()
        self.__game_solution(path, None, remaining)

    def __game_solution(self, path, solution: str, remaining: [str]):
        self.solution = solution
        self.remaining = remaining
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

    def set_not_legit(self):
        self.state = None


class GameMaster:

    def __init__(self, scoring_algorithm: wordle.Scoring,
                 start_word_manager: wt.StartWordManager,
                 interface: gui.Interface,
                 base_path: str,
                 games_to_play: int = 1) -> None:
        self._wordle_container: WordleContainer = None
        self._session_path: str = None
        self._current_solution_word: str = None
        self._scoring_algorithm: wordle.Scoring = scoring_algorithm
        self._start_word_manager: wt.StartWordManager = start_word_manager
        self._interface: gui.Interface = interface
        self._base_path: str = base_path
        self._games_to_play: int = games_to_play
        self._won: int = 0
        self._lost: int = 0
        self._attempts: int = 0

    def prepare_game(self):
        print(f"{'-' * 10}Play game {self.games_played() + 1}/{self._games_to_play}{'-' * 10}")
        self._session_path = self._base_path + "/" + f"{self.games_played() + 1}_{self._games_to_play}"
        os.makedirs(self._session_path)

        while True:
            try:
                colors = self._interface.get_colors(5, False)
                break
            except gui.ColorStateException:
                self.wait(.2)

        if colors[0][0] != gui.ColorCode.EMPTY:
            print("Game seems to have started already!")
            self._attempts = len([color[0] for color in colors if color[0] != gui.ColorCode.EMPTY])
            while True:
                input_ = input(f"Input words (space seperated) for {self._attempts} filled rows:")
                words = input_.lower().split()
                if len(words) != self._attempts:
                    print("Input to few words, again...")
                else:
                    break
            self._wordle_container = WordleContainer(words, colors)
            self._start_word_manager.start_word = words[0]
            self._current_solution_word = self._wordle_container.find()[0]
        else:
            self._wordle_container: WordleContainer = WordleContainer()
            self._current_solution_word = self._start_word_manager.start_word
        self._interface.move_to("submit")

    def play_game(self):

        def all_current_row(predicate: Callable[[gui.ColorCode], bool]):
            return all([predicate(code) for code in current_colors[self._attempts]])

        while not self._wordle_container.is_solved() and self._attempts < 6:
            self._interface.put_solution(self._current_solution_word)
            self.wait(1, "animation to start")

            retries = 10 if self._attempts > 5 else 20
            waiting_duration = .2 if self._attempts > 5 else .5
            for try_ in range(retries):
                try:
                    current_colors = self._interface.get_colors(self._attempts)
                    break
                except gui.ColorStateException as e:
                    self.wait(waiting_duration, "valid game state")
                    if try_ == retries - 1:
                        print("Could not get valid game state, exiting...")
                        raise e

            if not all_current_row(lambda code: code != gui.ColorCode.EMPTY):
                print(f"Word {self._current_solution_word} seems not to be wordle word, removing...")
                wt.remove_word(self._current_solution_word)
                if self._attempts == 0:
                    raise Exception(f"Your start word {self._current_solution_word} is not in wordlist!")
                print("Delete word...")
                [self._interface.click_on("delete", duration=0, echo=False) for _ in range(5)]
                self._current_solution_word = self._wordle_container.find()[0]
                continue

            self._wordle_container.update(self._current_solution_word, current_colors)

            if all_current_row(lambda code: code == gui.ColorCode.OK):
                self._wordle_container.set_solved(self._session_path)
            else:
                print(f"Word '{self._current_solution_word}' was not solution, "
                      f"starting iteration {self._attempts + 1}/6...")
                words = self._wordle_container.find()
                self._current_solution_word = self._scoring_algorithm.evaluate(words)[0]
            self._attempts += 1

    def end_game(self):
        self._interface.wait_for_endscreen()
        self._interface.make_endscreen_screenshot(self._session_path)
        new_path = self._session_path + f"_{self._attempts}_"
        if self._wordle_container.is_solved():
            print(f"Solution was {self._current_solution_word}")
            self._won += 1
            new_path += self._current_solution_word
            with open("whitelist.txt", mode="r+") as file:
                word_set = set(file.read().split())
                l_b = len(word_set)
                word_set.add(self._current_solution_word)
                l_a = len(word_set)
                if l_b < l_a:
                    file.write(self._current_solution_word + "\n")
        else:
            print("Could not solve wordle puzzle")
            self._lost += 1
            new_path += "UNSOLVED"
            self._wordle_container.set_unsolved(self._session_path)

        self._start_word_manager.update_statistics(self._wordle_container.is_solved(), self._attempts)
        self._attempts = 0
        self._interface.click_on("next_word")
        os.rename(self._session_path, new_path)

    def games_played(self) -> int:
        return self._won + self._lost

    def keep_playing(self) -> bool:
        return self.games_played() < self._games_to_play

    @staticmethod
    def wait(s: float, echo: str = None):
        if echo:
            click.echo(f"Wait {s} sec for {echo}...")
        time.sleep(s)


models = os.listdir("interfaces")


@click.group()
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.option('--gui-pause', default=0.5, required=False)
@click.option('--typing-speed', default=0.5, required=False)
@click.option("-i", "--interface", type=click.Choice(models, case_sensitive=False))
@click.option("-o", "--open-interface", is_flag=True, default=False)
@click.option("-f", "--force-open-interface", is_flag=True, default=False)
@click.pass_context
def cli(ctx, verbose, gui_pause, typing_speed, interface, open_interface, force_open_interface):
    ctx.ensure_object(dict)

    if interface:
        with open(f"interfaces/{interface}", mode="rb") as unpickle:
            ctx.obj['interface'] = pickle.load(unpickle)
            if open_interface and ctx.obj['interface'].commands:
                try:
                    ctx.obj['interface'].get_colors(5, False)
                    if force_open_interface:
                        ctx.obj['interface'].open_()
                    else:
                        print("Skip opening, as it seems already to be open")
                except (gui.ColorStateException, gui.MultipleColorMatches):
                    ctx.obj['interface'].open_()

    ctx.obj['verbose'] = verbose
    ctx.obj['gui_pause'] = gui_pause
    ctx.obj['typing_speed'] = typing_speed
    gui.PAUSE = gui_pause


@cli.command("click")
@click.argument("element")
@click.pass_context
def click_on(ctx, element):
    ctx.obj['interface'].click_on(element)


@cli.command("type")
@click.argument("word")
@click.option("-c", "--count", default=1)
@click.pass_context
def type(ctx, word, count):
    ctx.obj['interface'].move_to("submit", 1)
    for _ in range(count):
        ctx.obj['interface'].put_solution(word)


@cli.command()
@click.argument('element')
def get_pixel_color(ctx, element):
    by_element = ctx.obj['interface'].get_pixel_color_by_element(element)
    print(f"R[{by_element[0]}]G[{by_element[1]}]B[{by_element[2]}]")


@cli.command()
@click.option('-p', '--path', required=False, type=click.Path(exists=True))
def screenshot(path):
    if not path:
        gui.screenshot()
    else:
        gui.screenshot(with_datetime=True, path=path)


@cli.command()
@click.argument('path', type=click.Path(exists=True))
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
def scr_read():
    gui.scr_read()


@cli.command()
@click.option("-c", "--column", type=int)
@click.option("-r", "--row", type=int)
@click.option("-e", "--element", type=str)
@click.pass_context
def get_color(ctx, column, row, element):
    interface_: gui.Interface = ctx.obj['interface']
    if column or row:
        position = interface_.color_positions[column][row]
    elif element:
        position = interface_.elements[element]
    else:
        position = gui.mouse_position()
    colors = interface_.get_pixel_color_by_position(position)
    gui.move_to(position[0], position[1])
    print(f"Position: {position}, Color {colors}")
    [print(k.name + ":" + (" " * (15 - len(k.name))) + str(v)) for k, v in interface_.color_codes.items()]


@cli.command()
@click.pass_context
def get_colors(ctx):
    colors = ctx.obj['interface'].get_colors(5, False)
    gui.Interface.print_matrix(colors)


@cli.command()
@click.pass_context
def start_interface(ctx):
    ctx.obj['interface'].open_()


@cli.command("interface")
@click.pass_context
def new_interface(ctx):
    interface: gui.Interface = ctx.obj['interface'] if 'interface' in ctx.obj else gui.Interface()

    def update(id_: str) -> bool:
        if 'interface' in ctx.obj:
            return input(f"Do you want to update {id_}? (y/n): ") == "y"

    try:
        if not interface.identifier or update("id"):
            interface.identifier = input("Id: ")

        if not interface.commands or update('Start Commands'):
            interface.commands = input("Start Command: ")

        x_p: [int] = [0] * 5
        y_p: [int] = [0] * 6

        def define_positions(p_list, name, skip: bool = False):
            for i in range(len(p_list)):
                if skip and i == 0:
                    continue
                input(f"Hover {name}{i + 1} and press enter")
                p_list[i] = gui.mouse_position()
            return p_list

        if not interface.color_positions or update('Color Positions'):
            matrix: [[typing.Tuple]] = []
            for _ in range(6):
                matrix.append([()] * 5)

            x_p = define_positions(x_p, 'x')
            y_p = define_positions(y_p, 'y', True)
            y_p[0] = x_p[0]
            for i, y in enumerate(y_p):
                for j, x in enumerate(x_p):
                    matrix[i][j] = (x[0], y[1])

            interface.color_positions = matrix

        to_update = update("an Element")

        def define_element(k: str):
            input(f"Hover {k} and press enter ")
            interface.elements[k] = gui.mouse_position()
            if k == "next_word":
                interface.next_word_rgb = gui.Interface.get_pixel_color_by_position(interface.elements[k])

        if not to_update:
            for k, v in interface.elements.items():
                if v[0] == -1 and v[1] == -1:
                    define_element(k)
        else:
            element_name = input("Input element name: ")
            define_element(element_name)

        if update("Color codes"):
            for k, v in interface.color_codes.items():
                if v == gui.RGB():
                    input(f"Hover {k.name} and press enter")
                    pos = gui.mouse_position()
                    interface.color_codes[k] = gui.Interface.get_pixel_color_by_position(pos)

        if update("endscreen"):
            input("Hover over the left top corner of your desired endscreen and press enter")
            left, top = gui.mouse_position()
            input("Hover over the right bottom corner of your desired endscreen and press enter")
            bottom, right = gui.mouse_position()
            interface.endscreen_window = (left, top, right - left, bottom - top)

    except Exception as e:
        print(f"{e}")

    if interface.identifier:
        print(f"Save {interface}")
        with open(f"interfaces/{interface.identifier}", mode="wb") as pickle_file:
            pickle.dump(interface, pickle_file)


@cli.command("play")
@click.option("-w", "--start_word")
@click.option("-c", "--count", default=1, type=click.IntRange(1, sys.maxsize))
@click.pass_context
def start(ctx, start_word, count):
    interface: gui.Interface = ctx.obj["interface"]
    base_path = "/home/florian/Pictures/wordles/" + str(datetime.datetime.now()).replace(" ", "_")
    start_word_manager = wt.StartWordManager(start_word) if start_word else wt.StartWordManager()
    scoring_algorithm: wordle.Scoring = wordle.SimpleScoring()

    game_master = GameMaster(scoring_algorithm, start_word_manager, interface, base_path, count)
    while game_master.keep_playing():
        game_master.prepare_game()
        game_master.play_game()
        game_master.end_game()


if __name__ == '__main__':
    cli()
