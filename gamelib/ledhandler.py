import threading
from multiprocessing.spawn import old_main_modules

import grequests
from pygame import Color

from config.ledconfig import *
from config.gameconfig import GameConfig

class LedHandler:
    STAR_COLOR = 'FF9000'

    GOAT_BODY_COLOR_RGB = Color(255,200,125)
    GOAT_BODY_COLOR_GLOW_RGB = Color(255, 144, 0)
    GOAT_HORN_COLOR_RGB = Color(255, 220, 150)
    GOAT_HORN_COLOR_GLOW_RGB = Color(255,144, 0)

    GOAT_BODY_COLOR = 'FF9000'
    GOAT_HORN_COLOR = 'FF9000'

    BRIGHTNESS_MOD = 0 # modifying 0=ALL, 1=A, 2=B, 3=G
    STAR_BRIGHTNESS_A = 255 # row 0-2
    STAR_BRIGHTNESS_B = 255 # row 3-5
    GOAT_BRIGHTNESS = 255

    # todo: configure somewhere else?
    GOAT_POS_NUMS = 6

    # change color of segment 1 (0) to green: http://192.168.1.107/win&SM=0&SB=255&CL=H00FF00
    API_ADDR = '/win'
    API_ARG_SEGMENT = '&SM='
    API_ARG_BRIGHTNESS = '&SB='
    API_ARG_COLOR = '&CL=H'


    # Segment map for when only halve the stars are wired:
    #ledSegmentMap3 = [
    #   [ {"hub": 1, "segment": 2},                                                     {"hub": 2, "segment": 2}, {"hub": 3, "segment": 2}                          ],
    #   [                           {"hub": 1, "segment": 1}, {"hub": 2, "segment": 1},                                                     {"hub": 3, "segment": 1}],
    #   [ {"hub": 1, "segment": 0},                                                     {"hub": 2, "segment": 0}, {"hub": 3, "segment": 0}                          ],
    #
    #   [                           {"hub": 4, "segment": 2},                           {"hub": 5, "segment": 2},                           {"hub": 6, "segment": 2}],
    #   [ {"hub": 4, "segment": 1},                           {"hub": 5, "segment": 1},                           {"hub": 6, "segment": 1},                         ],
    #   [                           {"hub": 4, "segment": 0},                           {"hub": 5, "segment": 0},                           {"hub": 6, "segment": 0}]
    #]

    # Segment map for when 6x6 stars are wired but game is in 3x6 mode:
    ledSegmentMap3 = [
       [ {"hub": 1, "segment": 2},                                                     {"hub": 2, "segment": 3}, {"hub": 3, "segment": 2}                          ],
       [                           {"hub": 1, "segment": 4}, {"hub": 2, "segment": 1},                                                     {"hub": 3, "segment": 4}],
       [ {"hub": 1, "segment": 0},                                                     {"hub": 2, "segment": 5}, {"hub": 3, "segment": 0}                          ],

       [                           {"hub": 4, "segment": 3},                           {"hub": 5, "segment": 3},                           {"hub": 6, "segment": 3}],
       [ {"hub": 4, "segment": 1},                           {"hub": 5, "segment": 1},                           {"hub": 6, "segment": 1},                         ],
       [                           {"hub": 4, "segment": 5},                           {"hub": 5, "segment": 5},                           {"hub": 6, "segment": 5}]
    ]

    ledSegmentMap6 = [
       [ {"hub": 1, "segment": 2}, {"hub": 1, "segment": 3}, {"hub": 2, "segment": 2}, {"hub": 2, "segment": 3}, {"hub": 3, "segment": 2}, {"hub": 3, "segment": 3}],
       [ {"hub": 1, "segment": 1}, {"hub": 1, "segment": 4}, {"hub": 2, "segment": 1}, {"hub": 2, "segment": 4}, {"hub": 3, "segment": 1}, {"hub": 3, "segment": 4}],
       [ {"hub": 1, "segment": 0}, {"hub": 1, "segment": 5}, {"hub": 2, "segment": 0}, {"hub": 2, "segment": 5}, {"hub": 3, "segment": 0}, {"hub": 3, "segment": 5}],

       [ {"hub": 4, "segment": 2}, {"hub": 4, "segment": 3}, {"hub": 5, "segment": 2}, {"hub": 5, "segment": 3}, {"hub": 6, "segment": 2}, {"hub": 6, "segment": 3}],
       [ {"hub": 4, "segment": 1}, {"hub": 4, "segment": 4}, {"hub": 5, "segment": 1}, {"hub": 5, "segment": 4}, {"hub": 6, "segment": 1}, {"hub": 6, "segment": 4}],
       [ {"hub": 4, "segment": 0}, {"hub": 4, "segment": 5}, {"hub": 5, "segment": 0}, {"hub": 5, "segment": 5}, {"hub": 6, "segment": 0}, {"hub": 6, "segment": 5}]
    ]

    ledSegmentMap = None # initialized in setup/reset

    hubs = {}
    stars = {}
    leds = {}

    goatSegmentMap = [
        {"hub": 1, "body_segments": [0, 2], "horn_segments": [1]},
        {"hub": 1, "body_segments": [3, 5], "horn_segments": [4]},
        {"hub": 2, "body_segments": [0, 2], "horn_segments": [1]},
        {"hub": 2, "body_segments": [3, 5], "horn_segments": [4]},
        {"hub": 3, "body_segments": [0, 2], "horn_segments": [1]},
        {"hub": 3, "body_segments": [3, 5], "horn_segments": [4]}
    ]
    goat_hubs = {}
    goats = {}
    goat_leds = {}

    # todo: add goat leds

    def __init__(self, game_config: GameConfig):
        self.game_config = game_config
        self.active = -1 # 0: no, 1: yes, -1: active unless first request fails
        self.reset()


    def reset(self):
        self.hubs = {}
        self.stars = {}
        self.leds = {}
        self.goat_hubs = {}
        self.goats = {}
        self.goat_leds = {}

        if HUB_ADDR_STAR_1 != '':
            self.add_star_hub(1, HUB_ADDR_STAR_1)
        if HUB_ADDR_STAR_2 != '':
            self.add_star_hub(2, HUB_ADDR_STAR_2)
        if HUB_ADDR_STAR_3 != '':
            self.add_star_hub(3, HUB_ADDR_STAR_3)
        if HUB_ADDR_STAR_4 != '':
            self.add_star_hub(4, HUB_ADDR_STAR_4)
        if HUB_ADDR_STAR_5 != '':
            self.add_star_hub(5, HUB_ADDR_STAR_5)
        if HUB_ADDR_STAR_6 != '':
            self.add_star_hub(6, HUB_ADDR_STAR_6)

        for row in range(self.game_config.ROWS):
            self.stars[row] = {}
            self.leds[row] = {}
            for column in range(self.game_config.COLUMNS):
                self.stars[row][column] = {}
                self.leds[row][column] = {}

        if HUB_ADDR_GOAT_1 != '':
            self.add_goat_hub(1, HUB_ADDR_GOAT_1)
        if HUB_ADDR_GOAT_2 != '':
            self.add_goat_hub(2, HUB_ADDR_GOAT_2)
        if HUB_ADDR_GOAT_3 != '':
            self.add_goat_hub(3, HUB_ADDR_GOAT_3)

        for pos in range(self.GOAT_POS_NUMS):
            self.goats[pos] = {}
            self.goat_leds[pos] = {}


    def add_star_hub(self, num, address):
        self.hubs[num] = address


    def add_goat_hub(self, num, address):
        self.goat_hubs[num] = address


    def get_star_hub(self, row, column):
        if self.ledSegmentMap:
            segment = self.ledSegmentMap[row][column]
            hub = segment["hub"]
            return self.hubs.get(hub, None)
        return ''

    def get_goat_hub(self, pos):
        if self.goatSegmentMap:
            hub = self.goatSegmentMap[pos]["hub"]
            return self.goat_hubs.get(hub, None)
        return ''


    def get_led_api_url(self, row, column, bright, color):
        hub = self.get_star_hub(row, column)
        if not hub:
            return None
  
        segment = self.ledSegmentMap[row][column]

        return f'http://{hub}{self.API_ADDR}{self.API_ARG_SEGMENT}{segment["segment"]}{self.API_ARG_BRIGHTNESS}{bright}{self.API_ARG_COLOR}{color}&SV=2'


    def get_goat_led_api_urls(self, pos, body, horn, bright, body_color, horn_color):
        hub = self.get_goat_hub(pos)
        if not hub:
            return None

        urls = []
        if body:
            for segment in self.goatSegmentMap[pos]["body_segments"]:
                urls += [f'http://{hub}{self.API_ADDR}{self.API_ARG_SEGMENT}{segment}{self.API_ARG_BRIGHTNESS}{bright}{self.API_ARG_COLOR}{body_color}&SV=2']
        if horn:
            for segment in self.goatSegmentMap[pos]["horn_segments"]:
                urls += [f'http://{hub}{self.API_ADDR}{self.API_ARG_SEGMENT}{segment}{self.API_ARG_BRIGHTNESS}{bright}{self.API_ARG_COLOR}{horn_color}&SV=2']

        return urls


    def set_star_led(self, row, column, bright, color=None):
        self.stars[row][column]['bright'] = bright
        if not 'color' in self.stars[row][column]:
            self.stars[row][column]['color'] = self.STAR_COLOR
        if color:
            self.stars[row][column]['color'] = color


    def set_goat_led(self, pos, bright=None, body_color=None, horn_color=None):
        old_bright = None
        if 'bright' in self.goats[pos]:
            old_bright = self.goats[pos]['bright']
        for loop_pos in range(self.GOAT_POS_NUMS):
            self.goats[loop_pos]['bright'] = 0
            if not 'body_color' in self.goats[pos]:
                self.goats[loop_pos]['body_color'] = self.GOAT_BODY_COLOR
            if not 'horn_color' in self.goats[pos]:
                self.goats[loop_pos]['horn_color'] = self.GOAT_HORN_COLOR

        if bright:
            self.goats[pos]['bright'] = bright
        elif old_bright:
            self.goats[pos]['bright'] = old_bright
        if body_color:
            self.goats[pos]['body_color'] = body_color
        if horn_color:
            self.goats[pos]['horn_color'] = horn_color
        # print(f'Setting Goat Pos {pos} to {bright} brightness, body color {body_color} horn color {horn_color}')


    def set_all_leds_off(self, only_stars=False):
        for row, starRow in self.stars.items():
            for column, star in starRow.items():
                self.set_star_led(row, column, 0)

        if not only_stars:
            self.set_goat_led(0,0) # Setting any goat brightness sets all others to 0


    def update_brightness(self, new_brightness_a, new_brightness_b, new_brightness_g):
        for row, starRow in self.stars.items():
            for column, star in starRow.items():
                if star.get('bright', 0) > 0:
                    if row > 2:
                        star['bright'] = new_brightness_b
                    else:
                        star['bright'] = new_brightness_a
        for pos, goat in self.goats.items():
            if goat.get('bright', 0) > 0:
                goat['bright'] = new_brightness_g


    def collect_star_update_call_urls(self):
        urls = []
        for row, starRow in self.stars.items():
            for column, star in starRow.items():
                led = self.leds[row][column]

                star_brightness = star.get('bright', 0)
                led_brightness = led.get('bright', None)

                star_color = star.get('color', self.STAR_COLOR)
                led_color = star.get('color', None)

                if (star_brightness == led_brightness) and (star_color == led_color):
                    continue

                self.leds[row][column]['bright'] = star_brightness
                self.leds[row][column]['color'] = star_color

                api_url = self.get_led_api_url(row, column, star_brightness, star_color)
                if not api_url:
                    continue

                urls += [api_url]
                # print(f"Adding url for star row: {row} column: {column} to request: {api_url}")
        return urls


    def collect_goat_update_call_urls(self):
        urls = []
        for pos, goat in self.goats.items():
            led = self.goat_leds[pos]

            goat_brightness = goat.get('bright', 0)
            led_brightness = led.get('bright', None)

            goat_body_color = goat.get('body_color', self.GOAT_BODY_COLOR)
            led_body_color = led.get('body_color', None)

            goat_horn_color = goat.get('horn_color', self.GOAT_HORN_COLOR)
            led_horn_color = led.get('horn_color', None)

            if (goat_brightness == led_brightness) and (goat_horn_color == led_horn_color) and (
                    goat_body_color == led_body_color):
                continue

            self.goat_leds[pos]['bright'] = goat_brightness
            self.goat_leds[pos]['body_color'] = goat_body_color
            self.goat_leds[pos]['horn_color'] = goat_horn_color

            update_body = (goat_brightness != led_brightness) or (goat_body_color != led_body_color)
            update_horn = (goat_brightness != led_brightness) or (goat_horn_color != led_horn_color)

            api_urls = self.get_goat_led_api_urls(pos, update_body, update_horn, goat_brightness, goat_body_color,
                                                  goat_horn_color)
            if not api_urls:
                continue
            urls += api_urls
        return urls


    def update_leds(self, update_stars=True, update_goats=True):
        if self.active == 0:
            return

        urls = []

        if update_stars:
            urls += self.collect_star_update_call_urls()

        if update_goats:
            urls += self.collect_goat_update_call_urls()

        rs = (grequests.get(u, timeout=5) for u in urls)

        # noinspection PyShadowingNames
        def call_map(rs, exception_handler):
            grequests.map(rs, exception_handler=exception_handler)

        if self.active == -1:
            self.active = 1

            # noinspection PyUnusedLocal
            def exception_handler(request, exception):
                self.active = 0            
            threading.Thread(target=call_map, args=(rs,exception_handler)).start()
        else:
            threading.Thread(target=call_map, args=(rs,None)).start()

