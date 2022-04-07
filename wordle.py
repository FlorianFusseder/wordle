import re
from abc import ABC, abstractmethod
from typing import Set, Dict

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
        self.exclude_list: Set[str] = set()

    def add_excludes(self, excludes: str):
        for c in excludes:
            self.exclude_list.add(c)

    def get_regex(self) -> str:
        return "[^" + "".join(self.exclude_list) + "]" if self.exclude_list else self.regex


class WordleRegex:
    allowed_characters = "abcdefghijklmnopqrstuvwxyzöäü"
    any_character = "."
    # The 'ignore_character' can be used for the '-c' keyword to mark, that this position already contains the character
    # but there has to be another one, e.g. -c a..!.  which means there has to be an 'a' on one of the indexes, 1, 2, 4
    # there cannot be 'a' on 0 and the 'a' on index 3 has to be ignored. There are basically two 'a' in this word
    ignore_character = "!"
    # The 'not_character'  can be used for the '-c' keyword to mark, that the contained character is not at this index
    # e.g. -c a..^. the a character can only be at indexes 1, 2, 4
    not_character = "^"

    def get_word(self) -> [str]:
        return "".join([elem.character for elem in self.regex_elements])

    def __init__(self, word, contains, excludes, verbose):
        click.echo(f"Passed glob: {word}")
        click.echo(f"Contained: {contains}")
        click.echo(f"Not Contained: {excludes}")
        if verbose:
            click.echo("Output is verbose")

        assert len(word) == 5, "Your word length seems to be not equal to 5"
        if contains:
            assert [len(w) == 5 for w in contains], "One or more of your contains words seems to be not equal to 5"

        self.verbose = verbose
        self.excludes: str = excludes
        self.contains: [str] = contains if contains else []
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
            character = self._create_lookahead(contains)
            for i, contain in enumerate(contains):
                if contain == character or contain == self.not_character:
                    self.regex_elements[i].add_excludes(character)

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

    def _create_lookahead(self, term: str) -> str:
        """
        :param term: search term
        :return: the search char
        """
        ignore_character_count = term.count(self.ignore_character)
        not_character_count = term.count(self.not_character)
        character = term \
            .replace(self.any_character, "") \
            .replace(self.ignore_character, "") \
            .replace(self.not_character, "")

        if not ignore_character_count and not not_character_count:
            reg = f"(?:.*{character})+"
        elif ignore_character_count and not not_character_count:
            reg = f"(?:{'.*' + character}){{{ignore_character_count + 1},}}"
        elif not ignore_character_count and not_character_count:
            reg = f"(?:.*{character})"
        else:
            reg = f"(?:{'.*' + character}){{{ignore_character_count + 1}}}"

        self.regex_lookaheads.add(f"(?={reg})")
        return character

    def _add_lookahead(self, regex) -> str:
        for regex_lookahead in self.regex_lookaheads:
            regex = regex_lookahead + regex
        return regex


class ArenaWordleRegex(WordleRegex):
    """
    This Class creates a regex that will check an try to solve the ARENA problem
    where double Characters (like the a) are marked as 'contained' for the first character a (A)RENA but the last
    a AREN(A) is marked as 'not_contained'. If this happens, we do not use a for exclusion
    :return:
    """

    def _add_excludes(self):
        dont_remove = set()
        if self.excludes:
            for c in self.excludes:
                for contained in self.contains:
                    if c in contained:
                        dont_remove.add(c)

            for remove in dont_remove:
                self.excludes = self.excludes.replace(remove, "")

            for regex_element in self.regex_elements:
                regex_element.add_excludes(self.excludes)


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

    if not matches:
        print("Try arena problem solution... PRAY TO THE ALMIGHTY")
        wordle_regex = ArenaWordleRegex(word, contains, exclude, verbose)
        regex = wordle_regex.create()
        matches = re.findall(regex, all_words, re.IGNORECASE | re.MULTILINE)

    click.echo(f"Found {len(matches)} words that match the passed structure...")
    matches.sort(reverse=True, key=sort_word)
    click.echo(f"{matches}")
    return matches, regex


if __name__ == '__main__':
    find()
