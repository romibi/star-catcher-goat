import pygame as pg
from pygame import Rect

from config.gameconfig import GameConfig
from config.gamevisualizationconfig import GameVisualizationConfig

class GameState():
    SCREENRECT = Rect(0, 0, 1280, 720)

    CURRENT_MENU = None
    MENU_JUST_CLOSED = False
    GAME_QUIT = False

    REPLAY = False

    FRAME_COUNT = 0
    StarsMissed = 0

    CONTROLLER_COM_ADDR = ''
    CONTROLLER_COM = None

    CONTROLLER_PLAY_CATCH_SOUND = False

    LAST_SERIAL_BUTTONS = []

    LED_HANDLER = None

    PLAYER = None
    STARS = pg.sprite.Group()

    GAME_UI_SPRITES = pg.sprite.Group()    
    END_UI_SPRITES = pg.sprite.Group()

    GAME_SPRITES = pg.sprite.RenderUpdates()

    GAME_SCREEN = None
    GAME_BACKGROUND = None

    SCORE_POINTS = None
    SCORE_STATS = None
    SCORE_MISSED = None


    def reset(self, newColumns):
        # Shutdown LEDS
        self.LED_HANDLER.SetAllLedsOff()
        self.LED_HANDLER.UpdateLeds()

        for star in self.STARS:
            star.kill()

        self.config.reset() # restore default values (in case recording replay manipulated them)
        self.config.COLUMNS = newColumns

        if self.config.COLUMNS == 3:
            self.vizConfig.vizRects = self.vizConfig.vizRects3
            self.LED_HANDLER.ledSegmentMap = self.LED_HANDLER.ledSegmentMap3
        else:
            self.vizConfig.vizRects = self.vizConfig.vizRects6
            self.LED_HANDLER.ledSegmentMap = self.LED_HANDLER.ledSegmentMap6

        self.LED_HANDLER.reset()
        self.PLAYER.reset()

        self.StarsMissed = 0
        self.REPLAY = False
        self.FRAME_COUNT = 0

        if self.OnResetGame:
            self.OnResetGame()


    def __init__(self, conf: GameConfig, vizConf: GameVisualizationConfig):
        self.config = conf
        self.vizConfig = vizConf
        self.OnResetGame = None
