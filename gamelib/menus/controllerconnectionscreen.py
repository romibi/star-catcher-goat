from pygame import Rect

from config.buttonconfig import SERIAL_BUTTON_START, SERIAL_BUTTON_SELECT, SERIAL_CONTROLLER_CN, SERIAL_CONTROLLER_DC
from gamelib.data_helper_functions import load_image, load_font
from gamelib.gamestate import GameState
from gamelib.menus.menuscreen import MenuScreen
from gamelib.uielements import UiText, ButtonIcon


class ControllerConnectionScreen(MenuScreen):
    def __init__(self, state: GameState, next_menu: MenuScreen):
        MenuScreen.__init__(self, state,  {}, {}, next_menu=next_menu)

        menu_text_1 = UiText(self.sprites)
        menu_text_1.text = "Kontroller ist nicht verbunden!"
        menu_text_1.targetRect = Rect(160, 310, 300, 300)
        menu_text_1.font = load_font(64)

        menu_text_2 = UiText(self.sprites)
        menu_text_2.text = "Bitte einschalten!"
        menu_text_2.targetRect = Rect(160, 370, 300, 300)
        menu_text_2.font = load_font(64)

        #todo bild

        self.cursor.text = "" # no cursor

    def handle_key(self, key):
        if key == SERIAL_CONTROLLER_CN:
            self._close_menu()
            return True
        if key == SERIAL_CONTROLLER_DC:
            return False # nothing to do
        else:
            return MenuScreen.handle_key(self, key)
