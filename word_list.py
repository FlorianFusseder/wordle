import click


@click.group()
def cli():
    pass


@cli.command("remove")
@click.argument("word")
@click.pass_context
def remove(ctx, word):
    remove_word(word)
    click.echo("Done add to remove")
    ctx.invoke(create)
    ctx.invoke(statistics)


def remove_word(word):
    with open("blacklist.txt", mode="a") as blacklist:
        blacklist.writelines(word + "\n")

    create_wordlist()
    create_statistics()


@cli.command("statistics")
def statistics():
    create_statistics()


def create_statistics():
    statistics = {}
    with open("5long.txt") as file:
        for word in file.readlines():
            for i, c in enumerate(word):
                if i == 5:
                    continue
                c = c.lower()
                if c in statistics:
                    statistics[c] = statistics[c] + 1
                else:
                    statistics[c] = 1
    import json
    with open("statistics.json", mode="w") as file:
        file.write(json.dumps(statistics))
    click.echo("Done")


@cli.command("create")
def create():
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
    click.echo("Done create")


@cli.command("all")
@click.pass_context
def all(ctx):
    ctx.invoke(create)
    ctx.invoke(statistics)


if __name__ == '__main__':
    cli()
