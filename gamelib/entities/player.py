import pygame as pg

from typing import List
from pygame import Rect

from config.gameconfig import ScreenMode
from gamelib.gamestate import GameState

# todo: fix warnings

class Player(pg.sprite.Sprite):

    images: List[pg.Surface] = []
    gridPos = 0
    hornGlowIntensity = 0.0
    bodyGlowIntensity = 0.0
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
        # todo: possible to remove hacks?
        self.triggerControllerSoundCallback = None
        if not self.gamestate.vizConfig.vizGoatRects:
            if self.gamestate.screenMode == ScreenMode.GAME_BIG:
                self.gamestate.vizConfig.vizGoatRects = self.gamestate.vizConfig.vizGoatRectsB
            else:
                self.gamestate.vizConfig.vizGoatRects = self.gamestate.vizConfig.vizGoatRectsS
        self.updateRect()

    @property
    def led(self):
        return self.gamestate.LED_HANDLER


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


    def updateLeds(self):
        body_color = self.led.GOAT_BODY_COLOR_RGB
        horn_color = self.led.GOAT_HORN_COLOR_RGB

        body_color = body_color.lerp(self.led.GOAT_BODY_COLOR_GLOW_RGB, self.bodyGlowIntensity)
        horn_color = horn_color.lerp(self.led.GOAT_HORN_COLOR_GLOW_RGB, self.hornGlowIntensity)

        body_color_hex = f'{body_color.r:02x}{body_color.g:02x}{body_color.b:02x}'.upper()
        horn_color_hex = f'{horn_color.r:02x}{horn_color.g:02x}{horn_color.b:02x}'.upper()

        self.led.set_goat_led(self.viz_pos,self.led.GOAT_BRIGHTNESS, body_color_hex, horn_color_hex)
        # todo: immediately update goat leds? or later?
        self.led.update_leds(update_stars=False, update_goats=True) # immediately update goat leds


    @property
    def viz_pos(self):
        return int(self.gridPos*2)+max(self.facing,0)

    def updateRect(self):
        self.rect = self.gamestate.vizConfig.vizGoatRects[self.viz_pos]

    def moveInGrid(self):        
        maxGoatPos = round(self.gamestate.config.COLUMNS/2)-1
        if self.gamestate.config.COLUMNS == 3:
            maxGoatPos = 2

        if self.facing < 0:
            self.gridPos = max(self.gridPos-1,0)
        elif self.facing > 0:
            self.gridPos = min(self.gridPos+1,maxGoatPos)

    @property
    def points(self):
        return max(((self.starsCatchedHorn * 10) + self.starsCatchedButt - self.gamestate.StarsMissed), 0)

    def update(self):
        self.hornGlowIntensity = max(self.hornGlowIntensity-(1.0/20),0.0)
        self.bodyGlowIntensity = max(self.bodyGlowIntensity-(1.0/20),0.0)
        self.updateImage()
        self.updateLeds()


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
        self.hornGlowIntensity = 1.0
        self.updateImage()


    def BodyGlow(self):
        self.bodyGlowIntensity = 1.0
        self.updateImage()


    @property
    def HornGlowing(self):
        return self.hornGlowIntensity>0.001


    @property
    def BodyGlowing(self):
        return self.bodyGlowIntensity>0.001

    @property
    def HornColumn(self):
        if self.gamestate.config.COLUMNS == 3:
            return self.gridPos
        return self.viz_pos

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
                    self.triggerControllerSound("twinkle")
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
        if self.triggerControllerSoundCallback:
            self.triggerControllerSoundCallback(sound_name) # note: blocks receiving controller data
