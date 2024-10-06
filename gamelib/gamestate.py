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

    def __init__(self, conf: GameConfig, vizConf: GameVisualizationConfig):
        self.config = conf
        self.vizConfig = vizConf
