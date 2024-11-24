import pygame as pg
from pygame import Rect

from config.buttonconfig import SERIAL_BUTTON_START, SERIAL_BUTTON_SELECT
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

    def handle_key(self, key):
        if key == SERIAL_BUTTON_START:
            self.gamestate.reset(6)
            self._close_menu()
            return True
        elif key == SERIAL_BUTTON_SELECT:
            self.gamestate.reset(3)
            self._close_menu()
            return True
        else:
            return MenuScreen.handle_key(self, key)

    def loop(self, serial_keys):
        # Switch High-Score List every 30s (self.frame starts at -1 → +2 to not swap in first 2 frames)
        if (self.frame+2) % (self.gamestate.config.FRAME_RATE*30) == 0:
            if self.gamestate.config.COLUMNS == 3:
                self.gamestate.config.COLUMNS = 6
            else:
                self.gamestate.config.COLUMNS = 3
            self.re_render_scores()
            pg.display.flip()
        MenuScreen.loop(self, serial_keys)
