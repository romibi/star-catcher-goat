import pygame as pg

from config.buttonconfig import *

from gamelib.uielements import *

from gamelib.gamestate import GameState

class MenuScreen():
    def __init__(self, state: GameState, menuOptionMap):
        self.gamestate = state
        self.screen = state.GAME_SCREEN
        self.background = self.screen.copy()
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

        overlayBg = pg.Surface(self.gamestate.SCREENRECT.size, pg.SRCALPHA,32)
        overlayBg.fill((0,0,0, 150))
        self.background.blit(overlayBg, (0, 0))

    def _closeMenu(self):        
        self.gamestate.CURRENT_MENU = False
        self.gamestate.MENU_JUST_CLOSED = True



    def Loop(self, serial_keys):
        def handleKey(key):
            if key in BUTTONS_MENU_CLOSE:
                self._closeMenu()
                return True
            if key in BUTTONS_MENU_DOWN:
                self.cursorIndex = min(self.cursorIndex+1, len(self.menuOptionMap.keys())-1)
                self.cursor.targetRect = Rect(50, 100+(self.cursorIndex*50), 64, 64)
            if key in BUTTONS_MENU_UP:
                self.cursorIndex = max(self.cursorIndex-1, 0)
                self.cursor.targetRect = Rect(50, 100+(self.cursorIndex*50), 64, 64)
            if key in BUTTONS_MENU_CONFIRM + BUTTONS_MENU_LEFT + BUTTONS_MENU_RIGHT + BUTTONS_MENU_DENY:
                menuFuncs = list(self.menuOptionMap.values())
                menuFuncs[self.cursorIndex](key)
            return False

        self.frame += 1
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.gamestate.GAME_QUIT = True
                return
            if event.type == pg.KEYDOWN:
                if handleKey(event.key):
                    return

        for key in serial_keys:
            if handleKey(key):
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
