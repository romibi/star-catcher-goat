import pygame as pg

from typing import List

from gamelib.gamestate import GameState

class Star(pg.sprite.Sprite):

    gridPosX = 0
    gridPosY = 0
    images: List[pg.Surface] = []


    def __init__(self, state: GameState, column, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.gamestate = state
        self.image = self.images[0]
        self.gridPosX = column
        self.gridPosY = -1
        self.rect = self.gamestate.vizConfig.vizRects[self.gridPosY+1][self.gridPosX]
        self.facing = 0
        self.frame = 0

    @property
    def hangingLow(self):
        return self.gridPosY>=(self.gamestate.config.ROWS-1)

    def fall(self):
        self.gridPosY += 1
        if self.gridPosY < self.gamestate.config.ROWS:
            self.rect = self.gamestate.vizConfig.vizRects[self.gridPosY][self.gridPosX]
        else:
            self.land()


    def land(self, player=None):
        if self.frame % self.gamestate.config.STAR_MOVE_RATE != 0:
            return

        catched = False
        if not player == None:
            catched = player.CatchStarPassive(self)
        if not catched:
            self.gamestate.StarsMissed += 1
        self.kill()


    def update(self, *args, **kwargs):
        #self.rect.move_ip(self.facing, 1)
        if self.frame % self.gamestate.config.STAR_MOVE_RATE == 0:
            self.fall()

        if not self.gamestate.SCREENRECT.contains(self.rect):
            self.facing = -self.facing
            self.rect.top = self.rect.bottom + 1
            self.rect = self.rect.clamp(self.gamestate.SCREENRECT)
        self.frame = self.frame + 1
