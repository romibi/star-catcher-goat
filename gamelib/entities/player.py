import pygame as pg

from typing import List
from pygame import Rect

from config.gameconfig import ScreenMode
from gamelib.gamestate import GameState

class Player(pg.sprite.Sprite):

    images: List[pg.Surface] = []
    gridPos = 0
    hornGlowIntensity = 0
    bodyGlowIntensity = 0
    starsCatchedHorn = 0
    starsCatchedButt = 0

    def __init__(self, state: GameState, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.gamestate = state
        self.image = self.images[0]
        self.gridPos = 1
        self.facing = -1
        self.rect = Rect(0,0,0,0)
        self.reloading = 0
        self.origtop = self.rect.top
        self.updateImage()
        # todo: possible to remove hack?
        if not self.gamestate.vizConfig.vizGoatRects:
            if self.gamestate.screenMode == ScreenMode.GAME_BIG:
                self.gamestate.vizConfig.vizGoatRects = self.gamestate.vizConfig.vizGoatRectsB
            else:
                self.gamestate.vizConfig.vizGoatRects = self.gamestate.vizConfig.vizGoatRectsS
        self.updateRect()

    def reset(self):
        self.starsCatchedHorn = 0
        self.starsCatchedButt = 0
        self.facing = -1
        self.gridPos = 1
        self.updateImage()
        self.updateRect()


    def updateImage(self):
        if self.facing < 0:
            if self.HornGlowing and self.BodyGlowing:
                self.image = self.images[6]
            elif self.HornGlowing:
                self.image = self.images[2]
            elif self.BodyGlowing:
                self.image = self.images[4]
            else:
                self.image = self.images[0]
        elif self.facing > 0:
            if self.HornGlowing and self.BodyGlowing:
                self.image = self.images[7]
            elif self.HornGlowing:
                self.image = self.images[3]
            elif self.BodyGlowing:
                self.image = self.images[5]
            else:
                self.image = self.images[1]

    def updateRect(self):
        self.rect = self.gamestate.vizConfig.vizGoatRects[int(self.gridPos*2)+max(self.facing,0)]

    def moveInGrid(self):        
        maxGoatPos = round(self.gamestate.config.COLUMNS/2)-1
        if self.gamestate.config.COLUMNS == 3:
            maxGoatPos = 2

        if self.facing < 0:
            self.gridPos = max(self.gridPos-1,0)
        elif self.facing > 0:
            self.gridPos = min(self.gridPos+1,maxGoatPos)


    def update(self):
        self.hornGlowIntensity = max(self.hornGlowIntensity-1,0)
        self.bodyGlowIntensity = max(self.bodyGlowIntensity-1,0)
        self.updateImage()


    def move(self, direction):
        if direction == 0:
            return

        turned = (self.facing != direction)
        self.facing = direction

        if (not turned) or (self.gamestate.config.COLUMNS == 3):
            self.moveInGrid()        

        #print(f"gridPos: {self.gridPos}, facing: {self.facing}")

        self.updateImage()
        self.updateRect()


    def cursorMove(self, rect):
        self.rect = rect


    def HornGlow(self):
        self.hornGlowIntensity = 20
        self.updateImage()


    def BodyGlow(self):
        self.bodyGlowIntensity = 20
        self.updateImage()


    @property
    def HornGlowing(self):
        return self.hornGlowIntensity>0


    @property
    def BodyGlowing(self):
        return self.bodyGlowIntensity>0

    @property
    def HornColumn(self):
        if self.gamestate.config.COLUMNS == 3:
            return self.gridPos
        return self.gridPos * 2 + max(self.facing,0)


    @property
    def ButtColumn(self):
        if self.gamestate.config.COLUMNS == 3:
            return -1 # no butt column
        return self.gridPos*2 + (1-max(self.facing,0))


    def jump(self, stars):
        for star in stars:
            if star.gridPosX == self.HornColumn:
                self.starsCatchedHorn += 1
                self.HornGlow()
                if self.gamestate.CONTROLLER_PLAY_CATCH_SOUND:
                    self.triggerControllerSound("twinkle"); 
                #print(f"Catching Star: x:{star.gridPosX} y:{star.gridPosX}")
                star.kill()
        return

    def CatchStarPassive(self, star):
        if star.gridPosX == self.HornColumn:
            self.starsCatchedHorn += 1
            self.HornGlow()
            if self.gamestate.CONTROLLER_PLAY_CATCH_SOUND:
                self.triggerControllerSound("point")
            return True
        elif star.gridPosX == self.ButtColumn:
            self.starsCatchedButt += 1
            self.BodyGlow()
            if self.gamestate.CONTROLLER_PLAY_CATCH_SOUND:
                self.triggerControllerSound("point")
            return True
        return False

    def triggerControllerSound(self, sound_name):
        if self.triggerControllerSoundCallback != None:
            self.triggerControllerSoundCallback(sound_name); # note: blocks receiving controller data
