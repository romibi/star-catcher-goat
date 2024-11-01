import pygame as pg
from pygame import Rect

from config.buttonconfig import SERIAL_BUTTON_START, SERIAL_BUTTON_SELECT
from gamelib.data_helper_functions import load_image, load_font
from gamelib.gamestate import GameState
from gamelib.menus.menuscreen import MenuScreen
from gamelib.uielements import UiText, ButtonIcon


class StartMenuScreen(MenuScreen):
    def __init__(self, state: GameState):
        MenuScreen.__init__(self, state, {}, darken_bg=False)

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