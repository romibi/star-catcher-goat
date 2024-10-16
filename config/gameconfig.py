from enum import Enum

# ScreenModeElements = Enum('ScreenModeElements', ['GAME_VIEW', 'GAME_VIEW_SMALL', 'HISCORE', 'BUTTON_VIEW'])
class ScreenMode(Enum):
    GAME_BIG = 1
    SCORE_GAME_BUTTONS_HIGHSCORES = 2
    SCORE_GAME_BUTTONS = 3

class GameConfig:
    STAR_BASE_LIKELIHOOD: float  # Likelihood of first star per spawn block (0.3 = 30%, 2nd star half of it)
    STAR_MAX_LIKELIHOOD: float  # Max likelihood for first star per spawn block (2nd star half of it)
    STAR_TIMER_LIKELIHOOD: float  # star spawn likelihood increase over time
    FORCE_STAR_SPAWN_MIN: int  # if less stars than this are visible, first star spawns 100%
    MAX_STARS: int  # max stars per row

    # speed
    FRAME_RATE: int # fps
    STAR_MOVE_RATE: int # stars move every x frames

    # game end
    STAR_STOP_SPAWN_FRAME_COUNT: int  # no more stars after this frame
    END_FRAME_COUNT: int # game ends after this frame

    # how many stars? 3x6 or 6x6
    ROWS: int
    COLUMNS: int  # code works with 3 or 6 columns

    # Non-resetting configs (not stored in replay)
    DEFAULT_SCREEN_MODE: ScreenMode

    def __init__(self):
        self.DEFAULT_SCREEN_MODE = ScreenMode.GAME_BIG
        self.reset()

    def reset(self):
        # difficulty settings
        self.STAR_BASE_LIKELIHOOD = 0.3
        self.STAR_MAX_LIKELIHOOD = 0.95
        self.STAR_TIMER_LIKELIHOOD = 0.0005
        self.FORCE_STAR_SPAWN_MIN = 2
        self.MAX_STARS = 2

        # speed
        self.FRAME_RATE = 10
        self.STAR_MOVE_RATE = 10

        # game end
        self.STAR_STOP_SPAWN_FRAME_COUNT = 1120 # 112 seconds
        self.END_FRAME_COUNT = 1200 # 120 seconds

        # how many stars? 3x6 or 6x6
        self.ROWS = 6
        self.COLUMNS = 6
