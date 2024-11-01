import pygame as pg
from pygame import Rect

from gamelib.data_helper_functions import load_image
from gamelib.gamestate import GameState
from gamelib.menus.menuscreen import MenuScreen
from gamelib.uielements import UiText, ButtonIcon


class StartMenuScreen(MenuScreen):
    def __init__(self, state: GameState):
        MenuScreen.__init__(self, state, {}, darken_bg=False)

        normal_game_text = UiText(self.sprites)
        normal_game_text.text = "Normales Spiel starten"
        normal_game_text.targetRect = Rect(200, 120, 300, 300)
        normal_game_text.font = pg.font.Font(None, 84)

        easy_game_text = UiText(self.sprites)
        easy_game_text.text = "Einfaches Spiel starten"
        easy_game_text.targetRect = Rect(200, 260, 300, 300)
        easy_game_text.font = pg.font.Font(None, 84)

        # noinspection PyTypeChecker
        ButtonIcon(90, 95, [load_image(im, "buttons96") for im in ("button_black.png", "button_black_pressed.png")], self.sprites).frame = 12
        ButtonIcon(90, 235, [load_image(im, "buttons96") for im in ("button_white.png", "button_white_pressed.png")], self.sprites)

        self.cursor.text = "" # no cursor
