import threading
import grequests

from config.ledconfig import *
from config.gameconfig import GameConfig

class LedHandler:
    STAR_COLOR = 'FF9000'
    BRIGHTNESS_MOD = 0 # modifying 0=ALL, 1=A, 2=B, 3=G
    STAR_BRIGHTNESS_A = 255 # row 0-2
    STAR_BRIGHTNESS_B = 255 # row 3-5
    GOAT_BRIGHTNESS = 255

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
    # todo: add goat leds

    def __init__(self, game_config: GameConfig):
        self.game_config = game_config
        self.active = -1 # 0: no, 1: yes, -1: active unless first request fails
        self.reset()


    def reset(self):
        self.hubs = {}
        self.stars = {}
        self.leds = {}

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



    def add_star_hub(self, num, address):
        self.hubs[num] = address


    def get_star_hub(self, row, column):
        if self.ledSegmentMap:
            segment = self.ledSegmentMap[row][column]
            hub = segment["hub"]
            return self.hubs.get(hub, None)
        return ''


    def get_led_api_url(self, row, column, bright, color):
        hub = self.get_star_hub(row, column)
        if not hub:
            return None
  
        segment = self.ledSegmentMap[row][column]

        return f'http://{hub}{self.API_ADDR}{self.API_ARG_SEGMENT}{segment["segment"]}{self.API_ARG_BRIGHTNESS}{bright}{self.API_ARG_COLOR}{color}'


    def set_star_led(self, row, column, bright, color=None):
        self.stars[row][column]['bright'] = bright
        if not 'color' in self.stars[row][column]:
            self.stars[row][column]['color'] = self.STAR_COLOR
        if color:
            self.stars[row][column]['color'] = color


    def set_all_leds_off(self):
        for row, starRow in self.stars.items():
            for column, star in starRow.items():
                self.set_star_led(row, column, 0)


    def update_brightness(self, new_brightness_a, new_brightness_b, new_brightness_g):
        for row, starRow in self.stars.items():
            for column, star in starRow.items():
                if star.get('bright', 0) > 0:
                    if row > 2:
                        star['bright'] = new_brightness_b
                    else:
                        star['bright'] = new_brightness_a
        # todo: update brightness of goat


    def update_leds(self):
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
                #print(f"Adding url for star row: {row} column: {column} to request: {api_url}")
        
        rs = (grequests.get(u, timeout=5) for u in urls)

        # noinspection PyShadowingNames
        def call_map(rs, exception_handler):
            grequests.map(rs, exception_handler=exception_handler)

        if self.active == 0:
            return
        elif self.active == -1:
            self.active = 1

            # noinspection PyUnusedLocal
            def exception_handler(request, exception):
                self.active = 0            
            threading.Thread(target=call_map, args=(rs,exception_handler)).start()
        else:
            threading.Thread(target=call_map, args=(rs,None)).start()

