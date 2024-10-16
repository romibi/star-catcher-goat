#!/usr/bin/env python

import os
import random
import time
import subprocess
import pickle
import serial
import serial.tools.list_ports

from config.gameconfig import GameConfig, ScreenMode
from config.gamevisualizationconfig import GameVisualizationConfig
from config.buttonconfig import *

from gamelib.gamestate import GameState
from gamelib.ledhandler import LedHandler
from gamelib.entities.star import Star
from gamelib.entities.player import Player

from gamelib.menus.menufactory import MenuFactory
from gamelib.uielements import *

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

def save_recording(points=None):
    try:
        filedate = time.strftime("%Y%m%d-%H%M%S")
        game_mode = ""
        if RECORDING["settings"]["columns"] == 3:
            game_mode = "_easy"
        filename = os.path.join(main_dir, "recordings", f"recording_{filedate}{game_mode}.pickle")
        if points:
            filename = os.path.join(main_dir, "recordings", f"recording_{filedate}{game_mode}_{points}.pickle")

        filename_last = os.path.join(main_dir, "recordings", f"recording_last{game_mode}.pickle")

        with open(filename_last, "wb") as f:
            # noinspection PyTypeChecker
            pickle.dump(RECORDING, f, protocol=pickle.HIGHEST_PROTOCOL)
            print(f"Saved {filename_last}")

        with open(filename, "wb") as f:
            # noinspection PyTypeChecker
            pickle.dump(RECORDING, f, protocol=pickle.HIGHEST_PROTOCOL)
            print(f"Saved {filename}")
    except Exception as ex:
        print("Error during pickling object (Possibly unsupported):", ex)


def load_last_recording():
    global RECORDING
    try:
        game_mode = ""
        if GAME_CONFIG.COLUMNS == 3:
            game_mode = "_easy"

        filename = os.path.join(main_dir, "recordings", f"recording_last{game_mode}.pickle")

        with open(filename, "rb") as f:
            RECORDING = pickle.load(f)
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


# helper functions
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
        GAME_STATE.CONTROLLER_COM.write(bytes(f"play {name}", 'utf-8'))
        GAME_STATE.CONTROLLER_COM.flush()

def get_buttons_from_serial():
    result = []
    if not GAME_STATE.CONTROLLER_COM:
        return result

    last_line = ""

    bytes_to_read =  GAME_STATE.CONTROLLER_COM.inWaiting()
    data =  GAME_STATE.CONTROLLER_COM.read(bytes_to_read)
    lines = data.decode("utf-8").splitlines()

    for line in lines:
        print(f"Serial: {line}")
        if line.startswith("BUTTONS:"):
            last_line = line
        if line == "":
            break

    if last_line != "":
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
    end_ui_sprites = GAME_STATE.END_UI_SPRITES

    game_sprites =  GAME_STATE.GAME_SPRITES

    # initialize our starting sprites
    GAME_STATE.PLAYER = Player(GAME_STATE, game_sprites)

    if GAME_STATE.screenMode == ScreenMode.GAME_BIG:
        # right/left buttons
        # noinspection PyTypeChecker
        ButtonIcon(810, 330, [load_image(im, "buttons32") for im in ("button_blue_left.png", "button_blue_left_pressed.png")], (game_ui_sprites, game_sprites)).frame = 24 # offset button animations a bit
        # noinspection PyTypeChecker
        ButtonIcon(860, 330, [load_image(im, "buttons32") for im in ("button_blue_right.png", "button_blue_right_pressed.png")], (game_ui_sprites, game_sprites))
        # noinspection PyTypeChecker
        ButtonIcon(780, 370, [load_image(im, "buttons32") for im in ("button_yellow.png", "button_yellow_pressed.png")], (game_ui_sprites, game_sprites)).frame = 12

        # noinspection PyTypeChecker
        ButtonIcon(750, 620, [load_image(im, "buttons32") for im in ("button_black_right.png", "button_black_right_pressed.png")], (end_ui_sprites, game_sprites)).frame = 24
        # noinspection PyTypeChecker
        ButtonIcon(750, 670, [load_image(im, "buttons32") for im in ("button_black_left.png", "button_black_left_pressed.png")], (end_ui_sprites, game_sprites))
    elif GAME_STATE.screenMode == ScreenMode.SCORE_GAME_BUTTONS:
        # gamepad buttons from back to front
        # noinspection PyTypeChecker
        ButtonIcon(960, 449, [load_image(im, "buttons32") for im in ("button_blue_up.png", "button_blue_up_pressed.png")], (game_ui_sprites, game_sprites))
        # noinspection PyTypeChecker
        ButtonIcon(1020, 449, [load_image(im, "buttons32") for im in ("button_white.png", "button_white_pressed.png")], (end_ui_sprites, game_sprites))
        # noinspection PyTypeChecker
        ButtonIcon(1055, 449, [load_image(im, "buttons32") for im in ("button_black.png", "button_black_pressed.png")], (end_ui_sprites, game_sprites)).frame = 24

        # noinspection PyTypeChecker
        ButtonIcon(934, 464, [load_image(im, "buttons32") for im in ("button_blue_left.png", "button_blue_left_pressed.png")],(game_ui_sprites, game_sprites)).frame = 6
        # noinspection PyTypeChecker
        ButtonIcon(983, 464, [load_image(im, "buttons32") for im in ("button_blue_right.png", "button_blue_right_pressed.png")],(game_ui_sprites, game_sprites)).frame = 12
        # noinspection PyTypeChecker
        ButtonIcon(1146, 464, [load_image(im, "buttons32") for im in ("button_red.png", "button_red_pressed.png")],(game_ui_sprites, game_sprites))

        # noinspection PyTypeChecker
        ButtonIcon(954, 481, [load_image(im, "buttons32") for im in ("button_blue_down.png", "button_blue_down_pressed.png")],(game_ui_sprites, game_sprites)).frame = 24
        # noinspection PyTypeChecker
        ButtonIcon(1120, 481, [load_image(im, "buttons32") for im in ("button_yellow.png", "button_yellow_pressed.png")],(game_ui_sprites, game_sprites)).frame = 6

    leds = LedHandler(GAME_CONFIG)
    GAME_STATE.LED_HANDLER = leds

    global MENU_FACTORY
    MENU_FACTORY = MenuFactory(GAME_STATE)

    if pg.font:
        score_points = UiText(game_sprites)
        if GAME_STATE.screenMode == ScreenMode.GAME_BIG:
            score_points.targetRect = Rect(905,445, 335, 50)
            score_points.font = pg.font.Font(None, 56)
        elif GAME_STATE.screenMode == ScreenMode.SCORE_GAME_BUTTONS:
            score_points.targetRect = Rect(25, 30, 800, 355)
            score_points.font = pg.font.Font(None, 550)
        score_points.color = "#FFC000"
        score_points.align = 0
        GAME_STATE.SCORE_POINTS = score_points

        score_stats = UiText(game_sprites)
        if GAME_STATE.screenMode == ScreenMode.GAME_BIG:
            score_stats.targetRect = Rect(739,515, 510, 50)
        elif GAME_STATE.screenMode == ScreenMode.SCORE_GAME_BUTTONS:
            score_stats.targetRect = Rect(25, 400, 350, 75)
            score_stats.font = pg.font.Font(None, 36)
        GAME_STATE.SCORE_STATS = score_stats

        score_missed = UiText(game_sprites)
        if GAME_STATE.screenMode == ScreenMode.GAME_BIG:
            score_missed.targetRect = Rect(739,550, 510, 50)
        elif GAME_STATE.screenMode == ScreenMode.SCORE_GAME_BUTTONS:
            score_missed.targetRect = Rect(400, 400, 350, 75)
            score_missed.font = pg.font.Font(None, 36)
        score_missed.color = "grey"
        GAME_STATE.SCORE_MISSED = score_missed

    #try to find controller com port
    ports = serial.tools.list_ports.comports()
    for port in ports:
      if port.description == 'Feather 32u4':
        GAME_STATE.CONTROLLER_COM_ADDR = port.device
        try:
            GAME_STATE.CONTROLLER_COM = serial.Serial(port=port.device, baudrate=9600, timeout=.1)
            GAME_STATE.CONTROLLER_COM.write(bytes(f"serial on", 'utf-8'))
            GAME_STATE.CONTROLLER_COM.flush()
        except: # noqa
            GAME_STATE.CONTROLLER_COM = None

    # reset before first loop to have same random starting condition as in replay
    GAME_STATE.reset(6)

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
        # controller seems to get buggy on serial off ...
        #GAME_STATE.CONTROLLER_COM.write(bytes(f"serial off", 'utf-8'))
        #GAME_STATE.CONTROLLER_COM.flush()
        GAME_STATE.CONTROLLER_COM = None

    if pg.mixer:
        # todo: really add music and maybe some sample trigger commands to controller
        pg.mixer.music.fadeout(1000)
    pg.time.wait(1000)

def re_render_background():
    if GAME_STATE.screenMode == ScreenMode.GAME_BIG:
        if GAME_CONFIG.COLUMNS == 3:
            background_tile = load_image("background_game_big_easy.png")
        else:
            background_tile = load_image("background_game_big_normal.png")
    elif GAME_STATE.screenMode == ScreenMode.SCORE_GAME_BUTTONS:
        background_tile = load_image("background_score_game_buttons.png")

    background = pg.Surface(GAME_STATE.SCREEN_RECT.size)
    for x in range(0, GAME_STATE.SCREEN_RECT.width, background_tile.get_width()):
        background.blit(background_tile, (x, 0))
    GAME_STATE.GAME_SCREEN.blit(background, (0, 0))


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
    points = max(((player.starsCatchedHorn*10)+player.starsCatchedButt-GAME_STATE.StarsMissed),0)
    score_points.text = f"{points}"

    if GAME_CONFIG.COLUMNS == 3:
        score_stats.text = f"Gefangen: {player.starsCatchedHorn}"
    else:
        score_stats.text = f"Gefangen: (Horn/Total): {player.starsCatchedHorn}/{player.starsCatchedHorn+player.starsCatchedButt}"

    score_missed.text = f"Verpasst: {GAME_STATE.StarsMissed}"


    if (GAME_STATE.FRAME_COUNT == 1) or (GAME_STATE.FRAME_COUNT == GAME_CONFIG.END_FRAME_COUNT):
        for sprite in GAME_STATE.GAME_UI_SPRITES:
            sprite.paused = GAME_STATE.FRAME_COUNT != 1
        for sprite in GAME_STATE.END_UI_SPRITES:
            sprite.paused = GAME_STATE.FRAME_COUNT != GAME_CONFIG.END_FRAME_COUNT

    if (GAME_STATE.FRAME_COUNT == GAME_CONFIG.END_FRAME_COUNT) and (not GAME_STATE.REPLAY):
        # todo: Add Hi-Score Name enter screen and Hi-Score list
        save_recording(points)
        if random.randint(0,10) > 7:
          trigger_controller_sound("chest")
        else:
          trigger_controller_sound("fanfare")

    # re-draw whole background
    if GAME_STATE.MENU_JUST_CLOSED:
        re_render_background()
       
    # clear/erase the last drawn sprites
    game_sprites.clear(screen, background)
    
    leds = GAME_STATE.LED_HANDLER

    leds.set_all_leds_off()

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
