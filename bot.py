import subprocess
import time

from PIL import ImageOps
from PIL.Image import Image

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
@click.option('-g', '--greyscale', required=False, is_flag=True, default=False)
def screenshot(path, greyscale):
    if not path:
        gui_screenshot = gui.screenshot()
    else:
        gui_screenshot = gui.screenshot(True, path)

    if greyscale:
        screenshot_path = gui_screenshot.path
        gui.greyscale(gui_screenshot)


@cli.command()
@click.option('-p', '--path', type=click.Path(exists=True))
def greyscale(path):
    gui.greyscale(path)


@cli.command()
@click.option('-p', '--path', type=click.Path(exists=True))
def get_colors(path):
    gui.get_colors(path)


@cli.command()
def phone_start():
    phone()


@cli.command()
@click.option("-o", "--open", is_flag=True, default=False)
@click.pass_context
def start(ctx, open):
    if open:
        phone()
    time.sleep(2)
    gui.click_on("app")
    time.sleep(5)
    gui.click_on("play")

    gui.type("stier")

    gui.click_on("submit")
    time.sleep(4)
    gui.screenshot()


def phone():
    command = ["scrcpy", "--always-on-top", "--window-width", "470", "--window-height", "1015", "--window-x", "0",
               "--window-y", "0"]
    subprocess.Popen(command, shell=False,
                     stdin=None, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)


if __name__ == '__main__':
    cli()
