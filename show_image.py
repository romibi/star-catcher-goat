#!/usr/bin/env python

import os
import sys

import pygame as pg
from pygame import Rect

# see if we can load more than standard BMP
if not pg.image.get_extended():
    raise SystemExit("Sorry, extended image module required")

def load_image(file, subfolder=None):
    """loads an image, prepares it for play"""
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit(f'Could not load image "{file}" {pg.get_error()}')
    #surface = surface.convert()
    return surface.convert_alpha()


def main():
    # Initialize pygame
    if pg.get_sdl_version()[0] == 2:
        pg.mixer.pre_init(44100, 32, 2, 1024)
    pg.init()
    if pg.mixer and not pg.mixer.get_init():
        print("Warning, no sound")
        pg.mixer = None

    # Set the display mode
    SCREEN_RECT = Rect(0, 0, 1280, 720)
    best_depth = pg.display.mode_ok(SCREEN_RECT.size, 0, 32)
    screen = pg.display.set_mode(SCREEN_RECT.size, 0, best_depth)

    pg.display.set_caption("Pygame Star Catcher Goat (show_image)")
    pg.mouse.set_visible(0)

    # create the background, tile the bgd image
    background_tile = load_image(sys.argv[1])
    background = pg.Surface(SCREEN_RECT.size)
    for x in range(0, SCREEN_RECT.width, background_tile.get_width()):
        background.blit(background_tile, (x, 0))
    screen.blit(background, (0, 0))
    pg.display.flip()

    # Create Some Starting Values
    clock = pg.time.Clock()

    keep_running = True
    while keep_running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                keep_running = False
                continue
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    keep_running = False
                    continue
        clock.tick(0.1)

    if pg.mixer:
        pg.mixer.music.fadeout(1000)
    pg.time.wait(1000)

# call the "main" function if running this script
if __name__ == "__main__":
    main()
    pg.quit()
