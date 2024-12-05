import pygame as pg
from pygame import Rect, Color
from pygame.math import clamp

from config.gameconfig import ScreenMode
from gamelib.data_helper_functions import load_image, load_font
from gamelib.gamestate import GameState
from gamelib.uielements import ButtonIcon, ImageIcon, UiText, LineSprite


class Gamepad_Buttons():

    def __init__(self, state: GameState):
        self.gamestate = state
        self.frame = 0
        self.previous_screen_mode = None
        self.show_labels_mode = "start" # start | game | name-entry

        game_sprites = self.gamestate.GAME_SPRITES
        game_ui_sprites = self.gamestate.GAME_UI_SPRITES

        self.gamepad_sprite = ImageIcon(753,398, [load_image('gamepad.png', 'ui')], (game_ui_sprites, game_sprites))

        self.dpad_color = self.gamestate.CONTROLLER_COLOR
        if self.dpad_color not in ["blue", "green"]:
            self.dpad_color = "blue"

        # gamepad buttons from back to front
        # noinspection PyTypeChecker
        self.button_up = ButtonIcon(920, 449,
                                    [load_image(im, "buttons32") for im in
                                     (f"button_{self.dpad_color}_up.png", f"button_{self.dpad_color}_up_pressed.png")],
                                    (game_ui_sprites, game_sprites)
                                    )

        # noinspection PyTypeChecker
        self.button_select = ButtonIcon(980, 449,
                                        [load_image(im, "buttons32") for im in
                                         ("button_white.png", "button_white_pressed.png")],
                                        (game_ui_sprites, game_sprites)
                                        )

        # noinspection PyTypeChecker
        self.button_start = ButtonIcon(1015, 449,
                                       [load_image(im, "buttons32") for im in
                                        ("button_black.png", "button_black_pressed.png")],
                                       (game_ui_sprites, game_sprites)
                                       )
        self.button_start.frame = 24

        # noinspection PyTypeChecker
        self.button_left = ButtonIcon(894, 464,
                                      [load_image(im, "buttons32") for im in
                                       (f"button_{self.dpad_color}_left.png", f"button_{self.dpad_color}_left_pressed.png")],
                                      (game_ui_sprites, game_sprites)
                                      )
        self.button_left.frame = 6

        # noinspection PyTypeChecker
        self.button_right = ButtonIcon(943, 464,
                                       [load_image(im, "buttons32") for im in
                                        (f"button_{self.dpad_color}_right.png", f"button_{self.dpad_color}_right_pressed.png")],
                                       (game_ui_sprites, game_sprites)
                                       )
        self.button_right.frame = 12

        # noinspection PyTypeChecker
        self.button_red = ButtonIcon(1106, 464,
                                     [load_image(im, "buttons32") for im in
                                      ("button_red.png", "button_red_pressed.png")],
                                     (game_ui_sprites, game_sprites)
                                     )

        # noinspection PyTypeChecker
        self.button_down = ButtonIcon(914, 481,
                                      [load_image(im, "buttons32") for im in
                                       (f"button_{self.dpad_color}_down.png", f"button_{self.dpad_color}_down_pressed.png")],
                                      (game_ui_sprites, game_sprites)
                                      )
        self.button_down.frame = 24

        # noinspection PyTypeChecker
        self.button_yellow = ButtonIcon(1080, 481,
                                        [load_image(im, "buttons32") for im in
                                         ("button_yellow.png", "button_yellow_pressed.png")],
                                        (game_ui_sprites, game_sprites)
                                        )
        self.button_yellow.frame = 6

        font = load_font(42)

        self.label_text_easy = UiText((game_ui_sprites, game_sprites))
        self.label_text_easy.text = "Einfach"
        self.label_text_easy.targetRect = Rect(840,400,10,10)
        self.label_text_easy.font = font

        self.label_text_normal = UiText((game_ui_sprites, game_sprites))
        self.label_text_normal.text = "Normal"
        self.label_text_normal.targetRect = Rect(1040,400,10,10)
        self.label_text_normal.font = font

        self.label_text_left = UiText((game_ui_sprites, game_sprites))
        self.label_text_left.text = "Links"
        self.label_text_left.targetRect = Rect(760,465,10,10)
        self.label_text_left.font = font

        self.label_text_right = UiText((game_ui_sprites, game_sprites))
        self.label_text_right.text = "Rechts"
        self.label_text_right.targetRect = Rect(1142,445,10,10)
        self.label_text_right.font = font

        self.label_text_up = UiText((game_ui_sprites, game_sprites))
        self.label_text_up.text = "Hoch"
        self.label_text_up.targetRect = Rect(760,430,10,10)
        self.label_text_up.font = font

        self.label_text_jump = UiText((game_ui_sprites, game_sprites))
        self.label_text_jump.text = "Hüpfen"
        self.label_text_jump.targetRect = Rect(760,430,10,10)
        self.label_text_jump.font = font

        self.label_text_jump2 = UiText((game_ui_sprites, game_sprites))
        self.label_text_jump2.text = "Hüpfen"
        self.label_text_jump2.targetRect = Rect(1142,480,10,10)
        self.label_text_jump2.font = font

        self.label_text_down = UiText((game_ui_sprites, game_sprites))
        self.label_text_down.text = "Runter"
        self.label_text_down.targetRect = Rect(760,500,10,10)
        self.label_text_down.font = font

        self.label_text_right2 = UiText((game_ui_sprites, game_sprites))
        self.label_text_right2.text = "Rechts"
        self.label_text_right2.targetRect = Rect(760,535,10,10)
        self.label_text_right2.font = font

        self.label_text_ok = UiText((game_ui_sprites, game_sprites))
        self.label_text_ok.text = "OK"
        self.label_text_ok.targetRect = Rect(1142,445,10,10)
        self.label_text_ok.font = font

        self.label_text_del = UiText((game_ui_sprites, game_sprites))
        self.label_text_del.text = "Löschen"
        self.label_text_del.targetRect = Rect(1142,482,10,10)
        self.label_text_del.font = load_font(38)

        self.start_info_text1 = UiText((game_ui_sprites, game_sprites))
        self.start_info_text1.text = "Links/Rechts/Hüpfen"
        self.start_info_text1.targetRect = Rect(820, 640, 10, 10)
        self.start_info_text1.font = load_font(44)
        self.start_info_text2 = UiText((game_ui_sprites, game_sprites))
        self.start_info_text2.text = "erst nach Spielstart"
        self.start_info_text2.targetRect = Rect(820, 670, 10, 10)
        self.start_info_text2.font = load_font(44)

        self.label_line_easy = LineSprite(840, 435, [(5, 5), (142, 5), (155, 15)], 5, 'white',(game_ui_sprites, game_sprites))
        self.label_line_normal = LineSprite(1025, 435, [(5, 15), (18, 5), (140, 5)], 5, 'white',(game_ui_sprites, game_sprites))
        self.label_line_left = LineSprite(760,480, [(5,25), (105,25), (130,5)], 5, 'white', (game_ui_sprites, game_sprites))
        self.label_line_jump = LineSprite(760,460, [(5,10), (125,10), (155,5)], 5, 'white', (game_ui_sprites, game_sprites))
        self.label_line_right = LineSprite(1134,480, [(5,5), (135,5)], 5, 'white', (game_ui_sprites, game_sprites))
        self.label_line_right_l2 = LineSprite(975,460, [(5,25), (100,25), (120, 5), (152, 5), (172, 25)], 3, 'white', (game_ui_sprites, game_sprites))
        self.label_line_jump2 = LineSprite(1105,495, [(10,5), (40,25), (165,25)], 5, 'white', (game_ui_sprites, game_sprites))

        self.label_line_up = LineSprite(760, 460, [(5, 10), (88, 10), (93, 5), (155, 5)], 5, 'white',(game_ui_sprites, game_sprites))
        self.label_line_down = LineSprite(760,510, [(5,30), (125,30), (170,5)], 5, 'white', (game_ui_sprites, game_sprites))
        self.label_line_right2 = LineSprite(760, 495, [(5, 80), (125, 80), (200, 35), (200, 5)], 5, 'white',(game_ui_sprites, game_sprites))

        self.label_line_ok = LineSprite(1134, 480, [(5, 5), (50, 5)], 5, 'white', (game_ui_sprites, game_sprites))
        self.label_line_del = LineSprite(1105, 495, [(10, 5), (35, 25), (165, 25)], 5, 'white',(game_ui_sprites, game_sprites))

        self.reception_icon_image = pg.Surface((56,56), pg.SRCALPHA)
        self.reception_icon = ImageIcon(1222, 400, [self.reception_icon_image], (game_ui_sprites, game_sprites))
        self.reception_last_value = 0

        self.battery_icon_image = load_image("bat.png", "ui")
        self.battery_icon = ImageIcon(1236, 400, [self.battery_icon_image]) # no groups, don't show by default
        self.battery_last_value = None

    def update_rects(self):
        if self.gamestate.screenMode == ScreenMode.GAME_BIG:
            self.button_left.rect.left = 810
            self.button_left.rect.top = 330

            self.button_right.rect.left = 860
            self.button_right.rect.top = 330

            self.button_yellow.rect.left = 780
            self.button_yellow.rect.top = 370

            self.button_select.rect.left = 750
            self.button_select.rect.top = 620

            self.button_start.rect.left = 750
            self.button_start.rect.top = 670

            # unused in this screen mode
            self.button_up.rect.left = -100
            self.button_down.rect.left = -100
            self.button_red.rect.left = -100
        elif self.gamestate.screenMode == ScreenMode.SCORE_GAME_BUTTONS:
            self.button_up.rect.left = 920
            self.button_up.rect.top = 449

            self.button_left.rect.left = 894
            self.button_left.rect.top = 464

            self.button_right.rect.left = 943
            self.button_right.rect.top = 464

            self.button_down.rect.left = 914
            self.button_down.rect.top = 481

            self.button_start.rect.left = 1015
            self.button_start.rect.top = 449

            self.button_select.rect.left = 980
            self.button_select.rect.top = 449

            self.button_red.rect.left = 1106
            self.button_red.rect.top = 464

            self.button_yellow.rect.left = 1080
            self.button_yellow.rect.top = 481


    def show(self):
        game_sprites = self.gamestate.GAME_SPRITES
        game_ui_sprites = self.gamestate.GAME_UI_SPRITES

        game_sprites.remove(self.reception_icon)
        game_ui_sprites.remove(self.reception_icon)

        game_sprites.remove(self.battery_icon)
        game_ui_sprites.remove(self.battery_icon)

        game_sprites.add(self.gamepad_sprite)
        game_sprites.add(self.button_up)
        game_sprites.add(self.button_select)
        game_sprites.add(self.button_start)
        game_sprites.add(self.button_left)
        game_sprites.add(self.button_right)
        game_sprites.add(self.button_red)
        game_sprites.add(self.button_down)
        game_sprites.add(self.button_yellow)

        game_ui_sprites.add(self.gamepad_sprite)
        game_ui_sprites.add(self.button_up)
        game_ui_sprites.add(self.button_select)
        game_ui_sprites.add(self.button_start)
        game_ui_sprites.add(self.button_left)
        game_ui_sprites.add(self.button_right)
        game_ui_sprites.add(self.button_red)
        game_ui_sprites.add(self.button_down)
        game_ui_sprites.add(self.button_yellow)

        self.show_labels(self.show_labels_mode)

        game_sprites.add(self.reception_icon)
        game_ui_sprites.add(self.reception_icon)

        if self.should_show_bat():
            game_sprites.add(self.battery_icon)
            game_ui_sprites.add(self.battery_icon)

    def set_button_paused_state(self, mode):
        self.button_up.paused = True
        self.button_down.paused = True
        self.button_left.paused = True
        self.button_right.paused = True
        self.button_start.paused = True
        self.button_select.paused = True
        self.button_red.paused = True
        self.button_yellow.paused = True

        if mode == "start":
            self.button_start.paused = False
            self.button_select.paused = False
        elif mode == "game":
            self.button_left.paused = False
            self.button_right.paused = False
            self.button_up.paused = False
            self.button_red.paused = False
            self.button_yellow.paused = False
        elif mode == "name":
            self.button_up.paused = False
            self.button_down.paused = False
            self.button_left.paused = False
            self.button_right.paused = False
            self.button_red.paused = False
            self.button_yellow.paused = False


    def hide(self):
        game_sprites = self.gamestate.GAME_SPRITES
        game_ui_sprites = self.gamestate.GAME_UI_SPRITES

        self.hide_labels()

        game_sprites.remove(self.gamepad_sprite)
        game_sprites.remove(self.button_up)
        game_sprites.remove(self.button_select)
        game_sprites.remove(self.button_start)
        game_sprites.remove(self.button_left)
        game_sprites.remove(self.button_right)
        game_sprites.remove(self.button_red)
        game_sprites.remove(self.button_down)
        game_sprites.remove(self.button_yellow)

        game_ui_sprites.remove(self.gamepad_sprite)
        game_ui_sprites.remove(self.button_up)
        game_ui_sprites.remove(self.button_select)
        game_ui_sprites.remove(self.button_start)
        game_ui_sprites.remove(self.button_left)
        game_ui_sprites.remove(self.button_right)
        game_ui_sprites.remove(self.button_red)
        game_ui_sprites.remove(self.button_down)
        game_ui_sprites.remove(self.button_yellow)

    def set_mode(self, mode):
        self.show_labels_mode = mode
        self.show_labels(mode)
        self.set_button_paused_state(mode)
        self.update_dpad_color()

    def update_dpad_color(self):
        if self.dpad_color == self.gamestate.CONTROLLER_COLOR:
            return
        self.dpad_color = self.gamestate.CONTROLLER_COLOR
        if self.dpad_color not in ["blue", "green"]:
            self.dpad_color = "blue"

        self.button_up.images = [
            load_image(im, "buttons32") for im in
                (f"button_{self.dpad_color}_up.png", f"button_{self.dpad_color}_up_pressed.png")
        ]

        self.button_down.images = [
            load_image(im, "buttons32") for im in
                (f"button_{self.dpad_color}_down.png", f"button_{self.dpad_color}_down_pressed.png")
        ]

        self.button_left.images = [
            load_image(im, "buttons32") for im in
                (f"button_{self.dpad_color}_left.png", f"button_{self.dpad_color}_left_pressed.png")
        ]

        self.button_right.images = [
            load_image(im, "buttons32") for im in
                (f"button_{self.dpad_color}_right.png", f"button_{self.dpad_color}_right_pressed.png")
        ]

    def show_labels(self, mode):
        game_sprites = self.gamestate.GAME_SPRITES
        game_ui_sprites = self.gamestate.GAME_UI_SPRITES
        self.hide_labels()

        game_sprites.add(self.label_text_left)
        game_ui_sprites.add(self.label_text_left)
        game_sprites.add(self.label_line_left)
        game_ui_sprites.add(self.label_line_left)

        if mode == "start":
            game_sprites.add(self.start_info_text1)
            game_sprites.add(self.start_info_text2)
            game_ui_sprites.add(self.start_info_text1)
            game_ui_sprites.add(self.start_info_text2)

            game_sprites.add(self.label_text_easy)
            game_ui_sprites.add(self.label_text_easy)
            game_sprites.add(self.label_line_easy)
            game_ui_sprites.add(self.label_line_easy)
            game_sprites.add(self.label_text_normal)
            game_ui_sprites.add(self.label_text_normal)
            game_sprites.add(self.label_line_normal)
            game_ui_sprites.add(self.label_line_normal)
            game_sprites.add(self.label_text_jump)
            game_ui_sprites.add(self.label_text_jump)
            game_sprites.add(self.label_line_jump)
            game_ui_sprites.add(self.label_line_jump)
            game_sprites.add(self.label_text_jump2)
            game_ui_sprites.add(self.label_text_jump2)
            game_sprites.add(self.label_line_jump2)
            game_ui_sprites.add(self.label_line_jump2)
            game_sprites.add(self.label_text_right)
            game_ui_sprites.add(self.label_text_right)
            game_sprites.add(self.label_line_right)
            game_ui_sprites.add(self.label_line_right)
            game_sprites.add(self.label_line_right_l2)
            game_ui_sprites.add(self.label_line_right_l2)

        elif mode == "game":
            game_sprites.add(self.label_text_jump)
            game_ui_sprites.add(self.label_text_jump)
            game_sprites.add(self.label_line_jump)
            game_ui_sprites.add(self.label_line_jump)
            game_sprites.add(self.label_text_jump2)
            game_ui_sprites.add(self.label_text_jump2)
            game_sprites.add(self.label_line_jump2)
            game_ui_sprites.add(self.label_line_jump2)
            game_sprites.add(self.label_text_right)
            game_ui_sprites.add(self.label_text_right)
            game_ui_sprites.add(self.label_text_right)
            game_sprites.add(self.label_line_right)
            game_ui_sprites.add(self.label_line_right)
            game_sprites.add(self.label_line_right_l2)
            game_ui_sprites.add(self.label_line_right_l2)
        elif mode == "name":
            game_sprites.add(self.label_text_up)
            game_ui_sprites.add(self.label_text_up)
            game_sprites.add(self.label_line_up)
            game_ui_sprites.add(self.label_line_up)
            game_sprites.add(self.label_text_down)
            game_ui_sprites.add(self.label_text_down)
            game_sprites.add(self.label_line_down)
            game_ui_sprites.add(self.label_line_down)
            game_sprites.add(self.label_text_right2)
            game_ui_sprites.add(self.label_text_right2)
            game_sprites.add(self.label_line_right2)
            game_ui_sprites.add(self.label_line_right2)
            game_sprites.add(self.label_text_ok)
            game_ui_sprites.add(self.label_text_ok)
            game_sprites.add(self.label_line_ok)
            game_ui_sprites.add(self.label_line_ok)
            game_sprites.add(self.label_text_del)
            game_ui_sprites.add(self.label_text_del)
            game_sprites.add(self.label_line_del)
            game_ui_sprites.add(self.label_line_del)


    def hide_labels(self):
        game_sprites = self.gamestate.GAME_SPRITES
        game_ui_sprites = self.gamestate.GAME_UI_SPRITES

        game_sprites.remove(self.start_info_text1)
        game_sprites.remove(self.start_info_text2)
        game_ui_sprites.remove(self.start_info_text1)
        game_ui_sprites.remove(self.start_info_text2)

        game_sprites.remove(self.label_text_easy)
        game_ui_sprites.remove(self.label_text_easy)
        game_sprites.remove(self.label_text_normal)
        game_ui_sprites.remove(self.label_text_normal)
        game_sprites.remove(self.label_text_left)
        game_ui_sprites.remove(self.label_text_left)
        game_sprites.remove(self.label_text_right)
        game_ui_sprites.remove(self.label_text_right)
        game_sprites.remove(self.label_text_right2)
        game_ui_sprites.remove(self.label_text_right2)
        game_sprites.remove(self.label_text_up)
        game_ui_sprites.remove(self.label_text_up)
        game_sprites.remove(self.label_text_down)
        game_ui_sprites.remove(self.label_text_down)
        game_sprites.remove(self.label_text_jump)
        game_ui_sprites.remove(self.label_text_jump)
        game_sprites.remove(self.label_text_jump2)
        game_ui_sprites.remove(self.label_text_jump2)
        game_sprites.remove(self.label_text_ok)
        game_ui_sprites.remove(self.label_text_ok)
        game_sprites.remove(self.label_text_del)
        game_ui_sprites.remove(self.label_text_del)

        game_sprites.remove(self.label_line_easy)
        game_ui_sprites.remove(self.label_line_easy)
        game_sprites.remove(self.label_line_normal)
        game_ui_sprites.remove(self.label_line_normal)
        game_sprites.remove(self.label_line_left)
        game_ui_sprites.remove(self.label_line_left)
        game_sprites.remove(self.label_line_jump)
        game_ui_sprites.remove(self.label_line_jump)

        game_sprites.remove(self.label_line_right)
        game_ui_sprites.remove(self.label_line_right)
        game_sprites.remove(self.label_line_right_l2)
        game_ui_sprites.remove(self.label_line_right_l2)

        game_sprites.remove(self.label_line_jump2)
        game_ui_sprites.remove(self.label_line_jump2)

        game_sprites.remove(self.label_line_up)
        game_ui_sprites.remove(self.label_line_up)
        game_sprites.remove(self.label_line_down)
        game_ui_sprites.remove(self.label_line_down)
        game_sprites.remove(self.label_line_right2)
        game_ui_sprites.remove(self.label_line_right2)
        game_sprites.remove(self.label_line_ok)
        game_ui_sprites.remove(self.label_line_ok)
        game_sprites.remove(self.label_line_del)
        game_ui_sprites.remove(self.label_line_del)

    # https://stackoverflow.com/a/68722109
    def mapRange(self, value, inMin, inMax, outMin, outMax):
        return outMin + (((value - inMin) / (inMax - inMin)) * (outMax - outMin))

    def update_reception(self):
        if self.gamestate.CONTROLLER_CONNECTION_RECEPTION == self.reception_last_value:
            return

        self.reception_last_value = self.gamestate.CONTROLLER_CONNECTION_RECEPTION

        reception = self.gamestate.CONTROLLER_CONNECTION_RECEPTION  # seems to range  from -85 (bad) to -27 (perfect)
        reception = self.mapRange(reception, -85, -27, 0, 100)
        reception = clamp(reception, 0, 100)

        color_reception_good = Color(0, 192, 0)
        color_reception_bad = Color(192, 0, 0)

        reception_color = color_reception_bad.lerp(color_reception_good, reception / 100)

        reception_width = self.mapRange(reception, 0, 100, 2, 50)

        reception_rectangle_lower_left = (3, 53)
        reception_rectangle_lower_right = (3 + reception_width, 53)
        reception_rectangle_upper_right = (3 + reception_width, 53 - reception_width)

        self.reception_icon_image.fill(Color(0, 0, 0, 0))
        pg.draw.polygon(self.reception_icon_image, reception_color, (
        reception_rectangle_lower_left, reception_rectangle_upper_right, reception_rectangle_lower_right))

    def should_show_bat(self):
        return self.gamestate.CONTROLLER_VBAT is not None

    def update_bat(self):
        if self.gamestate.CONTROLLER_VBAT == self.battery_last_value:
            return

        if self.battery_last_value is None:
            self.reception_icon.rect.left -= 45
            self.gamestate.GAME_SPRITES.add(self.battery_icon)
            self.gamestate.GAME_UI_SPRITES.add(self.battery_icon)

        vbat = self.gamestate.CONTROLLER_VBAT #
        self.battery_last_value = vbat
        '''
        https://learn.adafruit.com/adafruit-feather-32u4-radio-with-rfm69hcw-module?view=all#measuring-battery-3122383 :
        > LiPoly batteries are 'maxed out' at 4.2V and stick around 3.7V for much of the battery life,
        > then slowly sink down to 3.2V or so before the protection circuitry cuts it off.
        See also graphs online. I bought 1C rated Lithium battery:
        https://www.dnkpower.com/wp-content/uploads/2019/01/discharging-curve-lipo-battery.png
        100% - 15% ≈ 4.0V - 3.45
        15% - 0% ≈ 3.45 - 3.2
        '''
        if vbat > 3.45:
            vbat_percent = self.mapRange(vbat, 3.45, 4.0, 15, 100)
        else:
            vbat_percent = self.mapRange(vbat, 3.2, 3.45, 0, 15)

        # todo: check if true
        charging = vbat_percent>130 # >4.2V

        vbat_percent = clamp(vbat_percent, 0, 100)

        color_bat_good = Color(0, 192, 0)
        color_bat_bad = Color(192, 0, 0)

        bat_color = color_bat_bad.lerp(color_bat_good, vbat_percent / 100)
        transparent_color = Color(0,0,0,0)

        bat_fill_height = self.mapRange(vbat_percent, 0, 100, 1, 37)
        bat_top = 12
        bat_left = 7
        bat_inner_height = 37
        bat_inner_width = 28
        bat_fill_top = bat_top + bat_inner_height - int(bat_fill_height)

        self.battery_icon_image.fill(transparent_color, Rect(bat_left, bat_top, bat_inner_width, bat_inner_height))
        self.battery_icon_image.fill(bat_color, Rect(bat_left, bat_fill_top, bat_inner_width, bat_fill_height))

        # top corners
        bat_right = bat_left+bat_inner_width
        bat_bottom = bat_top+bat_inner_height
        if bat_fill_top == bat_top:
            self.battery_icon_image.set_at((bat_left,bat_top), transparent_color)
            self.battery_icon_image.set_at((bat_left+1,bat_top), transparent_color)
            self.battery_icon_image.set_at((bat_right-1,bat_top), transparent_color)
            self.battery_icon_image.set_at((bat_right-2,bat_top), transparent_color)
        if bat_fill_top <= bat_top+1:
            self.battery_icon_image.set_at((bat_left,bat_top+1), transparent_color)
            self.battery_icon_image.set_at((bat_right-1,bat_top+1), transparent_color)

        # lower left corner
        self.battery_icon_image.set_at((bat_left, bat_bottom-1), transparent_color)
        self.battery_icon_image.set_at((bat_left+1, bat_bottom-1), transparent_color)
        self.battery_icon_image.set_at((bat_left, bat_bottom-2), transparent_color)

        # lower right corner
        self.battery_icon_image.set_at((bat_right-1, bat_bottom-1), transparent_color)
        self.battery_icon_image.set_at((bat_right-2, bat_bottom-1), transparent_color)
        self.battery_icon_image.set_at((bat_right-1, bat_bottom-2), transparent_color)

        if charging:
            pg.draw.polygon(self.battery_icon_image, transparent_color, ((21,32), (12,32), (21,16), (21,45), (30,28), (21,28)))

    def update(self):
        # todo: where to call this from?
        self.frame += 1
        if self.gamestate.screenMode != self.previous_screen_mode:
            self.update_rects()
        self.update_reception()
        self.update_bat()