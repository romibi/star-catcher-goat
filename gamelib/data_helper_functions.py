import os
import pygame as pg

main_dir = os.path.split(os.path.abspath(os.path.join(__file__, "..")))[0]

def load_image(file, subfolder=None):
    """loads an image, prepares it for play"""
    if subfolder:
        file = os.path.join(main_dir, "data", subfolder, file)
    else:
        file = os.path.join(main_dir, "data", file)

    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit(f'Could not load image "{file}" {pg.get_error()}')
    #surface = surface.convert()
    return surface.convert_alpha()


def load_sound(file):
    """because pygame can be compiled without mixer."""
    if not pg.mixer:
        return None
    file = os.path.join(main_dir, "data", file)
    try:
        sound = pg.mixer.Sound(file)
        return sound
    except pg.error:
        print(f"Warning, unable to load, {file}")
    return None

def load_font(size, font_name="PixelOperator-Bold.ttf"):
    """Loads the game default font in the requested size"""
    file = os.path.join(main_dir, "data", "fonts", font_name)
    return pg.font.Font(file, size)
