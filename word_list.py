import click


@click.group()
def cli1():
    pass


@click.group()
def statistic():
    pass


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
