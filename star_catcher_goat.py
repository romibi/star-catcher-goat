#!/usr/bin/env python

import os
import random
import time
import subprocess
import pickle
from datetime import datetime
from fileinput import filename

import serial
import serial.tools.list_ports
from pygame import Color

from config.gameconfig import GameConfig, ScreenMode
from config.gamevisualizationconfig import GameVisualizationConfig
from config.buttonconfig import *
# todo: load_font is "unused" but used below??
from gamelib.data_helper_functions import load_image, load_font
from gamelib.gamepad_buttons import Gamepad_Buttons

from gamelib.gamestate import GameState
from gamelib.ledhandler import LedHandler
from gamelib.entities.star import Star
from gamelib.entities.player import Player

from gamelib.menus.menufactory import MenuFactory
from gamelib.uielements import *

# todo: fix warnings

# see if we can load more than standard BMP
if not pg.image.get_extended():
    raise SystemExit("Sorry, extended image module required")

# Try to get the game version for versioning REPLAY data in future
CURRENT_GAME_VERSION = "(unknown)"

def get_git_revision_hash() -> str:
    current_dir = os.path.dirname(os.path.realpath(__file__))
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=current_dir).decode('ascii').strip()

try:
    CURRENT_GAME_VERSION = get_git_revision_hash()
except: # noqa
    pass

print(f"Running game version {CURRENT_GAME_VERSION}")

main_dir = os.path.split(os.path.abspath(__file__))[0]

GAME_CONFIG = GameConfig()
GAME_VIZ_CONF = GameVisualizationConfig()
GAME_STATE = GameState(GAME_CONFIG, GAME_VIZ_CONF)

MENU_FACTORY: MenuFactory

RECORDING = {}

HIGHSCORES_NORMAL = []
HIGHSCORES_EASY = []

#### HISCORE STUFF ###########################################################
# todo: move highscore logic (and recordings) out of this file
def load_highscores(name):
    try:
        filename = os.path.join(main_dir, "recordings", name)

        with open(filename, "rb") as f:
            print(f"Loading {filename}")
            highscores = pickle.load(f)
            f.close()
            return highscores

    except Exception as ex:
        print("Error during pickling object (Possibly unsupported):", ex)
        return []

def load_all_highscores():
    global HIGHSCORES_NORMAL, HIGHSCORES_EASY
    HIGHSCORES_NORMAL = load_highscores("highscores.pickle")
    HIGHSCORES_EASY = load_highscores("highscores_easy.pickle")


def persist_highscores(name, highscores):
    try:
        filename = os.path.join(main_dir, "recordings", name)
        filename_bak = f"{filename}.bak"

        if os.path.exists(filename_bak):
            os.remove(filename_bak)
        if os.path.exists(filename):
            os.rename(filename, filename_bak)

        with open(filename, "wb") as f:
            # noinspection PyTypeChecker
            pickle.dump(highscores, f, protocol=pickle.HIGHEST_PROTOCOL)
            f.close()
            print(f"Saved {filename}")
    except Exception as ex:
        print("Error during pickling object (Possibly unsupported):", ex)

def persist_all_highscores():
    persist_highscores("highscores.pickle", HIGHSCORES_NORMAL)
    persist_highscores("highscores_easy.pickle", HIGHSCORES_EASY)


def add_highscore(points, name, mode, recording_filename):
    global HIGHSCORES_NORMAL, HIGHSCORES_EASY
    highscores = HIGHSCORES_NORMAL
    if mode == "easy":
        highscores = HIGHSCORES_EASY

    highscores += [{"points": points, "name": name, "timestamp":  datetime.now(), "recording_filename": recording_filename}]
    highscores.sort(key=lambda entry: entry["points"], reverse=True)

    if mode == "easy":
        HIGHSCORES_EASY = highscores
    else:
        HIGHSCORES_NORMAL = highscores


#### RECORDING STUFF #########################################################
# todo: move recording logic out of this file
def init_recording():
    """
    Remarks:
    - lowercase values are important for replay
    - UPPER_CASE_VALUES are unlikely to change often between recordings (dependent on game version)
    - "rows" is unlikely to change as well but lowercase because columns is also lowercase
    - columns can currently either be 3 or 6
    """
    global RECORDING

    difficulty = {
        "STAR_BASE_LIKELIHOOD": GAME_CONFIG.STAR_BASE_LIKELIHOOD,
        "STAR_MAX_LIKELIHOOD": GAME_CONFIG.STAR_MAX_LIKELIHOOD,
        "STAR_TIMER_LIKELIHOOD": GAME_CONFIG.STAR_TIMER_LIKELIHOOD,
        "FORCE_STAR_SPAWN_MIN": GAME_CONFIG.FORCE_STAR_SPAWN_MIN,
        "MAX_STARS": GAME_CONFIG.MAX_STARS
    }

    settings = {
        "FRAME_RATE": GAME_CONFIG.FRAME_RATE,
        "STAR_MOVE_RATE": GAME_CONFIG.STAR_MOVE_RATE,
        "STAR_STOP_SPAWN_FRAME_COUNT": GAME_CONFIG.STAR_STOP_SPAWN_FRAME_COUNT,
        "END_FRAME_COUNT": GAME_CONFIG.END_FRAME_COUNT,
        "columns": GAME_CONFIG.COLUMNS,
        "rows": GAME_CONFIG.ROWS
    }
    RECORDING = {
        "player_name": "",
        "seed": time.time(),
        "movements": [],
        "game_version": CURRENT_GAME_VERSION,
        "difficulty": difficulty,
        "settings": settings
    }

init_recording()

def apply_recording_settings():
    if "difficulty" in RECORDING:
        difficulty = RECORDING["difficulty"]
        if "STAR_BASE_LIKELIHOOD" in difficulty: GAME_CONFIG.STAR_BASE_LIKELIHOOD = difficulty["STAR_BASE_LIKELIHOOD"]
        if "STAR_MAX_LIKELIHOOD" in difficulty: GAME_CONFIG.STAR_MAX_LIKELIHOOD = difficulty["STAR_MAX_LIKELIHOOD"]
        if "STAR_TIMER_LIKELIHOOD" in difficulty: GAME_CONFIG.STAR_TIMER_LIKELIHOOD = difficulty["STAR_TIMER_LIKELIHOOD"]
        if "FORCE_STAR_SPAWN_MIN" in difficulty: GAME_CONFIG.FORCE_STAR_SPAWN_MIN = difficulty["FORCE_STAR_SPAWN_MIN"]
        if "MAX_STARS" in difficulty: GAME_CONFIG.MAX_STARS = difficulty["MAX_STARS"]
    if "settings" in RECORDING:
        settings = RECORDING["settings"]
        if "FRAME_RATE" in settings: GAME_CONFIG.FRAME_RATE = settings["FRAME_RATE"]
        if "STAR_MOVE_RATE" in settings: GAME_CONFIG.STAR_MOVE_RATE = settings["STAR_MOVE_RATE"]
        if "STAR_STOP_SPAWN_FRAME_COUNT" in settings: GAME_CONFIG.STAR_STOP_SPAWN_FRAME_COUNT = settings["STAR_STOP_SPAWN_FRAME_COUNT"]
        if "END_FRAME_COUNT" in settings: GAME_CONFIG.END_FRAME_COUNT = settings["END_FRAME_COUNT"]
        if "rows" in settings: GAME_CONFIG.ROWS = settings["rows"]
        if "columns" in settings:
            GAME_CONFIG.COLUMNS = settings["columns"]
    if "player_name" in RECORDING:
        GAME_STATE.PLAYER_NAME = RECORDING["player_name"]


def save_recording(points=None):
    filename = ""
    try:
        filedate = time.strftime("%Y%m%d-%H%M%S")
        game_mode = ""
        if RECORDING["settings"]["columns"] == 3:
            game_mode = "_easy"
        name = RECORDING["player_name"]

        filename = f"recording_{filedate}{game_mode}.pickle"
        if points and len(name)>0:
            filename = f"recording_{filedate}{game_mode}_{name}_{points}.pickle"
        elif points:
            filename = f"recording_{filedate}{game_mode}_{points}.pickle"
        elif len(name)>0:
            filename = f"recording_{filedate}{game_mode}_{name}.pickle"

        filename_full = os.path.join(main_dir, "recordings", filename)

        filename_last = os.path.join(main_dir, "recordings", f"recording_last{game_mode}.pickle")

        with open(filename_last, "wb") as f:
            # noinspection PyTypeChecker
            pickle.dump(RECORDING, f, protocol=pickle.HIGHEST_PROTOCOL)
            f.close()
            print(f"Saved {filename_last}")

        with open(filename_full, "wb") as f:
            # noinspection PyTypeChecker
            pickle.dump(RECORDING, f, protocol=pickle.HIGHEST_PROTOCOL)
            f.close()
            print(f"Saved {filename_full}")
    except Exception as ex:
        print("Error during pickling object (Possibly unsupported):", ex)
    return filename


def load_last_recording():
    global RECORDING
    try:
        game_mode = ""
        if GAME_CONFIG.COLUMNS == 3:
            game_mode = "_easy"

        filename = os.path.join(main_dir, "recordings", f"recording_last{game_mode}.pickle")

        with open(filename, "rb") as f:
            RECORDING = pickle.load(f)
            f.close()
            print(f"Loaded {filename}")

        if RECORDING["game_version"] != CURRENT_GAME_VERSION:
            print("Warning: loaded game recording was recorded with a different version! Replay might differ!")
    except Exception as ex:
        print("Error during pickling object (Possibly unsupported):", ex)


def replay(recording):
    global RECORDING
    
    GAME_STATE.reset(RECORDING["settings"]["columns"])

    RECORDING = recording
    apply_recording_settings()

    GAME_STATE.REPLAY = True
    random.seed(RECORDING["seed"])

#### END RECORDING STUFF #########################################################

def spawn_new_star_row(stars, star_groups):
    if GAME_STATE.FRAME_COUNT > GAME_CONFIG.STAR_STOP_SPAWN_FRAME_COUNT:
        return

    if GAME_STATE.FRAME_COUNT % GAME_CONFIG.STAR_MOVE_RATE != 0:
        return

    star_likelihood = min(GAME_CONFIG.STAR_BASE_LIKELIHOOD + (GAME_STATE.FRAME_COUNT * GAME_CONFIG.STAR_TIMER_LIKELIHOOD), GAME_CONFIG.STAR_MAX_LIKELIHOOD)
    star_count = len(stars.sprites())

    for starNr in range(GAME_CONFIG.MAX_STARS):
        random_draw = random.random()
        spawn_star = random_draw < star_likelihood

        if star_count <= GAME_CONFIG.FORCE_STAR_SPAWN_MIN:
            #print("Force star spawn")
            spawn_star=True
            star_count += 1

        #print(f"FRAME: {FRAME_COUNT}: likelyHood: {star_likelihood}, draw: {random_draw}, spawn: {spawn_star}")

        if spawn_star:
            spawn_column = random.randint(0, GAME_CONFIG.COLUMNS-1)
            #print(f"Spawning at {spawn_column}")
            Star(GAME_STATE, spawn_column, star_groups)


def trigger_controller_sound(name):
    if GAME_STATE.CONTROLLER_COM:
        # GAME_STATE.CONTROLLER_COM.write(bytes(f"play {name}", 'utf-8'))
        try:
            GAME_STATE.CONTROLLER_COM.write(bytes(f"p:{name[0]}\n", 'utf-8'))
            GAME_STATE.CONTROLLER_COM.flush()
        except:
            pass


def get_buttons_from_serial():
    result = []
    if not GAME_STATE.CONTROLLER_COM:
        return result

    last_line = ""

    if (not GAME_STATE.CONTROLLER_LAST_RECEIVE) or (GAME_STATE.CONTROLLER_LAST_RECEIVE + 2.0 < time.time()):
        # we haven't received anythin in a while?
        # let's request the full state
        try:
            GAME_STATE.CONTROLLER_COM.write(bytes(f"state\n", 'utf-8'))
            GAME_STATE.CONTROLLER_COM.flush()
        except:
            pass

    try:
        bytes_to_read =  GAME_STATE.CONTROLLER_COM.inWaiting()
        data =  GAME_STATE.CONTROLLER_COM.read(bytes_to_read)
    except:
        return result
    lines = data.decode("utf-8").splitlines()

    for line in lines:
        print(f"Serial: {line}")
        if line.startswith("BUTTONS:"):
            last_line = line
        if line.startswith("COLOR:"):
            color = line.replace("COLOR:", "")
            match color:
                case "g":
                    GAME_STATE.CONTROLLER_COLOR = "green"
                case "b":
                    GAME_STATE.CONTROLLER_COLOR = "blue"
        if line.startswith("CONNECTION:"):
            state =  line.replace("CONNECTION:", "")
            changed = GAME_STATE.CONTROLLER_CONNECTION_STATE != state
            old_state = GAME_STATE.CONTROLLER_CONNECTION_STATE
            GAME_STATE.CONTROLLER_CONNECTION_STATE = state
            if changed:
                if state == "LOST":
                    result += [SERIAL_CONTROLLER_DC]
                if state == "OK":
                    if old_state == "LOST":
                        result += [SERIAL_CONTROLLER_CN]

        if line == "":
            break

    if last_line != "":
        GAME_STATE.CONTROLLER_LAST_RECEIVE = time.time();
        last_line = last_line.replace("BUTTONS:", "")
        for char in last_line:
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


def do_on_reset_game():
    re_render_background()
    pg.display.flip()

    init_recording()
    random.seed(RECORDING["seed"])


def main():
    # Initialize pygame
    if pg.get_sdl_version()[0] == 2:
        pg.mixer.pre_init(44100, 32, 2, 1024)
    pg.init()
    if pg.mixer and not pg.mixer.get_init():
        print("Warning, no sound")
        pg.mixer = None

    # Set the display mode
    best_depth = pg.display.mode_ok(GAME_STATE.SCREEN_RECT.size, 0, 32)
    screen = pg.display.set_mode(GAME_STATE.SCREEN_RECT.size, 0, best_depth)
    GAME_STATE.GAME_SCREEN = screen
    GAME_STATE.OnResetGame = do_on_reset_game

    #todo: move all screenmode checks to some reset code to be able to switch via debug menu

    # Load images, assign to sprite classes
    # (do this before the classes are used, after screen setup)
    if GAME_STATE.screenMode == ScreenMode.GAME_BIG:
        Player.images = [load_image(im, "goat64") for im in ("goatL.png", "goatR.png", "goatLHorn.png", "goatRHorn.png", "goatLBody.png", "goatRBody.png", "goatLFullGlow.png", "goatRFullGlow.png")]
        Star.images = [load_image("star32.png")]
    elif GAME_STATE.screenMode == ScreenMode.SCORE_GAME_BUTTONS:
        Player.images = [load_image(im, "goat28") for im in ("goatL.png", "goatR.png", "goatLHorn.png", "goatRHorn.png", "goatLBody.png", "goatRBody.png", "goatLFullGlow.png", "goatRFullGlow.png")]
        Star.images = [load_image("star12.png")]

    ## decorate the game window
    # icon = pg.transform.scale(Alien.images[0], (32, 32))
    #pg.display.set_icon(icon)
    pg.display.set_caption("Pygame Star Catcher Goat")
    pg.mouse.set_visible(0)

    # create the background, tile the bgd image
    if GAME_STATE.screenMode == ScreenMode.GAME_BIG:
        background_tile = load_image("background_game_big_normal.png")
    elif GAME_STATE.screenMode == ScreenMode.SCORE_GAME_BUTTONS:
        background_tile = load_image("background_score_game_buttons.png")
    background = pg.Surface(GAME_STATE.SCREEN_RECT.size)
    GAME_STATE.GAME_BACKGROUND = background
    for x in range(0, GAME_STATE.SCREEN_RECT.width, background_tile.get_width()):
        background.blit(background_tile, (x, 0))
    screen.blit(background, (0, 0))
    pg.display.flip()


    # Create Some Starting Values
    clock = pg.time.Clock()

    # Initialize Game Groups
    game_ui_sprites = GAME_STATE.GAME_UI_SPRITES

    game_sprites =  GAME_STATE.GAME_SPRITES

    # initialize our starting sprites
    GAME_STATE.PLAYER = Player(GAME_STATE, game_sprites)
    # todo: nicer:
    GAME_STATE.PLAYER.triggerControllerSoundCallback = trigger_controller_sound

    GAME_STATE.GAMEPAD_BUTTONS = Gamepad_Buttons(GAME_STATE)

    leds = LedHandler(GAME_CONFIG)
    GAME_STATE.LED_HANDLER = leds

    global MENU_FACTORY
    MENU_FACTORY = MenuFactory(GAME_STATE)

    if pg.font:
        score_points = UiText(game_sprites)
        if GAME_STATE.screenMode == ScreenMode.GAME_BIG:
            score_points.targetRect = Rect(905,445, 335, 50)
            score_points.font = load_font(56)
        elif GAME_STATE.screenMode == ScreenMode.SCORE_GAME_BUTTONS:
            score_points.crop = True
            score_points.targetRect = Rect(25, -96, 800, 445)
            score_points.font = load_font(552, "PixelOperator.ttf")
        score_points.color = "#FFC000"
        score_points.align = 0
        GAME_STATE.SCORE_POINTS = score_points

        score_stats = UiText(game_sprites)
        if GAME_STATE.screenMode == ScreenMode.GAME_BIG:
            score_stats.targetRect = Rect(739,515, 510, 50)
        elif GAME_STATE.screenMode == ScreenMode.SCORE_GAME_BUTTONS:
            score_stats.targetRect = Rect(25, 400, 350, 75)
            score_stats.font = load_font(36)
        GAME_STATE.SCORE_STATS = score_stats

        score_missed = UiText(game_sprites)
        if GAME_STATE.screenMode == ScreenMode.GAME_BIG:
            score_missed.targetRect = Rect(739,550, 510, 50)
        elif GAME_STATE.screenMode == ScreenMode.SCORE_GAME_BUTTONS:
            score_missed.targetRect = Rect(400, 400, 350, 75)
            score_missed.font = load_font(36)
            score_missed.align = 1
        score_missed.color = "grey"
        GAME_STATE.SCORE_MISSED = score_missed

    #try to find controller com port
    ports = serial.tools.list_ports.comports()
    for port in ports:
      if port.description == 'Feather 32u4':
        GAME_STATE.CONTROLLER_COM_ADDR = port.device
        try:
            GAME_STATE.CONTROLLER_COM = serial.Serial(port=port.device, baudrate=9600, timeout=.1)
            # todo: decide: deprecate serial off?
            GAME_STATE.CONTROLLER_COM.write(bytes(f"serial on\n", 'utf-8'))
            GAME_STATE.CONTROLLER_COM.flush()
        except: # noqa
            GAME_STATE.CONTROLLER_COM = None

    load_all_highscores()

    # reset before first loop to have same random starting condition as in replay
    GAME_STATE.reset(6)

    GAME_STATE.CURRENT_MENU = MENU_FACTORY.StartMenu(re_render_background)

    # Run our main loop whilst the player is alive.
    while GAME_STATE.PLAYER.alive() and not GAME_STATE.GAME_QUIT:
        # get currently pressed buttons on serial controller
        serial_keys = get_buttons_from_serial()
        next_key_list = serial_keys.copy() # copy for next frame

        # remove keys already pressed last time
        for key in GAME_STATE.LAST_SERIAL_BUTTONS:
            if key in serial_keys:
                serial_keys.remove(key)

        # set current list as pressed last time
        GAME_STATE.LAST_SERIAL_BUTTONS = next_key_list

        if GAME_STATE.CURRENT_MENU:
            GAME_STATE.CURRENT_MENU.loop(serial_keys)
        else:
            play_loop(serial_keys)
            GAME_STATE.MENU_JUST_CLOSED = False

        # cap the framerate at 10fps. Also called 10HZ or 10 times per second.
        clock.tick(GAME_CONFIG.FRAME_RATE)

    leds.set_all_leds_off()
    leds.update_leds()

    if GAME_STATE.CONTROLLER_COM:
        # todo: decide: deprecate serial off?
        # controller seems to get buggy on serial off ...
        # try:
        #     GAME_STATE.CONTROLLER_COM.write(bytes(f"serial off\n", 'utf-8'))
        #     GAME_STATE.CONTROLLER_COM.flush()
        # except:
        #     pass
        GAME_STATE.CONTROLLER_COM = None

    if pg.mixer:
        # todo: really add music and maybe some sample trigger commands to controller
        pg.mixer.music.fadeout(1000)
    pg.time.wait(1000)

def render_highscores():
    # todo: change between normal/easy highscore list on start screen after some time
    mode = "normal"
    mode_text = "Normales Spiel"
    if GAME_CONFIG.COLUMNS == 3:
        mode = "easy"
        mode_text = "Einfaches Spiel"
    font = load_font(28)
    font_mono = load_font(28, "PixelOperatorMono.ttf")
    highscores = f"HIGHSCORES ({mode_text}):"
    text = font.render(highscores, True, Color(255, 255, 255))
    textRect = text.get_rect()
    textRect.left = 25
    textRect.top = 445
    GAME_STATE.GAME_SCREEN.blit(text, textRect)

    y = 447
    highscores = HIGHSCORES_NORMAL
    if mode == "easy":
        highscores = HIGHSCORES_EASY
    if highscores:
        for place in range(10):
            y += 24
            if len(highscores)>place:
                entry = highscores[place]
                name = entry['name']
                if name == '':
                    name = 'Unbekannt'
                highscoretext = f"{place+1: >2}. {entry['points']: >4} Punkte: {name: <10} am {entry['timestamp'].strftime('%d.%m.%Y %H:%M')}"
            else:
                highscoretext = f"{place+1: >2}.    0 Punkte: .........."

            text = font_mono.render(highscoretext, True, Color(255, 255, 255))
            textRect = text.get_rect()
            textRect.left = 25
            textRect.top = y

            GAME_STATE.GAME_SCREEN.blit(text, textRect)

def re_render_background():
    mode = "normal"
    if GAME_CONFIG.COLUMNS == 3:
        mode = "easy"
    if GAME_STATE.screenMode == ScreenMode.GAME_BIG:
        background_tile = load_image(f"background_game_big_{mode}.png")
    elif GAME_STATE.screenMode == ScreenMode.SCORE_GAME_BUTTONS:
        background_tile = load_image("background_score_game_buttons.png")

    background = pg.Surface(GAME_STATE.SCREEN_RECT.size)
    for x in range(0, GAME_STATE.SCREEN_RECT.width, background_tile.get_width()):
        background.blit(background_tile, (x, 0))
    GAME_STATE.GAME_SCREEN.blit(background, (0, 0))

    render_highscores()



def play_loop(serial_keys):
    # load some Game state objects to local vars
    screen = GAME_STATE.GAME_SCREEN
    background = GAME_STATE.GAME_BACKGROUND

    player = GAME_STATE.PLAYER
    stars = GAME_STATE.STARS

    game_sprites =  GAME_STATE.GAME_SPRITES

    score_points = GAME_STATE.SCORE_POINTS
    score_stats = GAME_STATE.SCORE_STATS
    score_missed = GAME_STATE.SCORE_MISSED

    # increase frame count
    GAME_STATE.FRAME_COUNT += 1

    # get input
    # noinspection PyShadowingNames
    def handle_key(key):
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
                RECORDING["movements"].append({"frame": GAME_STATE.FRAME_COUNT, "key": pg.K_RIGHT})
                player.move(1)
        if key in BUTTONS_MOVE_LEFT:
            if not GAME_STATE.REPLAY:
                RECORDING["movements"].append({"frame": GAME_STATE.FRAME_COUNT, "key": pg.K_LEFT})
                player.move(-1)
        if key in BUTTONS_JUMP:
            if not GAME_STATE.REPLAY:
                RECORDING["movements"].append({"frame": GAME_STATE.FRAME_COUNT, "key": pg.K_UP})
                player.jump([star for star in stars if star.hangingLow])
        if (key == pg.K_F7) or (key == pg.K_F10):
            load_last_recording()
            replay(RECORDING)
            return True
        if (key == pg.K_F8) or (key == pg.K_F11):
            replay(RECORDING)
            return True
        if key == SERIAL_CONTROLLER_DC:
            GAME_STATE.CURRENT_MENU = MENU_FACTORY.ControllerConnection(None)
            return True
        return False

    # handle input from OS
    for event in pg.event.get():
        if event.type == pg.QUIT:
            # exit game loop and shut down leds
            player.kill()
            return
        if event.type == pg.KEYDOWN:
            if handle_key(event.key):
                return        

    # handle input from serial
    for key in serial_keys:
        if handle_key(key):
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

    # update score text:
    points = player.points
    score_points.text = f"{points}"

    if GAME_CONFIG.COLUMNS == 3:
        score_stats.text = f"Gefangen: {player.starsCatchedHorn: >2}"
    else:
        score_stats.text = f"Gefangen: {player.starsCatchedHorn+player.starsCatchedButt: >2} (Mit Hörner: {player.starsCatchedHorn: >2})"

    score_missed.text = f"Verpasst: {GAME_STATE.StarsMissed: >2}"

    if (GAME_STATE.FRAME_COUNT == GAME_CONFIG.END_FRAME_COUNT) and (not GAME_STATE.REPLAY):
        def update_and_save_recording():
            name = GAME_STATE.PLAYER_NAME
            RECORDING["player_name"] = name
            filename = save_recording(points)
            mode = "normal"
            if RECORDING["settings"]["columns"] == 3:
                mode = "easy"
            add_highscore(points, name, mode, filename)
            persist_all_highscores()
            re_render_background()
        if random.randint(0,10) > 7:
          trigger_controller_sound("chest")
        else:
          trigger_controller_sound("fanfare")
        score_points.text = ""
        score_missed.text = ""
        score_stats.text = ""
        GAME_STATE.CURRENT_MENU = MENU_FACTORY.NameEntry(update_and_save_recording, re_render_background)

    # re-draw whole background
    if GAME_STATE.MENU_JUST_CLOSED:
        re_render_background()
       
    # clear/erase the last drawn sprites
    game_sprites.clear(screen, background)
    
    leds = GAME_STATE.LED_HANDLER

    leds.set_all_leds_off(only_stars=True)

    # make stars land on player before update
    for star in stars:
        if star.hangingLow:
            star.land(player)

    # update all the sprites
    game_sprites.update()

    for star in stars:
        bright = leds.STAR_BRIGHTNESS_A
        if star.gridPosY > 2:
            bright = leds.STAR_BRIGHTNESS_B
        leds.set_star_led(star.gridPosY, star.gridPosX, bright)

    # draw the scene
    if GAME_STATE.MENU_JUST_CLOSED:
        pg.display.flip()
    
    dirty = game_sprites.draw(screen)
    pg.display.update(dirty)

    spawn_new_star_row(stars, (stars, game_sprites))

    leds.update_leds()


# call the "main" function if running this script
if __name__ == "__main__":
    main()
    pg.quit()
