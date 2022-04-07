import datetime
import json
import os
import sys
import time
import typing
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

        for i in range(number):
            for j in range(0, 5):
                c = text[j]
                color_code = colors[i][j]

                if color_code == gui.ColorCode.OK:
                    self.state.add_solved(c, j)
                elif color_code == gui.ColorCode.CONTAINED:
                    self.state.add_contained(c, j)
                elif color_code == gui.ColorCode.NOT_CONTAINED:
                    self.state.add_not_contained(c)
                elif color_code == gui.ColorCode.EMPTY:
                    break
            text = text[6:]

    def find(self) -> List[str]:
        words = wordle.find_words(self.state.word_glob, self.state.char_contained_list, self.state.char_not_contained,
                                  False)
        if not words:
            raise Exception("No Words could be found!")
        return words

    def set_solved(self, solution: str = None, path=None):
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
        if row_ != gui.ColorCode.EMPTY:
            is_complete = all([column != gui.ColorCode.EMPTY for column in colors[row]])
            if not is_complete:
                raise gui.ColorStateException("Not all Colors seem to be solved just yet")
            count = count + 1
        else:
            break
    return count


models = ['PSMART2019', 'P30']


@click.group()
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.option('--gui-pause', default=0.5, required=False)
@click.option('--typing-speed', default=0.5, required=False)
@click.option("-m", "--model",
              type=click.Choice(models, case_sensitive=False), default=models[0])
@click.pass_context
def cli(ctx, verbose, gui_pause, typing_speed, model):
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['gui_pause'] = gui_pause
    ctx.obj['typing_speed'] = typing_speed
    ctx.obj['model'] = model
    ctx.obj['phone'] = gui.Phone.init_device(model)
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
@click.argument("path", type=click.Path(exists=True))
@click.pass_context
def get_colors(ctx, path):
    gui.get_colors(path)


@cli.command()
@click.pass_context
def phone_start(ctx):
    start_phone(ctx.obj['phone'])


def wait(s: float, el: str = None):
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
        start_phone(ctx.obj['phone'])
        wait(2, "phone")
        gui.click_on("play")

    session_string = "/home/florian/Pictures/wordles/" + str(datetime.datetime.now()).replace(" ", "_")
    not_solved = []
    for i in range(count):
        print(f"{'-' * 10}Play game {i + 1}/{count}{'-' * 10}")
        put_solution(start_word)
        wordle_container = WordleContainer()
        wordle_container.word_list.append(start_word)
        solved = play(wordle_container, session_string, "/" + f"{i + 1}_{count}")
        if not solved:
            not_solved.append(i)

    __print_game_solution(not_solved)


def __print_game_solution(not_solved):
    if not_solved:
        print(
            f"Game{'s' if len(not_solved) != 1 else ''} {', '.join([str(i) for i in not_solved])} could not be solved!")
    else:
        print("Could solve all words! Ending...")


@cli.command()
@click.option("-o", "--open", is_flag=True, default=False)
@click.option("-c", "--count", default=1, type=click.IntRange(1, sys.maxsize))
@click.option("-w", "--start_word")
@click.pass_context
def resume(ctx, open, count, start_word):
    if count > 1 and not start_word:
        raise click.BadParameter(
            "If 'count' option is used, you have to define a start_word with '-w' (e.g. '-w stier')",
            start_word)

    if open:
        click.echo("Opening phone...")
        start_phone(ctx.obj['phone'])
        wait(2, "phone")

    gui.move_to("submit")

    session_string = "/home/florian/Pictures/wordles/" + str(datetime.datetime.now()).replace(" ", "_")
    not_solved = []
    for i in range(count):
        print(f"{'-' * 10}Play game {i + 1}/{count}{'-' * 10}")
        wordle_container = WordleContainer()
        if i == 0:
            word_list = gui.scr_read()
            wordle_container.word_list.extend([w.lower() for w in word_list.split()])
        else:
            put_solution(start_word)
            wordle_container.word_list.append(start_word)

        solved = play(wordle_container, session_string, "/" + f"{i + 1}_{count}")
        if not solved:
            not_solved.append(i)

    __print_game_solution(not_solved)


def play(wordle_container: WordleContainer, session_path, game_identifier):
    ident_path = session_path + game_identifier
    os.makedirs(ident_path)
    tries = 0
    while not wordle_container.is_solved() and tries < 6:
        current_text, current_colors, _ = get_current_game_state(ident_path)
        wordle_container.update(current_text, current_colors)
        if is_solved(current_colors):
            words = current_text.split()
            i = len(words) - 1
            print(f"Already solved with {words[i]}")
            wordle_container.set_solved(words[i], ident_path)
            gui.click_on("next_word")
            wait_for_game_start()
            break

        words = wordle_container.find()
        next_solution = words[0]
        put_solution(next_solution)
        wait(1, "animation to start")
        all_words, next_colors, tries = get_current_game_state(ident_path)

        for w in all_words.split():
            w = w.lower()
            if w not in [wc.lower() for wc in wordle_container.word_list] and w != next_solution.lower():
                raise Exception(f"""Inconsistent game state: 
                words read from picture: {', '.join(all_words.split())}
                words that have been typed until now: {wordle_container.word_list}
                solution for this iteration: {next_solution}""")

        if is_solved(next_colors):
            print(f"Solution was {next_solution}")
            wordle_container.set_solved(next_solution, ident_path)
            gui.screenshot((0, 65, 470, 990), False, ident_path, "endscreen.png")
            gui.click_on("next_word")
            os.rename(ident_path, ident_path + f"_{tries + 1}_{next_solution}")
            wait_for_game_start()
            return True
        elif not was_legit_input(next_colors, current_colors):
            print(f"Word {next_solution} seems not to be wordle word, removing...")
            wh.remove_word(next_solution)
            print("Delete word...")
            [gui.click_on("delete", duration=0, echo=False) for _ in range(5)]
            _, _, tries = get_current_game_state(ident_path)
        else:
            if tries < 6:
                print(f"Word '{next_solution}' was not solution, starting iteration {tries + 1}/6...")
            wordle_container.word_list.append(next_solution)

    if tries >= 6:
        wait_for_game_solution()
        renamed_path = ident_path + f"_{tries + 1}_UNSOLVED"
        os.rename(ident_path, renamed_path)
        wordle_container.set_solved(None, renamed_path)
        print("Could not solve...")
        wait(3, "endscreen solution")
        gui.screenshot((0, 65, 470, 990), False, renamed_path, "endscreen.png")
        gui.click_on("next_word")
        wait_for_game_start()
        return False


def wait_for_game_start():
    while not check_game_state(lambda state: gui.ColorCode.EMPTY == state):
        wait(.5, "game start")


def wait_for_game_solution():
    while not check_game_state(lambda state: gui.ColorCode.EMPTY != state):
        wait(1, "game solution")


def is_solved(colors: List[List[gui.ColorCode]]) -> bool:
    for color in colors:
        if all(solution == gui.ColorCode.OK for solution in color):
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


def check_game_state(fn: typing.Callable[[gui.ColorCode], bool]):
    """Executes the lambda on all states, and returns true if ALL of them return true"""
    while True:
        _, path = gui.screenshot()
        try:
            colors = gui.get_colors(path)
            all_match = all([fn(state) for state in colors[0]])
            os.remove(path)
            return all_match
        except gui.ColorStateException as e:
            os.remove(path)
            wait(.5, f"valid game state because '{e}'")
            continue


def get_current_game_state(data_path: str):
    again = True
    threshold = 5
    number: int
    if data_path:
        while again:
            _, path = gui.screenshot(path=data_path)
            try:
                colors = gui.get_colors(path)
                number = solution_number(colors)
                if number == 0:
                    raise gui.ColorStateException("Cannot get state if no rows are solved yet...")

            except gui.ColorStateException as e:
                """Solution is not yet done.."""
                os.remove(path)
                wait(1, f"valid game state because '{e}'")
                continue

            processed_path = gui.preprocess_img(path, threshold=threshold)
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
    return text, colors, number


def start_phone(phone: gui.Phone):
    phone.start()


if __name__ == '__main__':
    cli()
