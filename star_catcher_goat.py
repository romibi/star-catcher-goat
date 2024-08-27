#!/usr/bin/env python

import os
import random
from typing import List
import pygame as pg
from pygame import Rect
import grequests
from enum import Enum
import threading
import time
import subprocess
import pickle

# see if we can load more than standard BMP
if not pg.image.get_extended():
    raise SystemExit("Sorry, extended image module required")

# Try to get the game version for versioning REPLAY data in future
CURRENT_GAME_VERSION = "(unknown)"

def get_git_revision_hash() -> str:
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()

try:
    CURRENT_GAME_VERSION = get_git_revision_hash()
except:
    pass

print(f"Running game version {CURRENT_GAME_VERSION}")

HUB_ADDR_STAR_1 = '192.168.1.107'
HUB_ADDR_STAR_2 = ''
HUB_ADDR_STAR_3 = ''
HUB_ADDR_STAR_4 = ''
HUB_ADDR_STAR_5 = ''
HUB_ADDR_STAR_6 = ''

main_dir = os.path.split(os.path.abspath(__file__))[0]

class GameConfig():

    def __init__(self):
        self.reset()

    def reset(self):
        # difficulty settings
        self.STAR_BASE_LIKELYHOOD = 0.3 # at start 30% chance of 1 star. (15% for 2nd star)
        self.STAR_MAX_LIKELYHOOD = 0.95 # max chance of 95% for 1 star (47.5% for 2nd star)
        self.STAR_TIMER_LIKELYHOOD = 0.0005 # star spawn likely hood increase over time
        self.FORCE_STAR_SPAWN_MIN = 2 # if 2 or less stars 1 star spawns 100%
        self.MAX_STARS = 2 # max stars per row

        # speed
        self.FRAME_RATE = 10; # fps
        self.STAR_MOVE_RATE = 10; # stars move every x frames

        # game end
        self.STAR_STOP_SPAWN_FRAMECOUNT = 1120; # no more stars after 112 seconds
        self.END_FRAMECOUNT = 1200; # stop game loop after 120 seconds

        # how many stars? 3x6 or 6x6
        self.ROWS = 6;
        self.COLUMNS = 6; # code works with 3 or 6 columns


class GameVisualizationConfig():
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

    vizRects = None # initialized in setup/reset


class GameState():
    SCREENRECT = pg.Rect(0, 0, 1280, 720)

    CURRENT_MENU = None
    MENU_JUST_CLOSED = False
    GAME_QUIT = False

    REPLAY = False

    FRAME_COUNT = 0
    StarsMissed = 0


GAME_CONFIG = GameConfig()
GAME_STATE = GameState()
GAME_VIZ_CONF = GameVisualizationConfig()

RECORDING = None

def InitRecording():
    """
    Remarks:
    - lowercase values are important for replay
    - UPPER_CASE_VALUES are unlikely to change often between recordings (dependent on game version)
    - rows is unlikely to change as well but lowercase because columns is also lowercase
    - columns can currently either be 3 or 6
    """
    global RECORDING
    RECORDING = {
                    "seed": None,
                    "movements": [],
                    "gamever": CURRENT_GAME_VERSION
                }
    RECORDING["difficulty"] =   {
                                    "STAR_BASE_LIKELYHOOD": GAME_CONFIG.STAR_BASE_LIKELYHOOD,
                                    "STAR_MAX_LIKELYHOOD": GAME_CONFIG.STAR_MAX_LIKELYHOOD,
                                    "STAR_TIMER_LIKELYHOOD": GAME_CONFIG.STAR_TIMER_LIKELYHOOD,
                                    "FORCE_STAR_SPAWN_MIN": GAME_CONFIG.FORCE_STAR_SPAWN_MIN,
                                    "MAX_STARS": GAME_CONFIG.MAX_STARS
                                }
    RECORDING["settings"] = {
                                "FRAME_RATE": GAME_CONFIG.FRAME_RATE,
                                "STAR_MOVE_RATE": GAME_CONFIG.STAR_MOVE_RATE,
                                "STAR_STOP_SPAWN_FRAMECOUNT": GAME_CONFIG.STAR_STOP_SPAWN_FRAMECOUNT,
                                "END_FRAMECOUNT": GAME_CONFIG.END_FRAMECOUNT,
                                "columns": GAME_CONFIG.COLUMNS,
                                "rows": GAME_CONFIG.ROWS
                            }
    RECORDING["seed"] = time.time()

InitRecording()

def ApplyRecordingSettings():
    if "difficulty" in RECORDING:
        difficulty = RECORDING["difficulty"]
        if "STAR_BASE_LIKELYHOOD" in difficulty: GAME_CONFIG.STAR_BASE_LIKELYHOOD = difficulty["STAR_BASE_LIKELYHOOD"]
        if "STAR_MAX_LIKELYHOOD" in difficulty: GAME_CONFIG.STAR_MAX_LIKELYHOOD = difficulty["STAR_MAX_LIKELYHOOD"]
        if "STAR_TIMER_LIKELYHOOD" in difficulty: GAME_CONFIG.STAR_TIMER_LIKELYHOOD = difficulty["STAR_TIMER_LIKELYHOOD"]
        if "FORCE_STAR_SPAWN_MIN" in difficulty: GAME_CONFIG.FORCE_STAR_SPAWN_MIN = difficulty["FORCE_STAR_SPAWN_MIN"]
        if "MAX_STARS" in difficulty: GAME_CONFIG.MAX_STARS = difficulty["MAX_STARS"]
    if "settings" in RECORDING:
        settings = RECORDING["settings"]
        if "FRAME_RATE" in settings: GAME_CONFIG.FRAME_RATE = settings["FRAME_RATE"]
        if "STAR_MOVE_RATE" in settings: GAME_CONFIG.STAR_MOVE_RATE = settings["STAR_MOVE_RATE"]
        if "STAR_STOP_SPAWN_FRAMECOUNT" in settings: GAME_CONFIG.STAR_STOP_SPAWN_FRAMECOUNT = settings["STAR_STOP_SPAWN_FRAMECOUNT"]
        if "END_FRAMECOUNT" in settings: GAME_CONFIG.END_FRAMECOUNT = settings["END_FRAMECOUNT"]
        if "rows" in settings: GAME_CONFIG.ROWS = settings["rows"]
        if "columns" in settings:
            GAME_CONFIG.COLUMNS = settings["columns"]
        elif "columns" in RECORDING:
            GAME_CONFIG.COLUMNS = RECORDING["columns"] # very first few recordings had columns directly in main dict


def save_recording(points=None):
    try:
        filedate = time.strftime("%Y%m%d-%H%M%S")
        gameMode = ""
        if RECORDING["settings"]["columns"] == 3:
            gameMode = "_easy"
        filename = os.path.join(main_dir, "recordings", f"recording_{filedate}{gameMode}.pickle")
        if points:
            filename = os.path.join(main_dir, "recordings", f"recording_{filedate}{gameMode}_{points}.pickle")

        filename_last = os.path.join(main_dir, "recordings", f"recording_last{gameMode}.pickle")

        with open(filename_last, "wb") as f:
            pickle.dump(RECORDING, f, protocol=pickle.HIGHEST_PROTOCOL)
            print(f"Saved {filename_last}")

        with open(filename, "wb") as f:
            pickle.dump(RECORDING, f, protocol=pickle.HIGHEST_PROTOCOL)
            print(f"Saved {filename}")
    except exception as ex:
        print("Error during pickling object (Possibly unsupported):", ex)

def load_last_recording():
    global RECORDING
    try:
        gameMode = ""
        if GAME_CONFIG.COLUMNS == 3:
            gameMode = "_easy"

        filename = os.path.join(main_dir, "recordings", f"recording_last{gameMode}.pickle")

        with open(filename, "rb") as f:
            RECORDING = pickle.load(f)
            print(f"Loaded {filename}")

        if RECORDING["gamever"] != CURRENT_GAME_VERSION:
            print("Warning: loaded game recording was recorded with a different version! Replay might differ!")
    except exception as ex:
        print("Error during pickling object (Possibly unsupported):", ex)


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


class LedHandler():
    STAR_COLOR = 'FF9000'
    BRIGHTNESS_MOD = 0 # modifying 0=ALL, 1=A, 2=B, 3=G
    STAR_BRIGHTNESS_A = 255 # row 0-2
    STAR_BRIGHTNESS_B = 255 # row 3-5
    GOAT_BRIGHTNESS = 255

    # change color of segment 1 (0) to green: http://192.168.1.107/win&SM=0&SB=255&CL=H00FF00
    API_ADDR = '/win'
    API_ARG_SEGMENT = '&SM='
    API_ARG_BRIGHTNES = '&SB='
    API_ARG_COLOR = '&CL=H'


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

    ledSegmentMap = None # initialized in setup/reset

    hubs = {}
    stars = {}
    leds = {}

    def __init__(self):
        self.active = -1 # 0: no, 1: yes, -1: active unless first request fails
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

        for row in range(GAME_CONFIG.ROWS):
            self.stars[row] = {}
            self.leds[row] = {}
            for column in range(GAME_CONFIG.COLUMNS):
                self.stars[row][column] = {}
                self.leds[row][column] = {}



    def AddStarHub(self, num, address):
        self.hubs[num] = address


    def GetStarHub(self, row, column):
        if self.ledSegmentMap:
            segment = self.ledSegmentMap[row][column]
            hub = segment["hub"]
            return self.hubs.get(hub, None)
        return ''


    def GetLedApiUrl(self, row, column, bright, color):
        hub = self.GetStarHub(row, column);
        if not hub:
            return None;
  
        segment = self.ledSegmentMap[row][column];

        return f'http://{hub}{self.API_ADDR}{self.API_ARG_SEGMENT}{segment["segment"]}{self.API_ARG_BRIGHTNES}{bright}{self.API_ARG_COLOR}{color}'


    def SetStarLed(self, row, column, bright, color=None):
        self.stars[row][column]['bright'] = bright
        if not 'color' in self.stars[row][column]:
            self.stars[row][column]['color'] = self.STAR_COLOR
        if color:
            self.stars[row][column]['color'] = color


    def SetAllLedsOff(self):
        for row, starRow in self.stars.items():
            for column, star in starRow.items():
                self.SetStarLed(row, column, 0)


    def UpdateBrightness(self, newBrightnessA, newBrightnessB, newBrightnessG):
        for row, starRow in self.stars.items():
            for column, star in starRow.items():
                if star.get('bright', 0) > 0:
                    if row > 2:
                        star['bright'] = newBrightnessB
                    else:
                        star['bright'] = newBrightnessA


    def UpdateLeds(self):
        urls = []
        for row, starRow in self.stars.items():
            for column, star in starRow.items():
                led = self.leds[row][column]

                starBrigth = star.get('bright', 0)
                ledBrigth = led.get('bright', None)

                starColor = star.get('color', self.STAR_COLOR)
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
        
        rs = (grequests.get(u, timeout=5) for u in urls)

        def call_map(rs, exception_handler):
            grequests.map(rs, exception_handler=exception_handler)

        if self.active == 0:
            return
        elif self.active == -1:
            self.active = 1
            def exception_handler(request, exception):
                self.active = 0            
            threading.Thread(target=call_map, args=(rs,exception_handler)).start()
        else:
            threading.Thread(target=call_map, args=(rs,None)).start()


def ResetGame(newColumns, player, stars, screen, leds, clear_recording=True):
    # Shutdown LEDS
    leds.SetAllLedsOff()
    leds.UpdateLeds()

    GAME_CONFIG.reset() # restore default values (in case recording replay manipulated them)
    GAME_CONFIG.COLUMNS = newColumns

    if GAME_CONFIG.COLUMNS == 3:
        GAME_VIZ_CONF.vizRects = GAME_VIZ_CONF.vizRects3
        leds.ledSegmentMap = leds.ledSegmentMap3
    else:
        GAME_VIZ_CONF.vizRects = GAME_VIZ_CONF.vizRects6
        leds.ledSegmentMap = leds.ledSegmentMap6

    leds.reset()
    player.reset()
    GAME_STATE.StarsMissed = 0

    for star in stars:
        star.kill()

    ReRenderBackground(screen)
    pg.display.flip()

    if clear_recording:
        InitRecording()
        random.seed(RECORDING["seed"])

    GAME_STATE.REPLAY = False
    GAME_STATE.FRAME_COUNT = 0


def replay(recording, player, stars, screen, leds):
    global RECORDING
    #print(f"Replaying {recording}")
    RECORDING = recording
    ApplyRecordingSettings()

    ResetGame(GAME_CONFIG.COLUMNS, player, stars, screen, leds, False)
    GAME_STATE.REPLAY = True
    random.seed(RECORDING["seed"])


class Star(pg.sprite.Sprite):

    gridPosX = 0
    gridPosY = 0
    images: List[pg.Surface] = []


    def __init__(self, column, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.image = self.images[0]
        self.gridPosX = column
        self.gridPosY = -1
        self.rect = GAME_VIZ_CONF.vizRects[self.gridPosY+1][self.gridPosX]
        self.facing = 0
        self.frame = 0

    @property
    def hangingLow(self):
        return self.gridPosY>=(GAME_CONFIG.ROWS-1)

    def fall(self):
        self.gridPosY += 1
        if self.gridPosY < GAME_CONFIG.ROWS:
            self.rect = GAME_VIZ_CONF.vizRects[self.gridPosY][self.gridPosX]
        else:
            self.land()


    def land(self, player=None):
        if self.frame % GAME_CONFIG.STAR_MOVE_RATE != 0:
            return

        catched = False
        if not player == None:
            catched = player.CatchStarPassive(self)
        if not catched:
            GAME_STATE.StarsMissed += 1
        self.kill()


    def update(self, *args, **kwargs):
        #self.rect.move_ip(self.facing, 1)
        if self.frame % GAME_CONFIG.STAR_MOVE_RATE == 0:
            self.fall()

        if not GAME_STATE.SCREENRECT.contains(self.rect):
            self.facing = -self.facing
            self.rect.top = self.rect.bottom + 1
            self.rect = self.rect.clamp(GAME_STATE.SCREENRECT)
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
        self.rect = GAME_VIZ_CONF.vizGoatRects[int(self.gridPos*2)+max(self.facing,0)]

    def moveInGrid(self):        
        maxGoatPos = round(GAME_CONFIG.COLUMNS/2)-1
        if GAME_CONFIG.COLUMNS == 3:
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

        if (not turned) or (GAME_CONFIG.COLUMNS == 3):
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
        if GAME_CONFIG.COLUMNS == 3:
            return self.gridPos
        return self.gridPos * 2 + max(self.facing,0)


    @property
    def ButtColumn(self):
        if GAME_CONFIG.COLUMNS == 3:
            return -1 # no butt column
        return self.gridPos*2 + (1-max(self.facing,0))


    def jump(self, stars):
        for star in stars:
            if star.gridPosX == self.HornColumn:
                self.starsCatchedHorn += 1
                self.HornGlow()
                #print(f"Catching Star: x:{star.gridPosX} y:{star.gridPosX}")
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
        self.textFunc = None
        self.targetRect = Rect(0,0,0,0)
        self.align = -1 # -1 left, 0 center, 1 right
        self.update()
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
            if type(menuEntry) == str:
                entry.text = menuEntry
            elif callable(menuEntry):
                entry.textFunc = menuEntry
            entry.targetRect = Rect(100, nextPos, 300, 300)
            nextPos += 50

        self.frame = -1

        overlayBg = pg.Surface(GAME_STATE.SCREENRECT.size, pg.SRCALPHA,32)
        overlayBg.fill((0,0,0, 150))
        self.background.blit(overlayBg, (0, 0))


    def Loop(self):
        self.frame += 1
        for event in pg.event.get():
            if event.type == pg.QUIT:
                GAME_STATE.GAME_QUIT = True
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                CloseMenu(event.key)
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_DOWN:
                self.cursorIndex = min(self.cursorIndex+1, len(self.menuOptionMap.keys())-1)
                self.cursor.targetRect = Rect(50, 100+(self.cursorIndex*50), 64, 64)
            if event.type == pg.KEYDOWN and event.key == pg.K_UP:
                self.cursorIndex = max(self.cursorIndex-1, 0)
                self.cursor.targetRect = Rect(50, 100+(self.cursorIndex*50), 64, 64)
            if event.type == pg.KEYDOWN and event.key in [pg.K_RETURN, pg.K_LEFT, pg.K_RIGHT]:
                menuFuncs = list(self.menuOptionMap.values())
                menuFuncs[self.cursorIndex](event.key)

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
    if(GAME_STATE.FRAME_COUNT>GAME_CONFIG.STAR_STOP_SPAWN_FRAMECOUNT):
        return

    if GAME_STATE.FRAME_COUNT % GAME_CONFIG.STAR_MOVE_RATE != 0:
        return

    spawnStar = False
    starLikelyhood = min(GAME_CONFIG.STAR_BASE_LIKELYHOOD + (GAME_STATE.FRAME_COUNT*GAME_CONFIG.STAR_TIMER_LIKELYHOOD), GAME_CONFIG.STAR_MAX_LIKELYHOOD);
    starCount = len(stars.sprites())

    for starNr in range(GAME_CONFIG.MAX_STARS):
        randomDraw = random.random()
        spawnStar = randomDraw < starLikelyhood

        if starCount <= GAME_CONFIG.FORCE_STAR_SPAWN_MIN:
            #print("Force star spawn")
            spawnStar=True
            starCount += 1

        #print(f"FRAME: {FRAME_COUNT}: likelyHood: {starLikelyhood}, draw: {randomDraw}, spawn: {spawnStar}")

        if spawnStar:
            spawnColumn = random.randint(0, GAME_CONFIG.COLUMNS-1);
            #print(f"Spawning at {spawnColumn}")
            Star(spawnColumn, stargroups)



def CloseMenu(key):
    GAME_STATE.CURRENT_MENU = False
    GAME_STATE.MENU_JUST_CLOSED = True


def QuitGame(key):
    GAME_STATE.GAME_QUIT = True


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
    bestdepth = pg.display.mode_ok(GAME_STATE.SCREENRECT.size, winstyle, 32)
    screen = pg.display.set_mode(GAME_STATE.SCREENRECT.size, winstyle, bestdepth)

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
    background = pg.Surface(GAME_STATE.SCREENRECT.size)
    for x in range(0, GAME_STATE.SCREENRECT.width, bgdtile.get_width()):
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

    # reset before first loop to have same random starting condition as in replay
    ResetGame(6, player, stars, screen, leds)

    # Run our main loop whilst the player is alive.
    while player.alive() and not GAME_STATE.GAME_QUIT:
        if GAME_STATE.CURRENT_MENU:
            GAME_STATE.CURRENT_MENU.Loop()
        else:
            # todo: move scoreText, statText, statMissedText, gameButtons, endButtons and background to some GUI class/object contained in GAME_STATE
            # todo: move player, stars, leds,, gameSpprites, screen and background to GAME_STATE
            PlayLoop(player, scoreText, statText, statMissedText, leds, stars, gameButtons, endButtons, gameSprites, screen, background)
            GAME_STATE.MENU_JUST_CLOSED = False

        # cap the framerate at 10fps. Also called 10HZ or 10 times per second.
        clock.tick(GAME_CONFIG.FRAME_RATE)

    leds.SetAllLedsOff()
    leds.UpdateLeds()

    if pg.mixer:
        # todo: really add music and maybe some sample trigger commands to controller
        pg.mixer.music.fadeout(1000)
    pg.time.wait(1000)

def ReRenderBackground(screen):
    if GAME_CONFIG.COLUMNS == 3:
        bgdtile = load_image("backgroundB.png")
    else:
        bgdtile = load_image("background.png")

    background = pg.Surface(GAME_STATE.SCREENRECT.size)
    for x in range(0, GAME_STATE.SCREENRECT.width, bgdtile.get_width()):
        background.blit(bgdtile, (x, 0))
    screen.blit(background, (0, 0))


def PlayLoop(player, scoreText, statText, statMissedText, leds, stars, gameButtons, endButtons, gameSprites, screen, background):
    GAME_STATE.FRAME_COUNT += 1

    # todo: move menu definition outside play loop
    def Reset6(key):
        CloseMenu(key)
        ResetGame(6, player, stars, screen, leds)

    def Reset3(key):
        CloseMenu(key)
        ResetGame(3, player, stars, screen, leds)

    def LedText():
        if leds.active == 1:
            return "LED Ein/Aus: EIN"
        else:
            return "LED Ein/Aus: AUS"

    def ToggleLedActive(key):
        if leds.active == 1:
            leds.SetAllLedsOff()
            leds.UpdateLeds()
            leds.active = 0
        else:
            leds.active = 1

    def LedBrightText():
        if (leds.BRIGHTNESS_MOD != 0) or (leds.STAR_BRIGHTNESS_A != leds.STAR_BRIGHTNESS_B) or (leds.STAR_BRIGHTNESS_A != leds.GOAT_BRIGHTNESS) or (leds.STAR_BRIGHTNESS_B != leds.GOAT_BRIGHTNESS):
            if leds.BRIGHTNESS_MOD == 0:
                return f"LED Helligkeit: [{leds.STAR_BRIGHTNESS_A}|{leds.STAR_BRIGHTNESS_B}|{leds.GOAT_BRIGHTNESS}]"
            elif leds.BRIGHTNESS_MOD == 1:
                return f"LED Helligkeit: [{leds.STAR_BRIGHTNESS_A}]|{leds.STAR_BRIGHTNESS_B}|{leds.GOAT_BRIGHTNESS}"
            elif leds.BRIGHTNESS_MOD == 2:
                return f"LED Helligkeit: {leds.STAR_BRIGHTNESS_A}|[{leds.STAR_BRIGHTNESS_B}]|{leds.GOAT_BRIGHTNESS}"
            elif leds.BRIGHTNESS_MOD == 3:
                return f"LED Helligkeit: {leds.STAR_BRIGHTNESS_A}|{leds.STAR_BRIGHTNESS_B}|[{leds.GOAT_BRIGHTNESS}]"
        else:
            return f"LED Helligkeit: {leds.STAR_BRIGHTNESS_A}"

    def LedBright(key):
        modifiers = pg.key.get_mods()

        if (key == pg.K_RETURN) and (modifiers & pg.KMOD_LSHIFT):
            leds.BRIGHTNESS_MOD += 1
            if leds.BRIGHTNESS_MOD>3:
                leds.BRIGHTNESS_MOD = 0
            return

        modVal = 10
        if modifiers & pg.KMOD_LSHIFT:
            modVal = 1
        elif modifiers & pg.KMOD_LCTRL:
            modVal = 50

        if key == pg.K_LEFT:
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 1:
                leds.STAR_BRIGHTNESS_A = max(leds.STAR_BRIGHTNESS_A-modVal, 1)
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 2:
                leds.STAR_BRIGHTNESS_B = max(leds.STAR_BRIGHTNESS_B-modVal, 1)
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 3:
                leds.GOAT_BRIGHTNESS = max(leds.GOAT_BRIGHTNESS-modVal, 1)
        if key == pg.K_RIGHT:
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 1:
                leds.STAR_BRIGHTNESS_A = min(leds.STAR_BRIGHTNESS_A+modVal, 255)
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 2:
                leds.STAR_BRIGHTNESS_B = min(leds.STAR_BRIGHTNESS_B+modVal, 255)
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 3:
                leds.GOAT_BRIGHTNESS = min(leds.GOAT_BRIGHTNESS+modVal, 255)
        if key == pg.K_RETURN:
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 1:
                if leds.STAR_BRIGHTNESS_A > 255/2:
                    newBright = 10
                else:
                    newBright = 255
            if leds.BRIGHTNESS_MOD == 2:
                if leds.STAR_BRIGHTNESS_B > 255/2:
                    newBright = 10
                else:
                    newBright = 255
            if leds.BRIGHTNESS_MOD == 3:                
                if leds.GOAT_BRIGHTNESS > 255/2:
                    newBright = 10
                else:
                    newBright = 255            

            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 1:
                leds.STAR_BRIGHTNESS_A = newBright
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 2:
                leds.STAR_BRIGHTNESS_B = newBright
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 3:
                leds.GOAT_BRIGHTNESS = newBright            
        leds.UpdateBrightness(leds.STAR_BRIGHTNESS_A, leds.STAR_BRIGHTNESS_B, leds.GOAT_BRIGHTNESS)
        leds.UpdateLeds()


    # get input
    for event in pg.event.get():
        if event.type == pg.QUIT:
            # exit game loop and shut down leds
            player.kill()
            return
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            GAME_STATE.CURRENT_MENU = MenuScreen(screen, {"Zurück zum Spiel": CloseMenu, LedText: ToggleLedActive, LedBrightText: LedBright, "Neues Spiel (Normal)": Reset6, "Neues Spiel (Einfach)": Reset3, "Spiel Beenden": QuitGame})
            return
        if event.type == pg.KEYDOWN and event.key == pg.K_PAGEUP:
            Reset6(event.key)
            return
        if event.type == pg.KEYDOWN and event.key == pg.K_PAGEDOWN:
            Reset3(event.key)
            return
        if event.type == pg.KEYDOWN and event.key == pg.K_RIGHT:
            if not GAME_STATE.REPLAY:
                RECORDING["movements"].append({"frame": GAME_STATE.FRAME_COUNT, "key": event.key});
                player.move(1)
        if event.type == pg.KEYDOWN and event.key == pg.K_LEFT:
            if not GAME_STATE.REPLAY:
                RECORDING["movements"].append({"frame": GAME_STATE.FRAME_COUNT, "key": event.key});
                player.move(-1)
        if event.type == pg.KEYDOWN and event.key == pg.K_UP:
            if not GAME_STATE.REPLAY:
                RECORDING["movements"].append({"frame": GAME_STATE.FRAME_COUNT, "key": event.key});
                player.jump([star for star in stars if star.hangingLow])
        if event.type == pg.KEYDOWN and ((event.key == pg.K_F7) or (event.key == pg.K_F10)):
            load_last_recording()
            replay(RECORDING, player, stars, screen, leds)
            return
        if event.type == pg.KEYDOWN and ((event.key == pg.K_F8) or (event.key == pg.K_F11)):
            replay(RECORDING, player, stars, screen, leds)
            return

    if GAME_STATE.REPLAY:
        for movement in RECORDING["movements"]:
            if movement["frame"] > GAME_STATE.FRAME_COUNT:
                break
            if movement["frame"] == GAME_STATE.FRAME_COUNT:
                if movement["key"] == pg.K_RIGHT:
                    player.move(1)
                if movement["key"] == pg.K_LEFT:
                    player.move(-1)
                if movement["key"] == pg.K_UP:
                    player.jump([star for star in stars if star.hangingLow])

    keystate = pg.key.get_pressed()

    # update score text:
    punkte = max(((player.starsCatchedHorn*10)+player.starsCatchedButt-GAME_STATE.StarsMissed),0)
    scoreText.text = f"{punkte}"

    if GAME_CONFIG.COLUMNS == 3:
        statText.text = f"Gefangen: {player.starsCatchedHorn}"
    else:
        statText.text = f"Gefangen: (Horn/Total): {player.starsCatchedHorn}/{player.starsCatchedHorn+player.starsCatchedButt}"

    statMissedText.text = f"Verpasst: {GAME_STATE.StarsMissed}"


    if (GAME_STATE.FRAME_COUNT == 1) or (GAME_STATE.FRAME_COUNT == GAME_CONFIG.END_FRAMECOUNT):
        for button in gameButtons:
            button.paused = GAME_STATE.FRAME_COUNT != 1
        for button in endButtons:
            button.paused = GAME_STATE.FRAME_COUNT != GAME_CONFIG.END_FRAMECOUNT

    if (GAME_STATE.FRAME_COUNT == GAME_CONFIG.END_FRAMECOUNT) and (not GAME_STATE.REPLAY):
        # todo: Add Hi-Score Name enter screen and Hi-Score list
        save_recording(punkte)

    # re-draw whole background
    if GAME_STATE.MENU_JUST_CLOSED:
        ReRenderBackground(screen)
       
    # clear/erase the last drawn sprites
    gameSprites.clear(screen, background)
    
    leds.SetAllLedsOff()

    # make stars land on player before update
    for star in stars:
        if star.hangingLow:
            star.land(player)

    # update all the sprites
    gameSprites.update()

    for star in stars:
        bright = leds.STAR_BRIGHTNESS_A
        if star.gridPosY > 2:
            bright = leds.STAR_BRIGHTNESS_B
        leds.SetStarLed(star.gridPosY, star.gridPosX, bright)

    # handle player input
    #direction = keystate[pg.K_RIGHT] - keystate[pg.K_LEFT]
    #player.move(direction)
    #jumping = keystate[pg.K_UP]
    #player.jumping = jumping
    
    # draw the scene
    if GAME_STATE.MENU_JUST_CLOSED:
        pg.display.flip()
    
    dirty = gameSprites.draw(screen)
    pg.display.update(dirty)

    spawnNewStarRow(stars, (stars, gameSprites))

    leds.UpdateLeds()

    #print(f"starsCatchedHorn: {player.starsCatchedHorn}, starsCatchedButt:  {player.starsCatchedButt}, starsMissed: {GAME_STATE.StarsMissed}");



# call the "main" function if running this script
if __name__ == "__main__":
    main()
    pg.quit()