import pygame as pg

from typing import List
from pygame import Rect, Surface

from gamelib.data_helper_functions import load_font


class UiText(pg.sprite.Sprite):
    text = ""

    def __init__(self, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.font = load_font(48)
        #self.font.set_italic(1)
        self.color = "white"
        self.lastText = None
        self.lastTargetRect = None
        self.textFunc = None
        self.targetRect = Rect(0,0,0,0)
        self.align = -1 # -1 left, 0 center, 1 right
        self.crop = False
        self.update()
        self.image = self.font.render(self.text, 0, self.color)
        self.rect = self.image.get_rect().move(10, 450)


    def update(self, *args, **kwargs):
        """We only update the score in update() when it has changed."""
        if self.textFunc:
            self.text = self.textFunc()

        if (self.text != self.lastText) or (self.targetRect != self.lastTargetRect):
            self.lastText = self.text
            self.lastTargetRect = self.targetRect
            img = self.font.render(self.text, 0, self.color)
            self.image = img

            self.rect = self.targetRect.copy()
            if self.align == 0:
                self.rect.left = self.rect.left + ((self.targetRect.width - img.get_rect().width) / 2)
            elif self.align == 1:
                self.rect.left = self.rect.left + (self.targetRect.width - img.get_rect().width)

            if self.crop:
                self.rect.width = img.get_rect().width
                img = Surface((self.rect.width, self.rect.height), pg.SRCALPHA)
                img.blit(self.image, (0,0), self.image.get_rect())
                self.image = img



class ImageIcon(pg.sprite.Sprite):
    animation_cycle = 24
    images: List[pg.Surface] = []
    paused = False

    def __init__(self, x, y, images, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.images = images
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.frame = 0

    def update(self, *args, **kwargs):
        if self.paused:
            self.image = self.images[0]
            return

        self.frame = self.frame + 1
        self.image = self.images[self.frame // self.animation_cycle % len(self.images)]


class ButtonIcon(ImageIcon):
    def __init__(self, x, y, images, *groups):
        ImageIcon.__init__(self, x, y, images, *groups)


class LineSprite(ImageIcon):
    def __init__(self, x, y, points, linethickness, color, *groups):
        width = 0
        height = 0
        for point in points:
            width = max(width, point[0])
            height = max(height, point[1])
        width += linethickness/2
        height += linethickness/2
        image = pg.surface.Surface((width, height), pg.SRCALPHA)

        pg.draw.lines(image, color, False, points, linethickness)
        for p in points:
            pg.draw.circle(image, color, p, linethickness/2)

        ImageIcon.__init__(self, x, y, [image], groups)
        self.points = points
        self.linethickness = linethickness
        self.color = color
