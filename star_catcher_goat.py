#!/usr/bin/env python

import os
import random
from typing import List
import pygame as pg
from pygame import Rect
from enum import Enum
import time
import subprocess
import pickle
import serial

from config.gameconfig import GameConfig
from config.gamevisualizationconfig import GameVisualizationConfig
from config.buttonconfig import *

from gamelib.gamestate import GameState
from gamelib.ledhandler import LedHandler
from gamelib.entities.star import Star
from gamelib.entities.player import Player

from gamelib.menus.menufactory import MenuFactory
from gamelib.menus.menuscreen import MenuScreen
from gamelib.uielements import *

# see if we can load more than standard BMP
if not pg.image.get_extended():
    raise SystemExit("Sorry, extended image module required")

# Try to get the game version for versioning REPLAY data in future
CURRENT_GAME_VERSION = "(unknown)"

def get_git_revision_hash() -> str:
    currdir = os.path.dirname(os.path.realpath(__file__))
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=currdir).decode('ascii').strip()

try:
    CURRENT_GAME_VERSION = get_git_revision_hash()
except:
    pass

print(f"Running game version {CURRENT_GAME_VERSION}")

main_dir = os.path.split(os.path.abspath(__file__))[0]

GAME_CONFIG = GameConfig()
GAME_VIZ_CONF = GameVisualizationConfig()
GAME_STATE = GameState(GAME_CONFIG, GAME_VIZ_CONF)

MENU_FACTORY = None

RECORDING = None

#### RECORDING STUFF #########################################################
# todo: move recording logic out of this file
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
    except Exception as ex:
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
    except Exception as ex:
        print("Error during pickling object (Possibly unsupported):", ex)


def replay(recording):
    global RECORDING
    
    GAME_STATE.reset(RECORDING["settings"]["columns"])

    RECORDING = recording
    ApplyRecordingSettings()

    GAME_STATE.REPLAY = True
    random.seed(RECORDING["seed"])

#### END RECORDING STUFF #########################################################


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
            Star(GAME_STATE, spawnColumn, stargroups)


def triggerControllerSound(name):
    if GAME_STATE.CONTROLLER_COM:
        GAME_STATE.CONTROLLER_COM.write(bytes(f"play {name}", 'utf-8'))
        GAME_STATE.CONTROLLER_COM.flush()

def GetButtonsFromSerial():
    result = []
    if not GAME_STATE.CONTROLLER_COM:
        return result

    lastLine = ""

    bytesToRead =  GAME_STATE.CONTROLLER_COM.inWaiting()
    data =  GAME_STATE.CONTROLLER_COM.read(bytesToRead)
    lines = data.decode("utf-8").splitlines()

    for line in lines:
        print(f"Serial: {line}")
        if line.startswith("BUTTONS:"):
            lastLine = line
        if line == "":
            break

    if lastLine != "":
        lastLine = lastLine.replace("BUTTONS:", "")
        for char in lastLine:
            match char:
                case "R":
                    result += [SERIAL_BUTTON_R]
                case "Y":
                    result += [SERIAL_BUTTON_Y]
                case "S":
                    result += [SERIAL_BUTTON_START]
                case "s":
                    result += [SERIAL_BUTTON_SELECT]
                case "u":
                    result += [SERIAL_BUTTON_UP]
                case "d":
                    result += [SERIAL_BUTTON_DOWN]
                case "l":
                    result += [SERIAL_BUTTON_LEFT]
                case "r":
                    result += [SERIAL_BUTTON_RIGHT]
    return result


def DoOnResetGame():
    ReRenderBackground()
    pg.display.flip()

    InitRecording()
    random.seed(RECORDING["seed"])


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
    GAME_STATE.GAME_SCREEN = screen
    GAME_STATE.OnResetGame = DoOnResetGame

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
    GAME_STATE.GAME_BACKGROUND = background
    for x in range(0, GAME_STATE.SCREENRECT.width, bgdtile.get_width()):
        background.blit(bgdtile, (x, 0))
    screen.blit(background, (0, 0))
    pg.display.flip()


    # Create Some Starting Values
    clock = pg.time.Clock()

    # Initialize Game Groups
    stars = GAME_STATE.STARS

    gameUiSprites = GAME_STATE.GAME_UI_SPRITES
    endUiSprites = GAME_STATE.END_UI_SPRITES

    gameSprites =  GAME_STATE.GAME_SPRITES

    # initialize our starting sprites
    GAME_STATE.PLAYER = Player(GAME_STATE, gameSprites)

    # right/left buttons
    ButtonIcon(810, 330, [load_image(im) for im in ("button_blue_left.png", "button_blue_left_pressed.png")], (gameUiSprites, gameSprites)).frame = 24 # offset button animations a bit
    ButtonIcon(860, 330, [load_image(im) for im in ("button_blue_right.png", "button_blue_right_pressed.png")], (gameUiSprites, gameSprites))
    ButtonIcon(780, 370, [load_image(im) for im in ("button_yellow.png", "button_yellow_pressed.png")], (gameUiSprites, gameSprites)).frame = 12

    ButtonIcon(750, 620, [load_image(im) for im in ("button_black_right.png", "button_black_right_pressed.png")], (endUiSprites, gameSprites)).frame = 24
    ButtonIcon(750, 670, [load_image(im) for im in ("button_black_left.png", "button_black_left_pressed.png")], (endUiSprites, gameSprites))

    leds = LedHandler(GAME_CONFIG)
    GAME_STATE.LED_HANDLER = leds

    global MENU_FACTORY
    MENU_FACTORY = MenuFactory(GAME_STATE)

    if pg.font:
        scoreText = UiText(gameSprites)
        scoreText.targetRect = Rect(905,445, 335, 50)
        scoreText.font = pg.font.Font(None, 56)
        scoreText.color = "#FFC000"
        scoreText.align = 0
        GAME_STATE.SCORE_POINTS = scoreText

        statText = UiText(gameSprites)
        statText.targetRect = Rect(739,515, 510, 50)
        GAME_STATE.SCORE_STATS = statText

        statMissedText = UiText(gameSprites)
        statMissedText.targetRect = Rect(739,550, 510, 50)
        statMissedText.color = "grey"
        GAME_STATE.SCORE_MISSED = statMissedText

    #try find controller com port
    ports = serial.tools.list_ports.comports()
    for port in ports:
      if port.description == 'Feather 32u4':
        GAME_STATE.CONTROLLER_COM_ADDR = port.device
        try:
            GAME_STATE.CONTROLLER_COM = serial.Serial(port=port.device, baudrate=9600, timeout=.1)
            GAME_STATE.CONTROLLER_COM.write(bytes(f"serial on", 'utf-8'))
            GAME_STATE.CONTROLLER_COM.flush()
        except:
            GAME_STATE.CONTROLLER_COM = None

    # reset before first loop to have same random starting condition as in replay
    GAME_STATE.reset(6)

    # Run our main loop whilst the player is alive.
    while GAME_STATE.PLAYER.alive() and not GAME_STATE.GAME_QUIT:
        # get currently pressed buttons on serial contrller
        serial_keys = GetButtonsFromSerial()
        next_key_list = serial_keys.copy() # copy for next frame

        # remove keys already pressed last time
        for key in GAME_STATE.LAST_SERIAL_BUTTONS:
            if key in serial_keys:
                serial_keys.remove(key)

        # set current list as pressed last time
        GAME_STATE.LAST_SERIAL_BUTTONS = next_key_list

        if GAME_STATE.CURRENT_MENU:
            GAME_STATE.CURRENT_MENU.Loop(serial_keys)
        else:
            PlayLoop(serial_keys)
            GAME_STATE.MENU_JUST_CLOSED = False

        # cap the framerate at 10fps. Also called 10HZ or 10 times per second.
        clock.tick(GAME_CONFIG.FRAME_RATE)

    leds.SetAllLedsOff()
    leds.UpdateLeds()

    if GAME_STATE.CONTROLLER_COM:
        # controller seems to get buggy on serial off ...
        #GAME_STATE.CONTROLLER_COM.write(bytes(f"serial off", 'utf-8'))
        #GAME_STATE.CONTROLLER_COM.flush()
        GAME_STATE.CONTROLLER_COM = None

    if pg.mixer:
        # todo: really add music and maybe some sample trigger commands to controller
        pg.mixer.music.fadeout(1000)
    pg.time.wait(1000)

def ReRenderBackground():
    if GAME_CONFIG.COLUMNS == 3:
        bgdtile = load_image("backgroundB.png")
    else:
        bgdtile = load_image("background.png")

    background = pg.Surface(GAME_STATE.SCREENRECT.size)
    for x in range(0, GAME_STATE.SCREENRECT.width, bgdtile.get_width()):
        background.blit(bgdtile, (x, 0))
    GAME_STATE.GAME_SCREEN.blit(background, (0, 0))


def PlayLoop(serial_keys):
    # load some Game state objects to local vars
    screen = GAME_STATE.GAME_SCREEN
    background = GAME_STATE.GAME_BACKGROUND

    player = GAME_STATE.PLAYER
    stars = GAME_STATE.STARS

    gameSprites =  GAME_STATE.GAME_SPRITES

    scoreText = GAME_STATE.SCORE_POINTS
    statText = GAME_STATE.SCORE_STATS
    statMissedText = GAME_STATE.SCORE_MISSED

    # increase frame count
    GAME_STATE.FRAME_COUNT += 1

    # get input
    def handleKey(key):
        if key in BUTTONS_MENU_OPEN:
            GAME_STATE.CURRENT_MENU = MENU_FACTORY.FullMenu()
            return True
        if key == pg.K_PAGEUP:
            GAME_STATE.reset(6)
            return True
        if key == pg.K_PAGEDOWN:
            GAME_STATE.reset(3)
            return True
        if key in BUTTONS_MOVE_RIGHT:
            if not GAME_STATE.REPLAY:
                RECORDING["movements"].append({"frame": GAME_STATE.FRAME_COUNT, "key": pg.K_RIGHT});
                player.move(1)
        if key in BUTTONS_MOVE_LEFT:
            if not GAME_STATE.REPLAY:
                RECORDING["movements"].append({"frame": GAME_STATE.FRAME_COUNT, "key": pg.K_LEFT});
                player.move(-1)
        if key in BUTTONS_JUMP:
            if not GAME_STATE.REPLAY:
                RECORDING["movements"].append({"frame": GAME_STATE.FRAME_COUNT, "key": pg.K_UP});
                player.jump([star for star in stars if star.hangingLow])
        if ((key == pg.K_F7) or (key == pg.K_F10)):
            load_last_recording()
            replay(RECORDING)
            return True
        if ((key == pg.K_F8) or (key == pg.K_F11)):
            replay(RECORDING)
            return True
        return False

    # handle input from OS
    for event in pg.event.get():
        if event.type == pg.QUIT:
            # exit game loop and shut down leds
            player.kill()
            return
        if event.type == pg.KEYDOWN:
            if handleKey(event.key):
                return        

    # handle input from serial
    for key in serial_keys:
        if handleKey(key):
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
        for sprite in GAME_STATE.GAME_UI_SPRITES:
            sprite.paused = GAME_STATE.FRAME_COUNT != 1
        for sprite in GAME_STATE.END_UI_SPRITES:
            sprite.paused = GAME_STATE.FRAME_COUNT != GAME_CONFIG.END_FRAMECOUNT

    if (GAME_STATE.FRAME_COUNT == GAME_CONFIG.END_FRAMECOUNT) and (not GAME_STATE.REPLAY):
        # todo: Add Hi-Score Name enter screen and Hi-Score list
        save_recording(punkte)
        if random.randint(0,10) > 7:
          triggerControllerSound("chest")
        else:
          triggerControllerSound("fanfare")

    # re-draw whole background
    if GAME_STATE.MENU_JUST_CLOSED:
        ReRenderBackground()
       
    # clear/erase the last drawn sprites
    gameSprites.clear(screen, background)
    
    leds = GAME_STATE.LED_HANDLER

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
