#!/usr/bin/env python

import os
import random
from typing import List
import pygame as pg
from pygame import Rect
import grequests
from enum import Enum

# see if we can load more than standard BMP
if not pg.image.get_extended():
    raise SystemExit("Sorry, extended image module required")

# difficulty settings
STAR_BASE_LIKELYHOOD = 0.3 # at start 30% chance of 1 star. (15% for 2nd star)
STAR_MAX_LIKELYHOOD = 0.95 # max chance of 95% for 1 star (47.5% for 2nd star)
STAR_TIMER_LIKELYHOOD = 0.0005 # star spawn likely hood increase over time
FORCE_STAR_SPAWN_MIN = 2 # if 2 or less stars 1 star spawns 100%
MAX_STARS = 2 # max stars per row

# LED Stuff
STAR_COLOR = 'FF9000';
STAR_BRIGHTNESS = 255;

HUB_ADDR_STAR_1 = '192.168.1.107';
HUB_ADDR_STAR_2 = '';
HUB_ADDR_STAR_3 = '';
HUB_ADDR_STAR_4 = '';
HUB_ADDR_STAR_5 = '';
HUB_ADDR_STAR_6 = '';

# change color of segment 1 (0) to green: http://192.168.1.107/win&SM=0&SB=255&CL=H00FF00
API_ADDR = '/win';
API_ARG_SEGMENT = '&SM=';
API_ARG_BRIGHTNES = '&SB=';
API_ARG_COLOR = '&CL=H'

# speed
FRAME_COUNT = 0
FRAME_RATE = 10; # fps
STAR_MOVE_RATE = 10; # stars move every x frames

# game end
STAR_STOP_SPAWN_FRAMECOUNT = 1120; # no more stars after 112 seconds
GAME_END_FRAMECOUNT = 1200; # stop game loop after 120 seconds

# how many stars? 3x6 or 6x6
GAME_ROWS = 6;
GAME_COLUMNS = 6; # code works with 3 or 6 columns

SCREENRECT = pg.Rect(0, 0, 1280, 720)

main_dir = os.path.split(os.path.abspath(__file__))[0]

CURRENT_MENU = None
MENU_JUST_CLOSED = False
GAME_QUIT = False

# helper functions
def load_image(file):
    """loads an image, prepares it for play"""
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


# game status:
# let rowTemplate = Array(columns).fill(false);
# let stars = Array.from(Array(rows), () => [...rowTemplate]);
# goatPos = 0; # 0 = column 0&1, 1 = column 2&3, 2 = column 4&5
# goatDir = 0; # 0 = left, 1 = right;

# // missed points (other points in player class)
GAME_StarsMissed = 0;

# vizPos für 3 columns
vizRects3 = [
   [ Rect(84,  72, 32, 32),                                                 Rect(372,  72, 32, 32), Rect(552,  72, 32, 32)                        ],
   [                        Rect(138, 108, 32, 32), Rect(318, 108, 32, 32),                                                 Rect(606, 108, 32, 32)],
   [ Rect(84, 144, 32, 32),                                                 Rect(372, 144, 32, 32), Rect(552, 144, 32, 32)                        ],

   [                        Rect(138, 288, 32, 32),                         Rect(372, 288, 32, 32),                         Rect(606, 288, 32, 32)],
   [ Rect(84, 324, 32, 32),                         Rect(318, 324, 32, 32),                         Rect(552, 324, 32, 32)                        ],
   [                        Rect(138, 360, 32, 32),                         Rect(372, 360, 32, 32),                         Rect(606, 360, 32, 32)]
]

# vizPos für 6 columns
vizRects6 = [
   [ Rect(84,  72, 32, 32), Rect(138,  72, 32, 32), Rect(318,  72, 32, 32), Rect(372,  72, 32, 32), Rect(552,  72, 32, 32), Rect(606,  72, 32, 32)],
   [ Rect(84, 108, 32, 32), Rect(138, 108, 32, 32), Rect(318, 108, 32, 32), Rect(372, 108, 32, 32), Rect(552, 108, 32, 32), Rect(606, 108, 32, 32)],
   [ Rect(84, 144, 32, 32), Rect(138, 144, 32, 32), Rect(318, 144, 32, 32), Rect(372, 144, 32, 32), Rect(552, 144, 32, 32), Rect(606, 144, 32, 32)],

   [ Rect(84, 288, 32, 32), Rect(138, 288, 32, 32), Rect(318, 288, 32, 32), Rect(372, 288, 32, 32), Rect(552, 288, 32, 32), Rect(606, 288, 32, 32)],
   [ Rect(84, 324, 32, 32), Rect(138, 324, 32, 32), Rect(318, 324, 32, 32), Rect(372, 324, 32, 32), Rect(552, 324, 32, 32), Rect(606, 324, 32, 32)],
   [ Rect(84, 360, 32, 32), Rect(138, 360, 32, 32), Rect(318, 360, 32, 32), Rect(372, 360, 32, 32), Rect(552, 360, 32, 32), Rect(606, 360, 32, 32)]
]

vizGoatRects = [ Rect(84, 540, 64, 64), Rect(110, 540, 64, 64), Rect(318, 540, 64, 64), Rect(344, 540, 64, 64), Rect(552, 540, 64, 64), Rect(578, 540, 64, 64)]

# LED info
# Segment map for when only halve the stars are wired:
#ledSegmentMap3 = [
#   [ {"hub": 1, "segment": 2},                                                     {"hub": 2, "segment": 2}, {"hub": 3, "segment": 2}                          ],
#   [                           {"hub": 1, "segment": 1}, {"hub": 2, "segment": 1},                                                     {"hub": 3, "segment": 1}],
#   [ {"hub": 1, "segment": 0},                                                     {"hub": 2, "segment": 0}, {"hub": 3, "segment": 0}                          ],
#
#   [                           {"hub": 4, "segment": 2},                           {"hub": 5, "segment": 2},                           {"hub": 6, "segment": 2}],
#   [ {"hub": 4, "segment": 1},                           {"hub": 5, "segment": 1},                           {"hub": 6, "segment": 1},                         ],
#   [                           {"hub": 4, "segment": 0},                           {"hub": 5, "segment": 0},                           {"hub": 6, "segment": 0}]
#]

# Segment map for when 6x6 stars are wired but game is in 3x6 mode:
ledSegmentMap3 = [
   [ {"hub": 1, "segment": 2},                                                     {"hub": 2, "segment": 3}, {"hub": 3, "segment": 2}                          ],
   [                           {"hub": 1, "segment": 4}, {"hub": 2, "segment": 1},                                                     {"hub": 3, "segment": 4}],
   [ {"hub": 1, "segment": 0},                                                     {"hub": 2, "segment": 5}, {"hub": 3, "segment": 0}                          ],

   [                           {"hub": 4, "segment": 3},                           {"hub": 5, "segment": 3},                           {"hub": 6, "segment": 3}],
   [ {"hub": 4, "segment": 1},                           {"hub": 5, "segment": 1},                           {"hub": 6, "segment": 1},                         ],
   [                           {"hub": 4, "segment": 5},                           {"hub": 5, "segment": 5},                           {"hub": 6, "segment": 5}]
]

ledSegmentMap6 = [
   [ {"hub": 1, "segment": 2}, {"hub": 1, "segment": 3}, {"hub": 2, "segment": 2}, {"hub": 2, "segment": 3}, {"hub": 3, "segment": 2}, {"hub": 3, "segment": 3}],
   [ {"hub": 1, "segment": 1}, {"hub": 1, "segment": 4}, {"hub": 2, "segment": 1}, {"hub": 2, "segment": 4}, {"hub": 3, "segment": 1}, {"hub": 3, "segment": 4}],
   [ {"hub": 1, "segment": 0}, {"hub": 1, "segment": 5}, {"hub": 2, "segment": 0}, {"hub": 2, "segment": 5}, {"hub": 3, "segment": 0}, {"hub": 3, "segment": 5}],

   [ {"hub": 4, "segment": 2}, {"hub": 4, "segment": 3}, {"hub": 5, "segment": 2}, {"hub": 5, "segment": 3}, {"hub": 6, "segment": 2}, {"hub": 6, "segment": 3}],
   [ {"hub": 4, "segment": 1}, {"hub": 4, "segment": 4}, {"hub": 5, "segment": 1}, {"hub": 5, "segment": 4}, {"hub": 6, "segment": 1}, {"hub": 6, "segment": 4}],
   [ {"hub": 4, "segment": 0}, {"hub": 4, "segment": 5}, {"hub": 5, "segment": 0}, {"hub": 5, "segment": 5}, {"hub": 6, "segment": 0}, {"hub": 6, "segment": 5}]
]

vizRects = None # initialized in setup/reset
ledSegmentMap = None # initialized in setup/reset

class LedHandler():
    hubs = {}
    stars = {}
    leds = {}

    def __init__(self):
        self.reset()


    def reset(self):
        self.hubs = {}
        self.stars = {}
        self.leds = {}

        if HUB_ADDR_STAR_1 != '':
            self.AddStarHub(1, HUB_ADDR_STAR_1)
        if HUB_ADDR_STAR_2 != '':
            self.AddStarHub(2, HUB_ADDR_STAR_2)
        if HUB_ADDR_STAR_3 != '':
            self.AddStarHub(3, HUB_ADDR_STAR_3)
        if HUB_ADDR_STAR_4 != '':
            self.AddStarHub(4, HUB_ADDR_STAR_4)
        if HUB_ADDR_STAR_5 != '':
            self.AddStarHub(5, HUB_ADDR_STAR_5)
        if HUB_ADDR_STAR_6 != '':
            self.AddStarHub(6, HUB_ADDR_STAR_6)

        for row in range(GAME_ROWS):
            self.stars[row] = {}
            self.leds[row] = {}
            for column in range(GAME_COLUMNS):
                self.stars[row][column] = {}
                self.leds[row][column] = {}



    def AddStarHub(self, num, address):
        self.hubs[num] = address


    def GetStarHub(self, row, column):
        segment = ledSegmentMap[row][column]
        hub = segment["hub"]
        return self.hubs.get(hub, None)


    def GetLedApiUrl(self, row, column, bright, color):
        hub = self.GetStarHub(row, column);
        if not hub:
            return None;
  
        segment = ledSegmentMap[row][column];

        return f'http://{hub}{API_ADDR}{API_ARG_SEGMENT}{segment["segment"]}{API_ARG_BRIGHTNES}{bright}{API_ARG_COLOR}{color}'


    def SetStarLed(self, row, column, bright, color=None):
        self.stars[row][column]['bright'] = bright
        if not 'color' in self.stars[row][column]:
            self.stars[row][column]['color'] = STAR_COLOR
        if color:
            self.stars[row][column]['color'] = color


    def SetAllStarsOff(self):
        for row, starRow in self.stars.items():
            for column, star in starRow.items():
                self.SetStarLed(row, column, 0)


    def UpdateStars(self):
        urls = []
        for row, starRow in self.stars.items():
            for column, star in starRow.items():
                led = self.leds[row][column]

                starBrigth = star.get('bright', 0)
                ledBrigth = led.get('bright', None)

                starColor = star.get('color', STAR_COLOR)
                ledColor = star.get('color', None)

                if (starBrigth == ledBrigth) and (starColor == ledColor):
                    continue

                self.leds[row][column]['bright'] = starBrigth
                self.leds[row][column]['color'] = starColor

                apiUrl = self.GetLedApiUrl(row, column, starBrigth, starColor)
                if not apiUrl:
                    continue

                urls += [apiUrl]
                #print(f"Adding url for star row: {row} column: {column} to request: {apiUrl}")

        #if len(urls)>0:
        #    print(f"triggering url: {urls}")
        rs = (grequests.get(u, timeout=0.00001) for u in urls)
        grequests.map(rs)
        # TODO maybe show error message? (no timeout exception?)


def reset(newColumns, player, stars, screen, leds):
    global GAME_COLUMNS, FRAME_COUNT, GAME_StarsMissed, vizRects, ledSegmentMap

    leds.SetAllStarsOff()
    leds.UpdateStars()

    GAME_COLUMNS = newColumns

    if GAME_COLUMNS == 3:
        vizRects = vizRects3
        ledSegmentMap = ledSegmentMap3
    else:
        vizRects = vizRects6
        ledSegmentMap = ledSegmentMap6

    leds.reset()

    player.starsCatchedHorn = 0
    player.starsCatchedButt = 0
    GAME_StarsMissed = 0

    for star in stars:
        star.kill()

    ReRenderBackground(screen)
    pg.display.flip()

    FRAME_COUNT = 0

class Star(pg.sprite.Sprite):

    gridPosX = 0
    gridPosY = 0
    images: List[pg.Surface] = []


    def __init__(self, column, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.image = self.images[0]
        self.gridPosX = column
        self.gridPosY = -1
        self.rect = vizRects[self.gridPosY+1][self.gridPosX]
        self.facing = 0
        self.frame = 0

    @property
    def hangingLow(self):
        return self.gridPosY>=(GAME_ROWS-1)

    def fall(self):
        self.gridPosY += 1
        if self.gridPosY < GAME_ROWS:
            self.rect = vizRects[self.gridPosY][self.gridPosX]
        else:
            self.land()


    def land(self, player=None):
        global GAME_StarsMissed

        if self.frame % STAR_MOVE_RATE != 0:
            return

        catched = False
        if not player == None:
            catched = player.CatchStarPassive(self)
        if not catched:
            GAME_StarsMissed += 1
        self.kill()


    def update(self, *args, **kwargs):
        #self.rect.move_ip(self.facing, 1)
        if self.frame % STAR_MOVE_RATE == 0:
            self.fall()

        if not SCREENRECT.contains(self.rect):
            self.facing = -self.facing
            self.rect.top = self.rect.bottom + 1
            self.rect = self.rect.clamp(SCREENRECT)
        self.frame = self.frame + 1


class Player(pg.sprite.Sprite):

    images: List[pg.Surface] = []
    gridPos = 0
    hornGlowIntensity = 0
    bodyGlowIntensity = 0
    starsCatchedHorn = 0
    starsCatchedButt = 0

    def __init__(self, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.image = self.images[0]
        self.gridPos = 1
        self.facing = -1
        self.rect = Rect(0,0,0,0)
        self.reloading = 0
        self.origtop = self.rect.top
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
        self.rect = vizGoatRects[int(self.gridPos*2)+max(self.facing,0)]

    def moveInGrid(self):        
        maxGoatPos = round(GAME_COLUMNS/2)-1
        if GAME_COLUMNS == 3:
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

        if not turned:
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
        if GAME_COLUMNS == 3:
            return self.gridPos
        return self.gridPos * 2 + max(self.facing,0)


    @property
    def ButtColumn(self):
        if GAME_COLUMNS == 3:
            return -1 # no butt column
        return self.gridPos*2 + (1-max(self.facing,0))


    def jump(self, stars):
        for star in stars:
            if star.gridPosX == self.HornColumn:
                self.starsCatchedHorn += 1
                self.HornGlow()
                print(f"Catching Star: x:{star.gridPosX} y:{star.gridPosX}")
                star.kill()
        return

    def CatchStarPassive(self, star):
        if star.gridPosX == self.HornColumn:
            self.starsCatchedHorn += 1
            self.HornGlow()
            return True
        elif star.gridPosX == self.ButtColumn:
            self.starsCatchedButt += 1
            self.BodyGlow()
            return True
        return False


class UiText(pg.sprite.Sprite):
    ""
    text = ""

    def __init__(self, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.font = pg.font.Font(None, 48)
        #self.font.set_italic(1)
        self.color = "white"
        self.lastText = None
        self.lastTargetRect = None
        self.targetRect = Rect(0,0,0,0)
        self.align = -1 # -1 left, 0 center, 1 right
        self.update()
        self.rect = self.image.get_rect().move(10, 450)


    def update(self, *args, **kwargs):
        """We only update the score in update() when it has changed."""
        if (self.text != self.lastText) or (self.targetRect != self.lastTargetRect):
            self.lastText = self.text
            self.lastTargetRect = self.targetRect
            img = self.font.render(self.text, 0, self.color)
            self.image = img

            self.rect = self.targetRect.copy()
            if self.align == 0:
                self.rect.left = self.rect.left + ((self.targetRect.width - img.get_rect().width) / 2)
            elif self.align == 1:
                self.rect.left = self.rect.left + ((self.targetRect.width - img.get_rect().width))


class ButtonIcon(pg.sprite.Sprite):

    animcycle = 24
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
        self.image = self.images[self.frame // self.animcycle % 2]


class MenuScreen():
    def __init__(self, screen, menuOptionMap):
        self.screen = screen
        self.background = screen.copy()
        self.sprites = pg.sprite.RenderUpdates()
        self.cursor = UiText(self.sprites)
        self.cursor.text = ">"
        self.cursor.targetRect = Rect(50, 100, 64, 64)
        self.menuOptionMap = menuOptionMap
        self.cursorIndex = 0

        nextPos = 100
        for menuEntry in menuOptionMap.keys():
            entry = UiText(self.sprites);
            entry.text = menuEntry
            entry.targetRect = Rect(100, nextPos, 300, 300)
            nextPos += 50

        self.frame = -1

        overlayBg = pg.Surface(SCREENRECT.size, pg.SRCALPHA,32)
        overlayBg.fill((0,0,0, 150))
        self.background.blit(overlayBg, (0, 0))


    def Loop(self):
        self.frame += 1
        for event in pg.event.get():
            if event.type == pg.QUIT:
                global GAME_QUIT
                GAME_QUIT = True
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                CloseMenu()
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_DOWN:
                self.cursorIndex = min(self.cursorIndex+1, len(self.menuOptionMap.keys())-1)
                self.cursor.targetRect = Rect(50, 100+(self.cursorIndex*50), 64, 64)
            if event.type == pg.KEYDOWN and event.key == pg.K_UP:
                self.cursorIndex = max(self.cursorIndex-1, 0)
                self.cursor.targetRect = Rect(50, 100+(self.cursorIndex*50), 64, 64)
            if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                menuFuncs = list(self.menuOptionMap.values())
                func = menuFuncs[self.cursorIndex]()

        if self.frame == 0:
            self.screen.blit(self.background, (0, 0))

        self.sprites.clear(self.screen, self.background)

        self.sprites.update()

        # draw the scene
        if self.frame == 0:
            pg.display.flip()
        
        dirty = self.sprites.draw(self.screen)
        pg.display.update(dirty)


def spawnNewStarRow(stars, stargroups):
    if(FRAME_COUNT>STAR_STOP_SPAWN_FRAMECOUNT):
        return

    if FRAME_COUNT % STAR_MOVE_RATE != 0:
        return

    spawnStar = False
    starLikelyhood = min(STAR_BASE_LIKELYHOOD + (FRAME_COUNT*STAR_TIMER_LIKELYHOOD), STAR_MAX_LIKELYHOOD);
    starCount = len(stars.sprites())

    for starNr in range(MAX_STARS):
        randomDraw = random.random()
        spawnStar = randomDraw < starLikelyhood

        if starCount <= FORCE_STAR_SPAWN_MIN:
            #print("Force star spawn")
            spawnStar=True
            starCount += 1

        #print(f"likelyHood: {starLikelyhood}, draw: {randomDraw}, spawn: {spawnStar}")

        if spawnStar:
            spawnColumn = random.randint(0, GAME_COLUMNS-1);
            #print(f"Spawning at {spawnColumn}")
            Star(spawnColumn, stargroups)



def CloseMenu():
    global CURRENT_MENU, MENU_JUST_CLOSED
    CURRENT_MENU = False
    MENU_JUST_CLOSED = True


def QuitGame():
    global GAME_QUIT
    GAME_QUIT = True


def main(winstyle=0):
    # Initialize pygame
    if pg.get_sdl_version()[0] == 2:
        pg.mixer.pre_init(44100, 32, 2, 1024)
    pg.init()
    if pg.mixer and not pg.mixer.get_init():
        print("Warning, no sound")
        pg.mixer = None

    fullscreen = False
    # Set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    # Load images, assign to sprite classes
    # (do this before the classes are used, after screen setup)
    
    Player.images = [load_image(im) for im in ("goatL.png", "goatR.png", "goatLHorn.png", "goatRHorn.png", "goatLBody.png", "goatRBody.png", "goatLFullGlow.png", "goatRFullGlow.png")]
    img = load_image("star.png")
    Star.images = [img]

    ## decorate the game window
    # icon = pg.transform.scale(Alien.images[0], (32, 32))
    #pg.display.set_icon(icon)
    pg.display.set_caption("Pygame Star Catcher Goat")
    pg.mouse.set_visible(0)

    # create the background, tile the bgd image
    bgdtile = load_image("background.png")
    background = pg.Surface(SCREENRECT.size)
    for x in range(0, SCREENRECT.width, bgdtile.get_width()):
        background.blit(bgdtile, (x, 0))
    screen.blit(background, (0, 0))
    pg.display.flip()


    # Create Some Starting Values
    clock = pg.time.Clock()

    # Initialize Game Groups
    stars = pg.sprite.Group()
    gameButtons = pg.sprite.Group()    
    endButtons = pg.sprite.Group()

    gameSprites = pg.sprite.RenderUpdates()

    # initialize our starting sprites
    global CURRENT_MENU, vizRects, ledSegmentMap

    if GAME_COLUMNS == 3:
        vizRects = vizRects3
        ledSegmentMap = ledSegmentMap3
    else:
        vizRects = vizRects6
        ledSegmentMap = ledSegmentMap6

    player = Player(gameSprites)

    # right/left buttons
    ButtonIcon(810, 330, [load_image(im) for im in ("button_blue_left.png", "button_blue_left_pressed.png")], (gameButtons, gameSprites)).frame = 24 # offset button animations a bit
    ButtonIcon(860, 330, [load_image(im) for im in ("button_blue_right.png", "button_blue_right_pressed.png")], (gameButtons, gameSprites))
    ButtonIcon(780, 370, [load_image(im) for im in ("button_yellow.png", "button_yellow_pressed.png")], (gameButtons, gameSprites)).frame = 12

    ButtonIcon(750, 620, [load_image(im) for im in ("button_black_right.png", "button_black_right_pressed.png")], (endButtons, gameSprites)).frame = 24
    ButtonIcon(750, 670, [load_image(im) for im in ("button_black_left.png", "button_black_left_pressed.png")], (endButtons, gameSprites))

    leds = LedHandler();

    if pg.font:
        scoreText = UiText(gameSprites)
        scoreText.targetRect = Rect(905,445, 335, 50)
        scoreText.font = pg.font.Font(None, 56)
        scoreText.color = "#FFC000"
        scoreText.align = 0
        statText = UiText(gameSprites)
        statText.targetRect = Rect(739,515, 510, 50)
        statMissedText = UiText(gameSprites)
        statMissedText.targetRect = Rect(739,550, 510, 50)
        statMissedText.color = "grey"

    # Run our main loop whilst the player is alive.
    while player.alive() and not GAME_QUIT:
        if CURRENT_MENU:
            CURRENT_MENU.Loop()
        else:
            PlayLoop(player, scoreText, statText, statMissedText, leds, stars, gameButtons, endButtons, gameSprites, screen, background)
            global MENU_JUST_CLOSED
            MENU_JUST_CLOSED = False

        # cap the framerate at 10fps. Also called 10HZ or 10 times per second.
        clock.tick(FRAME_RATE)

    leds.SetAllStarsOff()
    leds.UpdateStars()

    if pg.mixer:
        pg.mixer.music.fadeout(1000)
    pg.time.wait(1000)

def ReRenderBackground(screen):
    if GAME_COLUMNS == 3:
        bgdtile = load_image("backgroundB.png")
    else:
        bgdtile = load_image("background.png")

    background = pg.Surface(SCREENRECT.size)
    for x in range(0, SCREENRECT.width, bgdtile.get_width()):
        background.blit(bgdtile, (x, 0))
    screen.blit(background, (0, 0))


def PlayLoop(player, scoreText, statText, statMissedText, leds, stars, gameButtons, endButtons, gameSprites, screen, background):
    global FRAME_COUNT
    FRAME_COUNT += 1

    def Reset6():
        CloseMenu()
        reset(6, player, stars, screen, leds)

    def Reset3():
        CloseMenu()
        reset(3, player, stars, screen, leds)

    
    # get input
    for event in pg.event.get():
        if event.type == pg.QUIT:
            # exit game loop and shut down leds
            player.kill()
            return
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            global CURRENT_MENU
            CURRENT_MENU = MenuScreen(screen, {"Zurück zum Spiel": CloseMenu, "Spiel neustarten (Normal)": Reset6, "Spiel neustarten (Einfach)": Reset3, "Spiel Beenden": QuitGame})
            return
        if event.type == pg.KEYDOWN and event.key == pg.K_PAGEUP:
            Reset6()
            return
        if event.type == pg.KEYDOWN and event.key == pg.K_PAGEDOWN:
            Reset3()
            return
        if event.type == pg.KEYDOWN and event.key == pg.K_RIGHT:
            player.move(1)
        if event.type == pg.KEYDOWN and event.key == pg.K_LEFT:
            player.move(-1)
        if event.type == pg.KEYDOWN and event.key == pg.K_UP:
            player.jump([star for star in stars if star.hangingLow])

    keystate = pg.key.get_pressed()

    # update score text:
    punkte = max(((player.starsCatchedHorn*10)+player.starsCatchedButt-GAME_StarsMissed),0)
    scoreText.text = f"{punkte}"

    if GAME_COLUMNS == 3:
        statText.text = f"Gefangen: {player.starsCatchedHorn}"
    else:
        statText.text = f"Gefangen: (Horn/Total): {player.starsCatchedHorn}/{player.starsCatchedHorn+player.starsCatchedButt}"

    statMissedText.text = f"Verpasst: {GAME_StarsMissed}"


    if (FRAME_COUNT == 1) or (FRAME_COUNT == GAME_END_FRAMECOUNT):
        for button in gameButtons:
            button.paused = FRAME_COUNT != 1
        for button in endButtons:
            button.paused = FRAME_COUNT != GAME_END_FRAMECOUNT


    # re-draw whole background
    if MENU_JUST_CLOSED:
        ReRenderBackground(screen)
       
    # clear/erase the last drawn sprites
    gameSprites.clear(screen, background)
    
    leds.SetAllStarsOff()

    # make stars land on player before update
    for star in stars:
        if star.hangingLow:
            star.land(player)

    # update all the sprites
    gameSprites.update()

    for star in stars:
        leds.SetStarLed(star.gridPosY, star.gridPosX, STAR_BRIGHTNESS)

    # handle player input
    #direction = keystate[pg.K_RIGHT] - keystate[pg.K_LEFT]
    #player.move(direction)
    #jumping = keystate[pg.K_UP]
    #player.jumping = jumping
    
    # draw the scene
    if MENU_JUST_CLOSED:
        pg.display.flip()
    
    dirty = gameSprites.draw(screen)
    pg.display.update(dirty)

    spawnNewStarRow(stars, (stars, gameSprites))

    leds.UpdateStars()

    #print(f"starsCatchedHorn: {player.starsCatchedHorn}, starsCatchedButt:  {player.starsCatchedButt}, starsMissed: {GAME_StarsMissed}");



# call the "main" function if running this script
if __name__ == "__main__":
    main()
    pg.quit()