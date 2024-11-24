from pygame import Rect

from config.buttonconfig import BUTTONS_MENU_DOWN, BUTTONS_MENU_UP, BUTTONS_MENU_LEFT, BUTTONS_MENU_RIGHT, \
    BUTTONS_MENU_CONFIRM, BUTTONS_MENU_DENY
from gamelib.data_helper_functions import load_image, load_font
from gamelib.gamestate import GameState
from gamelib.menus.menuscreen import MenuScreen
from gamelib.uielements import UiText, ImageIcon

class NameEntryScreen(MenuScreen):
    MAX_NAME_LENGTH = 10

    def __init__(self, state: GameState, confirm_callback, next_menu: MenuScreen, other_menus):
        MenuScreen.__init__(self, state, {}, next_menu=next_menu, other_menus=other_menus)
        self.confirm_callback = confirm_callback

        font = load_font(64)

        info_text1 = UiText(self.sprites)
        info_text1.text = f"Du hast {state.PLAYER.points} Punkte erreicht!"
        info_text1.font = font
        info_text1.targetRect = Rect(25, 15, 300, 64)

        info_text2 = UiText(self.sprites)
        info_text2.text = f"Willst du deinen Name eingeben?"
        info_text2.font = font
        info_text2.targetRect = Rect(25, 60, 300, 64)

        font = load_font(64, "PixelOperatorMono-Bold.ttf")

        name_target_area = UiText(self.sprites)
        name_target_area.text = "_ " * self.MAX_NAME_LENGTH
        name_target_area.font = font
        name_target_area.targetRect = Rect(50, 130, 300, 64)

        alphabet_letters1 = UiText(self.sprites)
        alphabet_letters1.text = "A B C D E F G H I J K L M"
        alphabet_letters1.font = font
        alphabet_letters1.targetRect = Rect(50, 210, 300, 64)

        alphabet_letters2 = UiText(self.sprites)
        alphabet_letters2.text = "N O P Q R S T U V W X Y Z"
        alphabet_letters2.font = font
        alphabet_letters2.targetRect = Rect(50, 270, 300, 64)

        alphabet_letters3 = UiText(self.sprites)
        alphabet_letters3.text = "Ä Ö Ü À É È . -"
        alphabet_letters3.font = font
        alphabet_letters3.targetRect = Rect(50, 330, 300, 64)

        alphabet_btns = UiText(self.sprites)
        alphabet_btns.text = "Löschen    OK"
        alphabet_btns.font = load_font(40, "PixelOperator-Bold.ttf")
        alphabet_btns.targetRect = Rect(630, 345, 50, 64)

        self.selector_x = 0
        self.selector_y = 0
        self.selector_images_letters = [load_image(im, "ui") for im in ("selector0.png", "selector1.png")]
        self.selector_images_delete = [load_image(im, "ui") for im in ("selector_löschen0.png", "selector_löschen1.png")]
        self.selector_images_ok = [load_image(im, "ui") for im in ("selector_ok0.png", "selector_ok1.png")]
        self.selector = ImageIcon(49, 221, self.selector_images_letters, self.sprites )

        self.text_cursor = ImageIcon(49, 143, [load_image("selector1.png", "ui")], self.sprites)

        self.name_sprite = UiText(self.sprites)
        self.name_sprite.text = ""
        self.name_sprite.font = font
        self.name_sprite.targetRect = Rect(50,130,300,64)

        self.name = ""

        self.gamestate.GAMEPAD_BUTTONS.set_mode("name")

        self.cursor.text = "" # no cursor

    def select_letter(self):
        if (self.selector_y == 2) and (self.selector_x == 9):
            self.remove_letter()
            return False
        if (self.selector_y == 2) and (self.selector_x == 12):
            return True

        if len(self.name) >= self.MAX_NAME_LENGTH:
            return False

        new_char = ""
        if self.selector_y == 0:
            new_char = chr(65 + self.selector_x)
        elif self.selector_y == 1:
            new_char = chr(78 + self.selector_x)
        else:
            if self.selector_x == 0:
                new_char = "Ä"
            elif self.selector_x == 1:
                new_char = "Ö"
            elif self.selector_x == 2:
                new_char  = "Ü"
            elif self.selector_x == 3:
                new_char = "À"
            elif self.selector_x == 4:
                new_char = "É"
            elif self.selector_x == 5:
                new_char = "È"
            elif self.selector_x == 6:
                new_char = "."
            elif self.selector_x == 7:
                new_char = "-"
            elif self.selector_x == 8:
                new_char = " "

        self.name = (self.name+new_char).lstrip() # don't allow space at start
        self.update_name_sprite()
        return False

    def update_name_sprite(self):
        if len(self.name) == self.MAX_NAME_LENGTH:
            self.text_cursor.rect.left = -80 # move it offscreen as we can't type anymore
        else:
            self.text_cursor.rect.left = 49 + 64 * len(self.name)
        self.name_sprite.text = "".join(['{} '.format(x) for x in self.name])


    def remove_letter(self):
        if len(self.name) > 0:
            self.name = self.name[:-1]
            self.update_name_sprite()


    def update_selector(self, moved_horizontally):
        # reset to default image list
        self.selector.images = self.selector_images_letters

        # on row 2 we might need to modify x coord and/or active image list
        if self.selector_y == 2:
            # Adapt x Coord if necessary: 8 = space, 9 = delete, 12 = ok; if 10 or 11: => 9
            if moved_horizontally:
                if self.selector_x == 10: # moving from delete towards ok
                    self.selector_x = 12
                if self.selector_x == 11: # moving from ok towards delete
                    self.selector_x = 9
            else:
                # moving vertically all x from 9 to 11 align up to delete
                if (self.selector_x > 9) and (self.selector_x < 12):
                    self.selector_x = 9

            # Change to different selector image list for delete or ok
            if self.selector_x == 9:
                self.selector.images = self.selector_images_delete
            if self.selector_x == 12:
                self.selector.images = self.selector_images_ok

        # Update selector sprite coordinates (special cases for left coordinate of some letters/buttons)
        if (self.selector_y == 2) and (self.selector_x >= 9):
            # delete and ok
            if self.selector_x == 9: # delete button selector left coord
                self.selector.rect.left = 628
            if self.selector_x == 12: # ok button selector left coord
                self.selector.rect.left = 808
        elif (self.selector_y == 0) and (self.selector_x == 12):
            # "M" selector left coordinate (it's awfully wide)
            self.selector.rect.left = 49 + self.selector_x * 64 - 2
        else:
            # left coord for all other letters
            self.selector.rect.left = 49 + self.selector_x * 64
        # top coordinate calculation is the same for all
        self.selector.rect.top = 221 + self.selector_y * 60


    def confirm(self):
        self.gamestate.PLAYER_NAME = self.name.strip() # don't allow spaces at end
        self.confirm_callback()
        # we don't use self._close_menu() because we need to upgrade next menu background
        self.gamestate.GAMEPAD_BUTTONS.set_mode("start") # next menu is start menu → make sure correct buttons are shown
        self.gamestate.CURRENT_MENU = self.next_menu
        # callback might update screen → update next menu background
        self.gamestate.CURRENT_MENU.background = self.gamestate.GAME_SCREEN.copy()

    def handle_key(self, key):
        if key in BUTTONS_MENU_DOWN:
            self.selector_y = (self.selector_y + 1) % 3
            self.update_selector(False)
        elif key in BUTTONS_MENU_UP:
            self.selector_y = (self.selector_y - 1) % 3
            self.update_selector(False)
        elif key in BUTTONS_MENU_RIGHT:
            self.selector_x = (self.selector_x + 1) % 13
            self.update_selector(True)
        elif key in BUTTONS_MENU_LEFT:
            self.selector_x = (self.selector_x - 1) % 13
            self.update_selector(True)

        elif key in BUTTONS_MENU_CONFIRM:
            if self.select_letter():
                self.confirm()
                return True
        elif key in BUTTONS_MENU_DENY:
            self.remove_letter()
        else:
            return MenuScreen.handle_key(self,key)