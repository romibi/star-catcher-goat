import pygame as pg
from pygame import Rect

from config.buttonconfig import *
from gamelib.data_helper_functions import load_image, load_font
from gamelib.gamestate import GameState
from gamelib.menus.menuscreen import MenuScreen
from gamelib.uielements import UiText, ButtonIcon


class StartMenuScreen(MenuScreen):
    def __init__(self, state: GameState, other_menus, re_render_scores_callback):
        MenuScreen.__init__(self, state,{}, other_menus=other_menus, darken_bg=False)

        self.re_render_scores = re_render_scores_callback

        normal_game_text = UiText(self.sprites)
        normal_game_text.text = "Normales Spiel starten"
        normal_game_text.targetRect = Rect(160, 110, 300, 300)
        normal_game_text.font = load_font(64)
        easy_game_text = UiText(self.sprites)
        easy_game_text.text = "Einfaches Spiel starten"
        easy_game_text.targetRect = Rect(160, 210, 300, 300)
        easy_game_text.font = load_font(64)
        # noinspection PyTypeChecker
        ButtonIcon(50, 85, [load_image(im, "buttons96") for im in ("button_black.png", "button_black_pressed.png")], self.sprites).frame = 12
        ButtonIcon(50, 185, [load_image(im, "buttons96") for im in ("button_white.png", "button_white_pressed.png")], self.sprites)

        state.GAMEPAD_BUTTONS.set_mode("start")

        self.cursor.text = "" # no cursor

    def handle_load_recording(self, key):
        if key in BUTTONS_LOAD_RECORDING_1:
            self.gamestate.LOAD_RECORDING_NR = 0
        elif key in BUTTONS_LOAD_RECORDING_2:
            self.gamestate.LOAD_RECORDING_NR = 1
        elif key in BUTTONS_LOAD_RECORDING_3:
            self.gamestate.LOAD_RECORDING_NR = 2
        elif key in BUTTONS_LOAD_RECORDING_4:
            self.gamestate.LOAD_RECORDING_NR = 3
        elif key in BUTTONS_LOAD_RECORDING_5:
            self.gamestate.LOAD_RECORDING_NR = 4
        elif key in BUTTONS_LOAD_RECORDING_6:
            self.gamestate.LOAD_RECORDING_NR = 5
        elif key in BUTTONS_LOAD_RECORDING_7:
            self.gamestate.LOAD_RECORDING_NR = 6
        elif key in BUTTONS_LOAD_RECORDING_8:
            self.gamestate.LOAD_RECORDING_NR = 7
        elif key in BUTTONS_LOAD_RECORDING_9:
            self.gamestate.LOAD_RECORDING_NR = 8
        elif key in BUTTONS_LOAD_RECORDING_10:
            self.gamestate.LOAD_RECORDING_NR = 9
        else:
            return False
        self.gamestate.LOAD_RECORDING_NR += self.gamestate.SCORE_DISPLAY_PAGE*10
        return True

    def handle_key(self, key):
        modifiers = pg.key.get_mods()
        shift_pressed = False
        if modifiers & pg.KMOD_LSHIFT:
            shift_pressed = True

        if key == SERIAL_BUTTON_START:
            self.gamestate.reset(6)
            self._close_menu()
            return True
        elif key == SERIAL_BUTTON_SELECT:
            self.gamestate.reset(3)
            self._close_menu()
            return True
        elif key in BUTTONS_HIGHSCORE_PAGE_DOWN:
            if shift_pressed:
                self.gamestate.config.COLUMNS = 3
            else:
                self.gamestate.SCORE_DISPLAY_PAGE += 1
            self.re_render_scores()
            pg.display.flip()
            return True
        elif key in BUTTONS_HIGHSCORE_PAGE_UP:
            if shift_pressed:
                self.gamestate.config.COLUMNS = 6
            else:
                self.gamestate.SCORE_DISPLAY_PAGE -= 1
                if self.gamestate.SCORE_DISPLAY_PAGE < 0:
                    self.gamestate.SCORE_DISPLAY_PAGE = 0
            self.re_render_scores()
            pg.display.flip()
            return True
        elif key in BUTTONS_LOAD_RECORDING:
            return self.handle_load_recording(key)
        else:
            return MenuScreen.handle_key(self, key)

    def loop(self, serial_keys):
        # Switch High-Score List every 30s if on first page (self.frame starts at -1 → +2 to not swap in first 2 frames)
        if (self.gamestate.SCORE_DISPLAY_PAGE == 0) and ((self.frame+2) % (self.gamestate.config.FRAME_RATE*30) == 0):
            if self.gamestate.config.COLUMNS == 3:
                self.gamestate.config.COLUMNS = 6
            else:
                self.gamestate.config.COLUMNS = 3
            self.re_render_scores()
            pg.display.flip()
        MenuScreen.loop(self, serial_keys)
