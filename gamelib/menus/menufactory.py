import pygame as pg
import serial
import serial.tools.list_ports

from config.buttonconfig import *

from gamelib.gamestate import GameState
from gamelib.menus.menuscreen import MenuScreen

class MenuFactory():
    def __init__(self, state: GameState):
        self.gamestate = state


    def _closeMenu(self, key):
        self.gamestate.CURRENT_MENU = False
        self.gamestate.MENU_JUST_CLOSED = True


    def _quitGame(self, key):
        self.gamestate.GAME_QUIT = True


    def _reset3(self, key):
        self._closeMenu(key)
        self.gamestate.reset(3)


    def _reset6(self, key):
        self._closeMenu(key)
        self.gamestate.reset(6)


    def _ledText(self):
        if self.gamestate.LED_HANDLER.active == 1:
            return "LED Ein/Aus: EIN"
        else:
            return "LED Ein/Aus: AUS"

    def _ledToggleActive(self, key):
        leds = self.gamestate.LED_HANDLER

        if leds.active == 1:
            leds.SetAllLedsOff()
            leds.UpdateLeds()
            leds.active = 0
        else:
            leds.active = 1


    def _ledBrightText(self):
        leds = self.gamestate.LED_HANDLER
        if (leds.BRIGHTNESS_MOD != 0) or (leds.STAR_BRIGHTNESS_A != leds.STAR_BRIGHTNESS_B) or (leds.STAR_BRIGHTNESS_A != leds.GOAT_BRIGHTNESS) or (leds.STAR_BRIGHTNESS_B != leds.GOAT_BRIGHTNESS):
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

    def _ledBright(self, key):
        modifiers = pg.key.get_mods()
        leds = self.gamestate.LED_HANDLER

        if ((key == pg.K_RETURN) and (modifiers & pg.KMOD_LSHIFT)) or (key in BUTTONS_MENU_DENY):
            leds.BRIGHTNESS_MOD += 1
            if leds.BRIGHTNESS_MOD>3:
                leds.BRIGHTNESS_MOD = 0
            return

        modVal = 10
        if modifiers & pg.KMOD_LSHIFT:
            modVal = 1
        elif modifiers & pg.KMOD_LCTRL:
            modVal = 50

        if key in BUTTONS_MENU_LEFT:
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 1:
                leds.STAR_BRIGHTNESS_A = max(leds.STAR_BRIGHTNESS_A-modVal, 1)
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 2:
                leds.STAR_BRIGHTNESS_B = max(leds.STAR_BRIGHTNESS_B-modVal, 1)
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 3:
                leds.GOAT_BRIGHTNESS = max(leds.GOAT_BRIGHTNESS-modVal, 1)
        if key in BUTTONS_MENU_RIGHT:
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 1:
                leds.STAR_BRIGHTNESS_A = min(leds.STAR_BRIGHTNESS_A+modVal, 255)
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 2:
                leds.STAR_BRIGHTNESS_B = min(leds.STAR_BRIGHTNESS_B+modVal, 255)
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 3:
                leds.GOAT_BRIGHTNESS = min(leds.GOAT_BRIGHTNESS+modVal, 255)
        if key in BUTTONS_MENU_CONFIRM:
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 1:
                if leds.STAR_BRIGHTNESS_A > 255/2:
                    newBright = 10
                else:
                    newBright = 255
            if leds.BRIGHTNESS_MOD == 2:
                if leds.STAR_BRIGHTNESS_B > 255/2:
                    newBright = 10
                else:
                    newBright = 255
            if leds.BRIGHTNESS_MOD == 3:                
                if leds.GOAT_BRIGHTNESS > 255/2:
                    newBright = 10
                else:
                    newBright = 255            

            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 1:
                leds.STAR_BRIGHTNESS_A = newBright
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 2:
                leds.STAR_BRIGHTNESS_B = newBright
            if leds.BRIGHTNESS_MOD == 0 or leds.BRIGHTNESS_MOD == 3:
                leds.GOAT_BRIGHTNESS = newBright            
        leds.UpdateBrightness(leds.STAR_BRIGHTNESS_A, leds.STAR_BRIGHTNESS_B, leds.GOAT_BRIGHTNESS)
        leds.UpdateLeds()


    def _controllerText(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if self.gamestate.CONTROLLER_COM_ADDR == port.device:
                if self.gamestate.CONTROLLER_COM:
                    return f"[X] Serial Controller: {port.description}"
                else:
                    return f"[ ] Serial Controller: {port.description}"
        self.gamestate.CONTROLLER_COM = None
        return f"[ ] Controller Commands Device: <none>"

    def _controllerAction(self, key):
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
                self.gamestate.CONTROLLER_COM.write(bytes(f"serial off", 'utf-8'))
                self.gamestate.CONTROLLER_COM.flush()
                self.gamestate.CONTROLLER_COM = None
            else:
                try:
                    self.gamestate.CONTROLLER_COM = serial.Serial(port=ports[new_index].device, baudrate=9600, timeout=.1)
                    self.gamestate.CONTROLLER_COM.write(bytes(f"serial on", 'utf-8'))
                    self.gamestate.CONTROLLER_COM.flush()
                except:
                    self.gamestate.CONTROLLER_COM = None


    def _controllerSoundText(self):
        if self.gamestate.CONTROLLER_PLAY_CATCH_SOUND:
            return "Controller Sounds: Viel"
        else:
            return "Controller Sounds: Wenig"

    def _toggleControllerSound(self, key):
        self.gamestate.CONTROLLER_PLAY_CATCH_SOUND = not self.gamestate.CONTROLLER_PLAY_CATCH_SOUND
       



    def FullMenu(self):
        return MenuScreen(self.gamestate,
            {"Zurück zum Spiel": self._closeMenu,
             self._ledText: self._ledToggleActive,
             self._ledBrightText: self._ledBright,
             self._controllerText: self._controllerAction,
             self._controllerSoundText: self._toggleControllerSound,
             "Neues Spiel (Normal)": self._reset6,
             "Neues Spiel (Einfach)": self._reset3,
             "Spiel Beenden": self._quitGame
             })