from config.buttonconfig import *

from gamelib.uielements import *

from gamelib.gamestate import GameState

class MenuScreen:
    def __init__(self, state: GameState, menu_optionmap):
        self.gamestate = state
        self.screen = state.GAME_SCREEN
        self.background = self.screen.copy()
        self.sprites = pg.sprite.RenderUpdates()
        self.cursor = UiText(self.sprites)
        self.cursor.text = ">"
        self.cursor.targetRect = Rect(50, 100, 64, 64)
        self.menuOptionMap = menu_optionmap
        self.cursorIndex = 0

        next_pos = 100
        for menuEntry in menu_optionmap.keys():
            entry = UiText(self.sprites)
            if type(menuEntry) == str:
                entry.text = menuEntry
            elif callable(menuEntry):
                entry.textFunc = menuEntry
            entry.targetRect = Rect(100, next_pos, 300, 300)
            next_pos += 50

        self.frame = -1

        overlay_bg = pg.Surface(self.gamestate.SCREEN_RECT.size, pg.SRCALPHA, 32)
        overlay_bg.fill((0,0,0, 150))
        self.background.blit(overlay_bg, (0, 0))

    def _close_menu(self):
        self.gamestate.CURRENT_MENU = False
        self.gamestate.MENU_JUST_CLOSED = True



    def loop(self, serial_keys):

        # noinspection PyShadowingNames
        def handle_key(key):
            if key in BUTTONS_MENU_CLOSE:
                self._close_menu()
                return True
            if key in BUTTONS_MENU_DOWN:
                self.cursorIndex = min(self.cursorIndex+1, len(self.menuOptionMap.keys())-1)
                self.cursor.targetRect = Rect(50, 100+(self.cursorIndex*50), 64, 64)
            if key in BUTTONS_MENU_UP:
                self.cursorIndex = max(self.cursorIndex-1, 0)
                self.cursor.targetRect = Rect(50, 100+(self.cursorIndex*50), 64, 64)
            if key in BUTTONS_MENU_CONFIRM + BUTTONS_MENU_LEFT + BUTTONS_MENU_RIGHT + BUTTONS_MENU_DENY:
                menu_functions = list(self.menuOptionMap.values())
                menu_functions[self.cursorIndex](key)
            return False

        self.frame += 1
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.gamestate.GAME_QUIT = True
                return
            if event.type == pg.KEYDOWN:
                if handle_key(event.key):
                    return

        for key in serial_keys:
            if handle_key(key):
                return

        if self.frame == 0:
            self.screen.blit(self.background, (0, 0))

        self.sprites.clear(self.screen, self.background)

        self.sprites.update()

        # draw the scene
        if self.frame == 0:
            pg.display.flip()
        
        dirty = self.sprites.draw(self.screen)
        pg.display.update(dirty)
