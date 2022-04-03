import subprocess
import time

import gui_helper as gui

import click


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
        screenshot = gui.screenshot(True, path)
        print(screenshot)



@cli.command()
@click.option("-o", "--open", is_flag=True, default=False)
@click.pass_context
def start(ctx, open):
    if open:
        command = ["scrcpy", "--always-on-top", "--window-width", "470", "--window-height", "1015", "--window-x", "0",
                   "--window-y", "0"]
        subprocess.Popen(command, shell=False,
                         stdin=None, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
    time.sleep(2)
    gui.click_on("app")
    time.sleep(5)
    gui.click_on("play")

    gui.type("stier")

    gui.click_on("submit")


if __name__ == '__main__':
    cli()
