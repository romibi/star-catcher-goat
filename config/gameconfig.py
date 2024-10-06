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
