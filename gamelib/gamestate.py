import pygame as pg
from pygame import Rect

from config.gameconfig import GameConfig, ScreenMode
from config.gamevisualizationconfig import GameVisualizationConfig
from gamelib.ledhandler import LedHandler


class GameState:
    # todo: check what None values could be moved to constructor
    SCREEN_RECT = Rect(0, 0, 1280, 720)

    CURRENT_MENU = None
    MENU_JUST_CLOSED = False
    GAME_QUIT = False

    REPLAY = False

    FRAME_COUNT = 0
    StarsMissed = 0

    CONTROLLER_COM_ADDR = ''
    CONTROLLER_COM = None
    CONTROLLER_COLOR = "green"
    CONTROLLER_CONNECTION_STATE = "UNKNOWN"
    CONTROLLER_CONNECTION_RECEPTION = -999
    CONTROLLER_LAST_RECEIVE = None

    CONTROLLER_PLAY_CATCH_SOUND = True

    LAST_SERIAL_BUTTONS = []

    LED_HANDLER: LedHandler | None

    PLAYER_NAME = ""

    PLAYER = None
    STARS = pg.sprite.Group()

    GAME_UI_SPRITES = pg.sprite.RenderUpdates()

    GAME_SPRITES = pg.sprite.RenderUpdates()

    GAME_SCREEN = None
    GAME_BACKGROUND = None

    SCORE_POINTS = None
    SCORE_STATS = None
    SCORE_MISSED = None

    GAMEPAD_BUTTONS = None

    def reset(self, new_columns):
        # Shutdown LEDS
        self.LED_HANDLER.set_all_leds_off()
        self.LED_HANDLER.update_leds()

        for star in self.STARS:
            star.kill()

        self.GAMEPAD_BUTTONS.set_mode("game")

        self.config.reset() # restore default values (in case recording replay manipulated them)
        self.config.COLUMNS = new_columns

        if self.config.COLUMNS == 3:
            self.LED_HANDLER.ledSegmentMap = self.LED_HANDLER.ledSegmentMap3
        else:
            self.LED_HANDLER.ledSegmentMap = self.LED_HANDLER.ledSegmentMap6

        if self.screenMode == ScreenMode.GAME_BIG:
            if self.config.COLUMNS == 3:
                self.vizConfig.vizRects = self.vizConfig.vizRects3B
            else:
                self.vizConfig.vizRects = self.vizConfig.vizRects6B
            self.vizConfig.vizGoatRects = self.vizConfig.vizGoatRectsB
        elif self.screenMode == ScreenMode.SCORE_GAME_BUTTONS:
            if self.config.COLUMNS == 3:
                self.vizConfig.vizRects = self.vizConfig.vizRects3S
            else:
                self.vizConfig.vizRects = self.vizConfig.vizRects6S
            self.vizConfig.vizGoatRects = self.vizConfig.vizGoatRectsS

        self.LED_HANDLER.reset()
        self.PLAYER.reset()

        self.StarsMissed = 0
        self.REPLAY = False
        self.FRAME_COUNT = 0

        if self.OnResetGame:
            self.OnResetGame()


    def __init__(self, conf: GameConfig, visualization_config: GameVisualizationConfig):
        self.config = conf
        self.vizConfig = visualization_config
        self.screenMode = conf.DEFAULT_SCREEN_MODE
        self.OnResetGame = None
        self.LED_HANDLER = None