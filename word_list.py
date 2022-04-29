import itertools
import json
import random

import click


@click.group()
def cli1():
    pass


@click.group()
def statistic():
    pass


class StartWordManager:

    def update_statistics(self, won: bool, attempts: int):
        with open("start_words.json", mode="r") as file:
            json_file = json.load(file)
        word_list = [w for w in json_file if w['word'] == self.__start_word]

        if not word_list:
            self.add_start_word_statistics(self.__start_word, 1 if won else 0, 1 if not won else 0, attempts)
        else:
            word = word_list[0]
            if won:
                word['won'] += 1
            else:
                word['lost'] += 1

            word['all_attempts'] += attempts
            word['avg_attempts'] = word['all_attempts'] / (word['won'] + word['lost'])

        with open("start_words.json", mode="w") as file:
            json.dump(json_file, file, indent=2)
        self.__statistics_updated = True

    @property
    def start_word(self):
        if not self.__statistics_updated:
            raise Exception("Update statistics before getting another start_word")
        if self.__generate_word:
            with open("start_words.json", mode="r") as file:
                json_file = json.load(file)
            length = len(json_file)
            randint = random.randint(0, length - 1)
            self.__start_word = json_file[randint]['word']
        return self.__start_word

    @start_word.setter
    def start_word(self, value):
        self.__start_word = value

    def __init__(self, start_word: str = None) -> None:
        self.__generate_word = start_word is None
        self.__start_word = start_word
        self.__statistics_updated = True

    @staticmethod
    def add_start_word_statistics(word: str, won: int = 0, lost: int = 0, all_attempts: int = 0,
                                  avg_attempts: int = None):
        with open("start_words.json", mode="r") as file:
            load = json.load(file)

        j_obj = [w for w in load if w['word'] == word]
        if j_obj:
            print(f"Word '{word}' already in wordlist:")
            print(json.dumps(j_obj[0], indent=2))
            return

        load.append(
            {
                "word": word,
                "won": won,
                "lost": lost,
                "all_attempts": all_attempts,
                "avg_attempts": avg_attempts
            }
        )
        with open("start_words.json", mode="w") as file:
            json.dump(load, file, indent=2)


class CleanupWordListManager(StartWordManager):

    @property
    def start_word(self):
        with open("5long.txt", mode="r") as file:
            for line in itertools.islice(file, self.__index, self.__index + 1):
                return line[:-1]

    def update_statistics(self, won: bool, attempts: int):
        self.__index += 1
        with open(".index", mode="w") as file:
            file.write(str(self.__index))

    def __init__(self, start_word: str = None) -> None:
        with open(".index", mode="r") as file:
            self.__index = int(file.read())


@cli1.command()
@click.argument("word")
def add_start_word(word):
    StartWordManager.add_start_word_statistics(word)


@cli1.command("remove")
@click.argument("word")
@click.pass_context
def remove(ctx, word):
    remove_word(word)
    ctx.invoke(create_wordlist_command)
    ctx.invoke(create_statistics)


def remove_word(word):
    with open("blacklist.txt", mode="a") as blacklist:
        blacklist.writelines(word + "\n")

    create_wordlist()
    create_statistics()


@statistic.command()
def create_statistic():
    create_statistics()


@statistic.command()
def print_statistics():
    import json
    with open("statistics.json", mode="r") as file:
        dic = json.load(file)
        d = dict(sorted(dic.items(), key=lambda x: x[1], reverse=True))
        for k, v in d.items():
            print(f"{k}: {v}")


def create_statistics():
    statistics = {}
    with open("5long.txt") as file:
        for word in file.readlines():
            for c in set(word[:5]):
                c = c.lower()
                if c in statistics:
                    statistics[c] = statistics[c] + 1
                else:
                    statistics[c] = 1
    import json
    with open("statistics.json", mode="w") as file:
        file.write(json.dumps(statistics, indent=4, sort_keys=True))


@cli1.command("create-wordlist")
def create_wordlist_command():
    create_wordlist()


def create_wordlist():
    words = []
    with open("german.dic", mode='r', encoding="ISO-8859-1") as file:
        for line in file.readlines():
            if len(line) == 6:
                words.append(line)
    with open("blacklist.txt", mode="r") as file:
        for line in file.readlines():
            words.remove(line)
    with open("5long.txt", mode='w') as file:
        file.writelines(words)
    click.echo("Done recreating wordlists!")


@cli1.command("all")
@click.pass_context
def all(ctx):
    ctx.invoke(create_wordlist_command)
    ctx.invoke(create_statistics)


cli = click.CommandCollection(sources=[cli1, statistic])

if __name__ == '__main__':
    cli()
