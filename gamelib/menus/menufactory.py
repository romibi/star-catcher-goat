import serial
import serial.tools.list_ports

from config.buttonconfig import *

from gamelib.gamestate import GameState
from gamelib.menus.controllerconnectionscreen import ControllerConnectionScreen
from gamelib.menus.menuscreen import MenuScreen
from gamelib.menus.nameentryscreen import NameEntryScreen
from gamelib.menus.startmenuscreen import StartMenuScreen


class MenuFactory:
    def __init__(self, state: GameState):
        self.gamestate = state

    def _close_menu(self, key):
        self.gamestate.CURRENT_MENU = False
        self.gamestate.MENU_JUST_CLOSED = True

    def _quit_game(self, key):
        self.gamestate.GAME_QUIT = True

    def _reset3(self, key):
        self._close_menu(key)
        self.gamestate.reset(3)

    def _reset6(self, key):
        self._close_menu(key)
        self.gamestate.reset(6)

    def _led_text(self):
        if self.gamestate.LED_HANDLER.active == 1:
            return "LED Ein/Aus: EIN"
        else:
            return "LED Ein/Aus: AUS"

    def _led_toggle_active(self, key):
        leds = self.gamestate.LED_HANDLER

        if leds.active == 1:
            leds.set_all_leds_off()
            leds.update_leds()
            leds.active = 0
        else:
            leds.active = 1

    def _led_brightness_text(self):
        leds = self.gamestate.LED_HANDLER
        if (leds.BRIGHTNESS_MOD != 0) or (leds.STAR_BRIGHTNESS_A != leds.STAR_BRIGHTNESS_B) or (
                leds.STAR_BRIGHTNESS_A != leds.GOAT_BRIGHTNESS) or (leds.STAR_BRIGHTNESS_B != leds.GOAT_BRIGHTNESS):
            if leds.BRIGHTNESS_MOD == 0:
                return f"LED Helligkeit: [{leds.STAR_BRIGHTNESS_A}|{leds.STAR_BRIGHTNESS_B}|{leds.GOAT_BRIGHTNESS}]"
            elif leds.BRIGHTNESS_MOD == 1:
                return f"LED Helligkeit: [{leds.STAR_BRIGHTNESS_A}]|{leds.STAR_BRIGHTNESS_B}|{leds.GOAT_BRIGHTNESS}"
            elif leds.BRIGHTNESS_MOD == 2:
                return f"LED Helligkeit: {leds.STAR_BRIGHTNESS_A}|[{leds.STAR_BRIGHTNESS_B}]|{leds.GOAT_BRIGHTNESS}"
            elif leds.BRIGHTNESS_MOD == 3:
                return f"LED Helligkeit: {leds.STAR_BRIGHTNESS_A}|{leds.STAR_BRIGHTNESS_B}|[{leds.GOAT_BRIGHTNESS}]"
        else:
            return f"LED Helligkeit: {leds.STAR_BRIGHTNESS_A}"

    def _led_brightness(self, key):
        modifiers = pg.key.get_mods()
        leds = self.gamestate.LED_HANDLER

        if ((key == pg.K_RETURN) and (modifiers & pg.KMOD_LSHIFT)) or (key in BUTTONS_MENU_DENY):
            leds.BRIGHTNESS_MOD += 1
            if leds.BRIGHTNESS_MOD > 3:
                leds.BRIGHTNESS_MOD = 0
            return

        mod = 10
        if modifiers & pg.KMOD_LSHIFT:
            mod = 1
        elif modifiers & pg.KMOD_LCTRL:
            mod = 50

        if key in BUTTONS_MENU_LEFT:
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 1:
                leds.STAR_BRIGHTNESS_A = max(leds.STAR_BRIGHTNESS_A - mod, 1)
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 2:
                leds.STAR_BRIGHTNESS_B = max(leds.STAR_BRIGHTNESS_B - mod, 1)
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 3:
                leds.GOAT_BRIGHTNESS = max(leds.GOAT_BRIGHTNESS - mod, 1)
        if key in BUTTONS_MENU_RIGHT:
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 1:
                leds.STAR_BRIGHTNESS_A = min(leds.STAR_BRIGHTNESS_A + mod, 255)
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 2:
                leds.STAR_BRIGHTNESS_B = min(leds.STAR_BRIGHTNESS_B + mod, 255)
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 3:
                leds.GOAT_BRIGHTNESS = min(leds.GOAT_BRIGHTNESS + mod, 255)
        if key in BUTTONS_MENU_CONFIRM:
            new_brightness = 0
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 1:
                if leds.STAR_BRIGHTNESS_A > 255 / 2:
                    new_brightness = 10
                else:
                    new_brightness = 255
            if leds.BRIGHTNESS_MOD == 2:
                if leds.STAR_BRIGHTNESS_B > 255 / 2:
                    new_brightness = 10
                else:
                    new_brightness = 255
            if leds.BRIGHTNESS_MOD == 3:
                if leds.GOAT_BRIGHTNESS > 255 / 2:
                    new_brightness = 10
                else:
                    new_brightness = 255

            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 1:
                leds.STAR_BRIGHTNESS_A = new_brightness
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 2:
                leds.STAR_BRIGHTNESS_B = new_brightness
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 3:
                leds.GOAT_BRIGHTNESS = new_brightness
        leds.update_brightness(leds.STAR_BRIGHTNESS_A, leds.STAR_BRIGHTNESS_B, leds.GOAT_BRIGHTNESS)
        leds.update_leds()

    def _controller_text(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if self.gamestate.CONTROLLER_COM_ADDR == port.device:
                if self.gamestate.CONTROLLER_COM:
                    return f"[X] Serial Controller: {port.description}"
                else:
                    return f"[ ] Serial Controller: {port.description}"
        self.gamestate.CONTROLLER_COM = None
        return f"[ ] Controller Commands Device: <none>"

    def _controller_action(self, key):
        ports = serial.tools.list_ports.comports()
        current_index = -1
        i = 0
        for port in ports:
            print(f"Port {i}: {port.device}: {port.description}")
            if self.gamestate.CONTROLLER_COM_ADDR == port.device:
                current_index = i
            i += 1

        new_index = current_index

        if key in BUTTONS_MENU_LEFT:
            new_index -= 1
        if key in BUTTONS_MENU_RIGHT:
            new_index += 1

        if (new_index < -1) or (new_index >= len(ports)):
            new_index = -1

        if new_index >= 0:
            self.gamestate.CONTROLLER_COM_ADDR = ports[new_index].device
        else:
            self.gamestate.CONTROLLER_COM_ADDR = ''

        if key in BUTTONS_MENU_CONFIRM:
            if self.gamestate.CONTROLLER_COM:
                try:
                    # todo: decide: deprecate serial off?
                    self.gamestate.CONTROLLER_COM.write(bytes(f"serial off\n", 'utf-8'))
                    self.gamestate.CONTROLLER_COM.flush()
                    self.gamestate.CONTROLLER_COM = None
                except:
                    pass
            else:
                try:
                    self.gamestate.CONTROLLER_COM = serial.Serial(port=ports[new_index].device, baudrate=9600,
                                                                  timeout=.1)
                    # todo: decide: deprecate serial off?
                    self.gamestate.CONTROLLER_COM.write(bytes(f"serial on\n", 'utf-8'))
                    self.gamestate.CONTROLLER_COM.flush()
                except:  # noqa
                    self.gamestate.CONTROLLER_COM = None

    def _controller_sound_text(self):
        if self.gamestate.CONTROLLER_PLAY_CATCH_SOUND:
            return "Controller Sounds: Viel"
        else:
            return "Controller Sounds: Wenig"

    def _toggle_controller_sound(self, key):
        self.gamestate.CONTROLLER_PLAY_CATCH_SOUND = not self.gamestate.CONTROLLER_PLAY_CATCH_SOUND

    # todo: maybe fix warnings
    def FullMenu(self, next_menu=None):  # noqa
        return MenuScreen(self.gamestate,
            {"Zurück zum Spiel": "close_menu",
             self._led_text: self._led_toggle_active,
             self._led_brightness_text: self._led_brightness,
             self._controller_text: self._controller_action,
             self._controller_sound_text: self._toggle_controller_sound,
             "Neues Spiel (Normal)": self._reset6,
             "Neues Spiel (Einfach)": self._reset3,
             "Spiel Beenden": self._quit_game
             },
            {"controller_dc": self.ControllerConnection},
            next_menu=next_menu)

    def StartMenu(self, re_render_scores_callback):
        return StartMenuScreen(self.gamestate, {"controller_dc": self.ControllerConnection, "fullmenu": self.FullMenu}, re_render_scores_callback)

    def NameEntry(self, confirm_callback, re_render_scores_callback):
        return NameEntryScreen(self.gamestate, confirm_callback, self.StartMenu(re_render_scores_callback),
                               {"controller_dc": self.ControllerConnection, "fullmenu": self.FullMenu})

    def ControllerConnection(self, next_menu):
        return ControllerConnectionScreen(self.gamestate, next_menu)
