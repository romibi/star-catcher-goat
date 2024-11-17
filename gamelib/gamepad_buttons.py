from config.gameconfig import ScreenMode
from gamelib.data_helper_functions import load_image
from gamelib.gamestate import GameState
from gamelib.uielements import ButtonIcon, ImageIcon


class Gamepad_Buttons():

    def __init__(self, state: GameState):
        self.gamestate = state
        self.frame = 0
        self.previous_screen_mode = None

        game_sprites = self.gamestate.GAME_SPRITES
        game_ui_sprites = self.gamestate.GAME_UI_SPRITES

        # todo: make gamepad sprite non transparent? or why are (old?) sprites behind gamepad visible?
        self.gamepad_sprite = ImageIcon(873,454, [load_image('gamepad.png', 'ui')], game_ui_sprites)

        # gamepad buttons from back to front
        # noinspection PyTypeChecker
        self.button_up = ButtonIcon(960, 449,
                                    [load_image(im, "buttons32") for im in
                                     ("button_blue_up.png", "button_blue_up_pressed.png")],
                                    (game_ui_sprites, game_sprites)
                                    )

        # noinspection PyTypeChecker
        self.button_select = ButtonIcon(1020, 449,
                                        [load_image(im, "buttons32") for im in
                                         ("button_white.png", "button_white_pressed.png")],
                                        (game_ui_sprites, game_sprites)
                                        )

        # noinspection PyTypeChecker
        self.button_start = ButtonIcon(1055, 449,
                                       [load_image(im, "buttons32") for im in
                                        ("button_black.png", "button_black_pressed.png")],
                                       (game_ui_sprites, game_sprites)
                                       )
        self.button_start.frame = 24

        # noinspection PyTypeChecker
        self.button_left = ButtonIcon(934, 464,
                                      [load_image(im, "buttons32") for im in
                                       ("button_blue_left.png", "button_blue_left_pressed.png")],
                                      (game_ui_sprites, game_sprites)
                                      )
        self.button_left.frame = 6

        # noinspection PyTypeChecker
        self.button_right = ButtonIcon(983, 464,
                                       [load_image(im, "buttons32") for im in
                                        ("button_blue_right.png", "button_blue_right_pressed.png")],
                                       (game_ui_sprites, game_sprites)
                                       )
        self.button_right.frame = 12

        # noinspection PyTypeChecker
        self.button_red = ButtonIcon(1146, 464,
                                     [load_image(im, "buttons32") for im in
                                      ("button_red.png", "button_red_pressed.png")],
                                     (game_ui_sprites, game_sprites)
                                     )

        # noinspection PyTypeChecker
        self.button_down = ButtonIcon(954, 481,
                                      [load_image(im, "buttons32") for im in
                                       ("button_blue_down.png", "button_blue_down_pressed.png")],
                                      (game_ui_sprites, game_sprites)
                                      )
        self.button_down.frame = 24

        # noinspection PyTypeChecker
        self.button_yellow = ButtonIcon(1120, 481,
                                        [load_image(im, "buttons32") for im in
                                         ("button_yellow.png", "button_yellow_pressed.png")],
                                        (game_ui_sprites, game_sprites)
                                        )
        self.button_yellow.frame = 6


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
            self.button_up.rect.left = 960
            self.button_up.rect.top = 449

            self.button_left.rect.left = 934
            self.button_left.rect.top = 464

            self.button_right.rect.left = 983
            self.button_right.rect.top = 464

            self.button_down.rect.left = 954
            self.button_down.rect.top = 481

            self.button_start.rect.left = 1055
            self.button_start.rect.top = 449

            self.button_select.rect.left = 1020
            self.button_select.rect.top = 449

            self.button_red.rect.left = 1146
            self.button_red.rect.top = 464

            self.button_yellow.rect.left = 1120
            self.button_yellow.rect.top = 481

    def update(self):
        # todo: where to call this from?
        self.frame += 1
        if self.gamestate.screenMode != self.previous_screen_mode:
            self.update_rects()

        # todo: add/render labels

        # self.button_up.update()
        # self.button_down.update()
        # self.button_right.update()
        # self.button_left.update()
        # self.button_start.update()
        # self.button_select.update()
        # self.button_red.update()
        # self.button_yellow.update()
