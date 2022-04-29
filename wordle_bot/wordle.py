import itertools
import re
from abc import ABC, abstractmethod
from collections import defaultdict
from enum import Enum
from typing import Set, List, Dict, Optional

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
    InfoCoding.NOT_CONTAINED.value: InfoCoding.NOT_CONTAINED,
    InfoCoding.CONTAINED.value: InfoCoding.CONTAINED
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

    def __init__(self, index, character, other_occurrences=None):
        self.__index: int = index
        self.__character: str = character
        self.__regex: str = character
        self._other_occurrences: Dict[InfoCoding, List[int]] = other_occurrences

    @abstractmethod
    def add_self_to_regex(self, builder: 'WordleRegexBuilder') -> None:
        pass

    @abstractmethod
    def _init_lookahead(self) -> (int, bool):
        """lookahead logic requires the initial values
        int -> start count is 1 or zero depending on self
        bool -> if there is somewhere a NOT_CONTAINED element"""
        pass

    def _create_lookahead(self, builder: 'WordleRegexBuilder') -> None:
        count, or_more = self._init_lookahead()

        if InfoCoding.CONTAINED in self._other_occurrences:
            count += len(self._other_occurrences[InfoCoding.CONTAINED])
        if InfoCoding.CORRECT in self._other_occurrences:
            count += len(self._other_occurrences[InfoCoding.CORRECT])

        occurrence_multiplier_new = Multiplier(self.character, count, or_more)
        if self.character in builder.lookaheads:
            occurrence_multiplier_old = builder.lookaheads[self.character]
            if occurrence_multiplier_old.count < occurrence_multiplier_new.count or \
                    occurrence_multiplier_old.or_more and not occurrence_multiplier_new.or_more:
                builder.lookaheads[self.character] = occurrence_multiplier_new
        else:
            builder.lookaheads[self.character] = occurrence_multiplier_new

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(Index: {self.index} Character: {self.character})"

    def __repr__(self):
        return self.__str__()


class SolvedChar(Char):

    def _init_lookahead(self) -> (int, bool):
        """1 -> count itself as occurrence, see if NOT_CONTAINED is other occurrence"""
        return 1, InfoCoding.NOT_CONTAINED not in self._other_occurrences

    def add_self_to_regex(self, builder: 'WordleRegexBuilder') -> None:
        if not builder.elements[self.index]:
            builder.elements[self.index] = self.character
        elif builder.elements[self.index] and builder.elements[self.index] != self.character:
            raise ImmutableElementException
        else:
            return  # skip

    def __init__(self, index: int, character: str):
        super().__init__(index, character)


class ContainedChar(Char):

    def _init_lookahead(self) -> (int, bool):
        """1 -> count itself as occurrence, see if NOT_CONTAINED is other occurrence"""
        return 1, InfoCoding.NOT_CONTAINED not in self._other_occurrences

    def add_self_to_regex(self, builder: 'WordleRegexBuilder') -> None:
        builder.excludes[self.index].add(self.character)
        self._create_lookahead(builder)

    def __init__(self, index, character, other_occurrences):
        super().__init__(index, character, other_occurrences)


class NotContainedChar(Char):

    def _init_lookahead(self) -> (int, bool):
        """0 -> don't count itself as occurrence, self is NOT_CONTAINED, so we have upper count aka 'not or_more'"""
        return 0, False

    def add_self_to_regex(self, builder: 'WordleRegexBuilder') -> None:
        if InfoCoding.CONTAINED in self._other_occurrences:
            # exclude only from index, leave rest to contained char
            builder.excludes[self.index].add(self.character)
        elif InfoCoding.CORRECT in self._other_occurrences and InfoCoding.CONTAINED not in self._other_occurrences:
            self._create_lookahead(builder)
            for i in range(len(builder.excludes)):
                if i not in itertools.chain.from_iterable(self._other_occurrences.values()):
                    builder.excludes[i].add(self.character)
        else:
            [excludes.add(self.character) for excludes in builder.excludes]

    def __init__(self, index: int, character: str, other_occurrences):
        super().__init__(index, character, other_occurrences)


class Word:

    def __init__(self, word: str, info: str) -> None:
        self.character_list: List[Char] = [None] * 5
        self._character_dict: Dict[str, List[int]] = defaultdict(list)
        [self._character_dict[char].append(i) for i, char in enumerate(word.lower())]

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
        self._regex_word_elements: List[Optional[str]] = [None] * 5
        self._regex_excluded_elements: List[Set[str]] = [set() for _ in range(5)]
        self._regex_lookahead_elements: Dict[str, Multiplier] = {}

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

    @property
    def character(self):
        return self.__character

    def __init__(self, character: str, count: int, or_more: bool):
        self.__character = character
        self.__count = count
        self.__or_more = or_more

    def to_regex_string(self):
        if self.count == 1 and self.or_more:
            multiplier_string = f"(?:.*{self.character})+"
        elif self.count > 1 and self.or_more:
            multiplier_string = f"(?:{'.*' + self.character}){{{self.count},}}"
        elif self.count == 1 and not self.or_more:
            multiplier_string = f"(?:.*{self.character})"
        elif self.count > 1 and not self.or_more:
            multiplier_string = f"(?:{'.*' + self.character}){{{self.count}}}"
        else:
            raise ValueError("Uncovered Multiplier Condition")
        return "(?=" + multiplier_string + ")"


class ColorInfoWordleRegex(WordleRegexBuilder):

    def __init__(self, attempts) -> None:
        super().__init__()
        self.__attempts: [Word]
        if isinstance(attempts, list):
            self.__attempts: [Word] = [Word(word, info) for word, info in [attempt for attempt in attempts]]
        elif isinstance(attempts, dict):
            self.__attempts: [Word] = [Word(key, value) for key, value in attempts.items()]
        else:
            raise ValueError("either dict or list")

    def __generate_element_list(self):
        return [multiplier.to_regex_string() for multiplier in self.lookaheads.values()] + ["^"] + [
            self.elements[i] if self.elements[i] else "[^" + "".join(self.excludes[i]) + "]"
            for i in range(len(self.elements))] + ["$"]

    def create(self) -> str:
        __attempt: Word
        for __attempt in self.__attempts:
            __attempt.process(self)

        element_list = self.__generate_element_list()
        regex_string = "".join(element_list)
        print(regex_string)
        return regex_string


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
            with open("../files/statistics.json") as file:
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

            with open("../files/whitelist.txt") as file:
                all_solution_words = file.read()

            if word in all_solution_words:
                score += 29
            return score

        word_list.sort(reverse=True, key=sort_word)
        return word_list


@click.group()
def wordle():
    pass


def check_solution(ctx, param, value):
    if len(value) % 2 != 0:
        click.BadArgumentUsage("has always to be word and word-information", ctx)

    for i in range(0, len(value), 2):
        word: str = value[i]
        info: str = value[i + 1]
        if len(info) != 5 or len(word) != 5:
            click.BadArgumentUsage("Length of info and word has to be 5")
        info_ = info.replace("t", "").replace("f", "").replace("c", "")
        if len(info_) != 0:
            print("Word info contains unrecognized character(s): " + info_)
    return [(value[i], value[i + 1]) for i in range(0, len(value), 2)]


@wordle.command("solve")
@click.argument('attempts', nargs=-1, callback=check_solution)
def find(attempts):
    regex_builder: ColorInfoWordleRegex = ColorInfoWordleRegex(attempts)
    words = __find_words(regex_builder)
    return words


def __find_words(regex_builder: WordleRegexBuilder):
    with open("../files/5long.txt", "r") as file:
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
    with open("../files/5long.txt", "r") as file:
        all_words = file.read()
    word_list = execute_regex(all_words, regex_)
    print(word_list)


def find_words(attempts):
    regex_builder: WordleRegexBuilder = ColorInfoWordleRegex(attempts)
    return __find_words(regex_builder)


def execute_regex(all_words, regex_):
    matches = re.findall(regex_, all_words, re.IGNORECASE | re.MULTILINE)
    return matches


if __name__ == '__main__':
    wordle()
