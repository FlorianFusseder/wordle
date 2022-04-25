import re
from abc import ABC, abstractmethod
from collections import defaultdict
from enum import Enum
from typing import Set, List, Dict, Tuple, Optional

import click


class ImmutableElementException(Exception):
    def __init__(self, elem):
        super.__init__(elem)


class InfoCoding(Enum):
    CORRECT = 't'
    NOT_CONTAINED = 'f'
    CONTAINED = 'c'


InfoCoding.dict = {
    InfoCoding.CORRECT.value: InfoCoding.CORRECT,
    'f': InfoCoding.NOT_CONTAINED,
    'c': InfoCoding.CONTAINED
}


class Char(ABC):

    @property
    def index(self):
        return self.__index

    @property
    def character(self):
        return self.__character

    @property
    def regex(self):
        return self.__regex

    def __init__(self, index, character, other_occurrences: Dict[InfoCoding, List[int]] = None):
        self.__index = index
        self.__character = character
        self.__regex = character
        self._other_occurrences = other_occurrences

    @abstractmethod
    def add_self_to_regex(self, builder: 'WordleRegexBuilder') -> None:
        pass

    @abstractmethod
    def add_excludes(self, excludes: str):
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(Index: {self.index} Character: {self.character})"

    def __repr__(self):
        return self.__str__()


class SolvedChar(Char):

    def add_self_to_regex(self, builder: 'WordleRegexBuilder') -> None:
        if builder.elements[self.index]:
            raise ImmutableElementException
        builder.elements[self.index] = self.character

    def __init__(self, index: int, character: str):
        super().__init__(index, character)

    def add_excludes(self, excludes):
        pass


class ContainedChar(Char):

    def add_self_to_regex(self, builder: 'WordleRegexBuilder') -> None:
        builder.excludes[self.index].add(self.character)

        count: int = 1
        or_more = InfoCoding.NOT_CONTAINED not in self._other_occurrences  # if NOT_CONTAINED exists -> we got exact count

        if InfoCoding.CONTAINED in self._other_occurrences:
            count += len(self._other_occurrences[InfoCoding.CONTAINED])
        if InfoCoding.CORRECT in self._other_occurrences:
            count += len(self._other_occurrences[InfoCoding.CORRECT])

        occurrence_multiplier_new = Multiplier(count, or_more)
        if self.character in builder.lookaheads:
            occurrence_multiplier_old = builder.lookaheads[self.character]
            if occurrence_multiplier_old.count < occurrence_multiplier_new.count or \
                    occurrence_multiplier_old.or_more and not occurrence_multiplier_new.or_more:
                builder.lookaheads[self.character] = occurrence_multiplier_new
        else:
            builder.lookaheads[self.character] = occurrence_multiplier_new

    def __init__(self, index, character, other_occurrences):
        super().__init__(index, character, other_occurrences)

    def add_excludes(self, excludes: str):
        pass


class NotContainedChar(Char):

    def add_self_to_regex(self, builder: 'WordleRegexBuilder') -> None:
        if InfoCoding.CONTAINED in self._other_occurrences:
            builder.excludes[self.index].add(self.character)
        else:
            [excludes.add(self.character) for excludes in builder.excludes]

    def __init__(self, index: int, character: str, other_occurrences):
        super().__init__(index, character, other_occurrences)

    def add_excludes(self, excludes: str):
        pass


class AnyChar(Char):

    def add_self_to_regex(self, builder: 'WordleRegexBuilder') -> None:
        pass

    @property
    def regex(self):
        return "[^" + "".join(self.exclude_list) + "]" if self.exclude_list else self.__regex

    def __init__(self, index):
        super().__init__(index, ".")
        self.exclude_list: Set[str] = set()

    def add_excludes(self, excludes: str):
        for c in excludes:
            self.exclude_list.add(c)


class Word:

    def __init__(self, word: str, info: str) -> None:
        self.character_list: List[Char] = [None] * 5
        self._character_dict: Dict[str, List[int]] = defaultdict(list)
        [self._character_dict[char].append(i) for i, char in enumerate(word)]

        index_list: List[int]
        for char, index_list in self._character_dict.items():
            for i in index_list:
                def other_indexes() -> Dict[InfoCoding, List[int]]:
                    dict_ = defaultdict(list)
                    [dict_[InfoCoding.dict[info[index]]].append(index) for index in index_list if index != i]
                    return dict_

                char_obj: Char
                info_code: InfoCoding = InfoCoding.dict[info[i]]
                if info_code == InfoCoding.CORRECT:
                    char_obj = SolvedChar(i, char)
                elif info_code == InfoCoding.NOT_CONTAINED:
                    char_obj = NotContainedChar(i, char, other_indexes())
                elif info_code == InfoCoding.CONTAINED:
                    char_obj = ContainedChar(i, char, other_indexes())
                else:
                    raise KeyError(f"'{info[i]}' is not a valid 'WordInfo' character")
                self.character_list[i] = char_obj

    def __len__(self):
        return len(self.character_list)

    def __getitem__(self, item):
        return self.character_list[item]

    def __iter__(self):
        class WordIterator:
            def __init__(self, word: Word) -> None:
                self.__index: int = 0
                self.__word: Word = word

            def __next__(self) -> Char:
                char: Char
                if len(self.__word) > self.__index >= 0:
                    char = self.__word[self.__index]
                    self.__index += 1
                    return char
                elif len(self.__word) <= self.__index:
                    raise StopIteration
                else:
                    raise IndexError

        return WordIterator(self)

    def __repr__(self) -> str:
        return ", ".join([char.__repr__() for char in self.character_list])

    def process(self, builder: 'WordleRegexBuilder'):
        for char in self:
            char.add_self_to_regex(builder)


class WordleRegexBuilder(ABC):

    @property
    def elements(self):
        return self._regex_word_elements

    @property
    def lookaheads(self):
        return self._regex_lookahead_elements

    @property
    def excludes(self):
        return self._regex_excluded_elements

    def __init__(self) -> None:
        self._regex_word_elements = [None] * 5
        self._regex_excluded_elements: List[Set[str]] = [set() for _ in range(5)]
        self._regex_lookahead_elements = {str: Multiplier}

    @abstractmethod
    def create(self) -> str:
        pass


class Multiplier:

    @property
    def count(self):
        return self.__count

    @property
    def or_more(self):
        return self.__or_more

    def __init__(self, count: int, or_more: bool):
        self.__count = count
        self.__or_more = or_more

    def to_regex_string(self):
        return None


class ColorInfoWordleRegex(WordleRegexBuilder):

    def __init__(self, attempts) -> None:
        super().__init__()
        self.__attempts: [Word] = [Word(word, info) for word, info in [attempt for attempt in attempts]]

    def create(self) -> str:
        __attempt: Word
        for __attempt in self.__attempts:
            __attempt.process(self)
        return ""


class GlobWordleRegex(WordleRegexBuilder):
    allowed_characters = "abcdefghijklmnopqrstuvwxyzöäü"
    any_character = "."
    # The 'ignore_character' can be used for the '-c' keyword to mark, that this position already contains the character
    # but there has to be another one, e.g. -c a..!.  which means there has to be an 'a' on one of the indexes, 1, 2, 4
    # there cannot be 'a' on 0 and the 'a' on index 3 has to be ignored. There are basically two 'a' in this word
    ignore_character = "!"
    # The 'not_character'  can be used for the '-c' keyword to mark, that the contained character is not at this index
    # e.g. -c a..^. the a character can only be at indexes 1, 2, 4
    not_character = "^"

    def __init__(self, word, contains, excludes, verbose):
        super().__init__()
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
        for i, character in enumerate(word):
            if character == ".":
                self.regex_elements.append(AnyChar(i))
            else:
                self.regex_elements.append(SolvedChar(i, character))

    def _get_regex(self):
        return ''.join([regex_.regex for regex_ in self.regex_elements])

    def _add_excludes(self):
        if self.excludes:

            # check if any of the excludes is in contained -> then we have to remove it from general excludes
            remove = [char for char in self.excludes if
                      any([char in contained_glob for contained_glob in self.contains])]
            for char_to_remove in remove:
                self.excludes = self.excludes.replace(char_to_remove, "")

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
            .replace(self.not_character, "")[0]  # take only one

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

    def _add_lookahead(self, regex_) -> str:
        for regex_lookahead in self.regex_lookaheads:
            regex_ = regex_lookahead + regex_
        return regex_


class Scoring(ABC):

    def __init__(self, name: str) -> None:
        self._name = name

    @abstractmethod
    def evaluate(self, word_list: [str]) -> [str]:
        print(f"Using {self._name} Algorithm...")
        return word_list

    def __str__(self) -> str:
        return self._name


class SimpleScoring(Scoring):

    def __init__(self) -> None:
        super().__init__("SimpleScoring")

    def evaluate(self, word_list: [str]) -> [str]:
        super().evaluate(word_list)

        def sort_word(word):
            with open("statistics.json") as file:
                import json
                statistics = json.load(file)

            s_dict = {}
            for i, k in enumerate(sorted(statistics.items(), key=lambda x: x[1])):
                s_dict[k[0]] = i + 1

            score = 0
            for char in word.lower():
                score += s_dict[char]

            s = set(word)
            for _ in range(len(word) - len(s)):
                score -= 5

            with open("whitelist.txt") as file:
                all_solution_words = file.read()

            if word in all_solution_words:
                score += 29
            return score

        word_list.sort(reverse=True, key=sort_word)
        return word_list


@click.group()
def wordle():
    pass


@wordle.command("solve")
@click.argument('word')
@click.option('--contains', '-c', required=False, multiple=True)
@click.option('--exclude', '-x')
@click.option('--verbose', '-v', is_flag=True)
def find(word, contains, exclude, verbose):
    find_words(word, contains, exclude, verbose)


def check_solution(ctx, param, value):
    if len(value) % 2 != 0:
        click.BadArgumentUsage("has always to be word and word-information", ctx)

    for i in range(0, int(len(value) / 2), 2):
        word: str = value[i]
        info: str = value[i + 1]
        if len(info) != 5 or len(word) != 5:
            click.BadArgumentUsage("Length of info and word has to be 5")
        info_ = info.replace("t", "").replace("f", "").replace("c", "")
        if len(info_) != 0:
            print("Word info contains unrecognized charakter(s): " + info_)
    return [(value[i], value[i + 1]) for i in range(0, int(len(value) / 2), 2)]


@wordle.command("solve")
@click.argument('attempts', nargs=-1, callback=check_solution)
def find(attempts):
    regex_builder: ColorInfoWordleRegex = ColorInfoWordleRegex(attempts)
    words = __find_words(regex_builder)
    return words


def __find_words(regex_builder: WordleRegexBuilder):
    with open("5long.txt", "r") as file:
        all_words = file.read()
    regex_ = regex_builder.create()
    matches = execute_regex(all_words, regex_)
    click.echo(f"Found {len(matches)} words that match the passed structure...")
    scoring = SimpleScoring()
    matches = scoring.evaluate(matches)
    click.echo(f"{matches}")
    return matches, regex_


@wordle.command()
@click.argument("regex")
def regex(regex_):
    with open("5long.txt", "r") as file:
        all_words = file.read()
    word_list = execute_regex(all_words, regex_)
    print(word_list)


def find_words(word, contains, exclude, verbose):
    regex_builder: GlobWordleRegex = GlobWordleRegex(word, contains, exclude, verbose)
    return __find_words(regex_builder)


def execute_regex(all_words, regex_):
    matches = re.findall(regex_, all_words, re.IGNORECASE | re.MULTILINE)
    return matches


if __name__ == '__main__':
    wordle()
