import re
from abc import ABC, abstractmethod

import click


class Char(ABC):
    def __init__(self, character):
        self.character = character
        self.regex = character

    def get_regex(self) -> str:
        return self.regex

    @abstractmethod
    def add_excludes(self, excludes: str):
        pass

    def __str__(self) -> str:
        return f"Regex: {self.regex}, Character: {self.character}"


class FixedChar(Char):

    def __init__(self, character):
        super().__init__(character)

    def add_excludes(self, excludes):
        pass


class AnyChar(Char):

    def __init__(self):
        super().__init__(".")
        self.exclude_list: [str] = []

    def add_excludes(self, excludes: str):
        for c in excludes:
            self.exclude_list.append(c)

    def get_regex(self) -> str:
        return "[^" + "".join(self.exclude_list) + "]" if self.exclude_list else self.regex


class WordleRegex:
    def __init__(self, word, contains, excludes, verbose):
        click.echo(f"Passed word: {word}")
        click.echo(f"Contained: {contains}")
        click.echo(f"Not Contained: {excludes}")
        if verbose:
            click.echo("Output is verbose")

        assert len(word) == 5, "Your word length seems to be not equal to 5"
        if contains:
            assert [len(w) == 5 for w in contains], "One or more of your contains words seems to be not equal to 5"

        self.verbose = verbose
        self.excludes = excludes
        self.contains = contains if contains else []
        self.regex_elements: [Char] = []
        self.regex_lookaheads: [str] = set()
        for character in word:
            if character == ".":
                self.regex_elements.append(AnyChar())
            else:
                self.regex_elements.append(FixedChar(character))

    def _get_regex(self):
        return ''.join([regex.get_regex() for regex in self.regex_elements])

    def _add_excludes(self):
        if self.excludes:
            for regex_element in self.regex_elements:
                regex_element.add_excludes(self.excludes)

    def _add_contains(self):
        for contains in self.contains:
            for i, contain in enumerate(contains):
                if contain != ".":
                    self.regex_elements[i].add_excludes(contain)
                    self._create_lookahead(contain)

    def _add_anchors(self) -> str:
        return rf"^{self._get_regex()}$"

    def _echo(self, message):
        if self.verbose:
            click.echo(message)

    def create(self) -> str:
        self._echo(f"Starting regex: {self._get_regex()}")
        self._add_excludes()
        self._echo(f"Regex with excludes: {self._get_regex()}")
        self._add_contains()
        self._echo(f"Regex with contains: {self._get_regex()}")
        anchored_regex = self._add_anchors()
        self._echo(f"Anchored Regex: {anchored_regex}")
        final_regex = self._add_lookahead(anchored_regex)
        click.echo(f"Final regex: {final_regex}")
        return final_regex

    def _create_lookahead(self, contain):
        self.regex_lookaheads.add(f"(?=.*{contain}+.*)")

    def _add_lookahead(self, regex) -> str:
        for regex_lookahead in self.regex_lookaheads:
            regex = regex_lookahead + regex
        return regex


def sort_word(word):
    with open("statistics.json") as file:
        import json
        statistics = json.load(file)

    score = 0
    for char in word:
        score = score + statistics[char.lower()]

    s = set(word)

    for _ in range(len(word) - len(s)):
        score = score / 2

    return score


@click.command()
@click.argument('word')
@click.option('--contains', '-c', required=False, multiple=True)
@click.option('--exclude', '-x')
@click.option('--verbose', '-v', is_flag=True)
def find(word, contains, exclude, verbose):
    find_words(word, contains, exclude, verbose)


def find_words(word, contains, exclude, verbose):
    with open("5long.txt", "r") as file:
        all_words = file.read()
    regex_builder: WordleRegex = WordleRegex(word, contains, exclude, verbose)
    regex = regex_builder.create()
    matches = re.findall(regex, all_words, re.IGNORECASE | re.MULTILINE)
    click.echo(f"Found {len(matches)} words that match the passed structure...")
    matches.sort(reverse=True, key=sort_word)
    click.echo(f"{matches}")


if __name__ == '__main__':
    find()
