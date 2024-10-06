import threading
import grequests

from config.ledconfig import *
from config.gameconfig import GameConfig

class LedHandler():
    STAR_COLOR = 'FF9000'
    BRIGHTNESS_MOD = 0 # modifying 0=ALL, 1=A, 2=B, 3=G
    STAR_BRIGHTNESS_A = 255 # row 0-2
    STAR_BRIGHTNESS_B = 255 # row 3-5
    GOAT_BRIGHTNESS = 255

    # change color of segment 1 (0) to green: http://192.168.1.107/win&SM=0&SB=255&CL=H00FF00
    API_ADDR = '/win'
    API_ARG_SEGMENT = '&SM='
    API_ARG_BRIGHTNES = '&SB='
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

    def __init__(self, gameconf: GameConfig):
        self.gameconfig = gameconf
        self.active = -1 # 0: no, 1: yes, -1: active unless first request fails
        self.reset()


    def reset(self):
        self.hubs = {}
        self.stars = {}
        self.leds = {}

        if HUB_ADDR_STAR_1 != '':
            self.AddStarHub(1, HUB_ADDR_STAR_1)
        if HUB_ADDR_STAR_2 != '':
            self.AddStarHub(2, HUB_ADDR_STAR_2)
        if HUB_ADDR_STAR_3 != '':
            self.AddStarHub(3, HUB_ADDR_STAR_3)
        if HUB_ADDR_STAR_4 != '':
            self.AddStarHub(4, HUB_ADDR_STAR_4)
        if HUB_ADDR_STAR_5 != '':
            self.AddStarHub(5, HUB_ADDR_STAR_5)
        if HUB_ADDR_STAR_6 != '':
            self.AddStarHub(6, HUB_ADDR_STAR_6)

        for row in range(self.gameconfig.ROWS):
            self.stars[row] = {}
            self.leds[row] = {}
            for column in range(self.gameconfig.COLUMNS):
                self.stars[row][column] = {}
                self.leds[row][column] = {}



    def AddStarHub(self, num, address):
        self.hubs[num] = address


    def GetStarHub(self, row, column):
        if self.ledSegmentMap:
            segment = self.ledSegmentMap[row][column]
            hub = segment["hub"]
            return self.hubs.get(hub, None)
        return ''


    def GetLedApiUrl(self, row, column, bright, color):
        hub = self.GetStarHub(row, column);
        if not hub:
            return None;
  
        segment = self.ledSegmentMap[row][column];

        return f'http://{hub}{self.API_ADDR}{self.API_ARG_SEGMENT}{segment["segment"]}{self.API_ARG_BRIGHTNES}{bright}{self.API_ARG_COLOR}{color}'


    def SetStarLed(self, row, column, bright, color=None):
        self.stars[row][column]['bright'] = bright
        if not 'color' in self.stars[row][column]:
            self.stars[row][column]['color'] = self.STAR_COLOR
        if color:
            self.stars[row][column]['color'] = color


    def SetAllLedsOff(self):
        for row, starRow in self.stars.items():
            for column, star in starRow.items():
                self.SetStarLed(row, column, 0)


    def UpdateBrightness(self, newBrightnessA, newBrightnessB, newBrightnessG):
        for row, starRow in self.stars.items():
            for column, star in starRow.items():
                if star.get('bright', 0) > 0:
                    if row > 2:
                        star['bright'] = newBrightnessB
                    else:
                        star['bright'] = newBrightnessA


    def UpdateLeds(self):
        urls = []
        for row, starRow in self.stars.items():
            for column, star in starRow.items():
                led = self.leds[row][column]

                starBrigth = star.get('bright', 0)
                ledBrigth = led.get('bright', None)

                starColor = star.get('color', self.STAR_COLOR)
                ledColor = star.get('color', None)

                if (starBrigth == ledBrigth) and (starColor == ledColor):
                    continue

                self.leds[row][column]['bright'] = starBrigth
                self.leds[row][column]['color'] = starColor

                apiUrl = self.GetLedApiUrl(row, column, starBrigth, starColor)
                if not apiUrl:
                    continue

                urls += [apiUrl]
                #print(f"Adding url for star row: {row} column: {column} to request: {apiUrl}")
        
        rs = (grequests.get(u, timeout=5) for u in urls)

        def call_map(rs, exception_handler):
            grequests.map(rs, exception_handler=exception_handler)

        if self.active == 0:
            return
        elif self.active == -1:
            self.active = 1
            def exception_handler(request, exception):
                self.active = 0            
            threading.Thread(target=call_map, args=(rs,exception_handler)).start()
        else:
            threading.Thread(target=call_map, args=(rs,None)).start()

