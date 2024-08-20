#!/usr/bin/env python

import os
import random
from typing import List
import pygame as pg
from pygame import Rect

# see if we can load more than standard BMP
if not pg.image.get_extended():
    raise SystemExit("Sorry, extended image module required")

# difficulty settings
STAR_BASE_LIKELYHOOD = 0.3; # at start 30% chance of 1 star. (15% for 2nd star)
STAR_MAX_LIKELYHOOD = 0.95; # max chance of 95% for 1 star (47.5% for 2nd star)
STAR_TIMER_LIKELYHOOD = 0.0005; # star spawn likely hood increase over time
FORCE_STAR_SPAWN_MIN = 2; # if 2 or less stars 1 star spawns 100%
MAX_STARS = 2; # max stars per row

# LED Stuff
STAR_COLOR = 'FF9000';

HUB_ADDR_STAR_1 = '192.168.1.107';
HUB_ADDR_STAR_2 = '';
HUB_ADDR_STAR_3 = '';
HUB_ADDR_STAR_4 = '';
HUB_ADDR_STAR_5 = '';
HUB_ADDR_STAR_6 = '';

# change color of segment 1 (0) to green: http://192.168.1.107/win&SM=0&SB=255&CL=H00FF00
API_ADDR = '/win';
API_ARG_SEGMENT = '&SM=';
API_ARG_BRIGHTNES = '&SB=';
API_ARG_COLOR = '&CL=H'

# speed
FRAME_COUNT = 0
FRAME_RATE = 10; # fps
STAR_MOVE_RATE = 10; # stars move every x frames

# game end
STAR_STOP_SPAWN_FRAMECOUNT = 1120; # no more stars after 112 seconds
GAME_END_FRAMECOUNT = 1200; # stop game loop after 120 seconds

# how many stars? 6x3 or 6x6
rows = 6;
columns = 6; # code works with 3 or 6 columns

SCREENRECT = pg.Rect(0, 0, 640, 480)

main_dir = os.path.split(os.path.abspath(__file__))[0]


# helper functions
def load_image(file):
    """loads an image, prepares it for play"""
    file = os.path.join(main_dir, "data", file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit(f'Could not load image "{file}" {pg.get_error()}')
    return surface.convert()


def load_sound(file):
    """because pygame can be compiled without mixer."""
    if not pg.mixer:
        return None
    file = os.path.join(main_dir, "data", file)
    try:
        sound = pg.mixer.Sound(file)
        return sound
    except pg.error:
        print(f"Warning, unable to load, {file}")
    return None


# game status:
# let rowTemplate = Array(columns).fill(false);
# let stars = Array.from(Array(rows), () => [...rowTemplate]);
# goatPos = 0; # 0 = column 0&1, 1 = column 2&3, 2 = column 4&5
# goatDir = 0; # 0 = left, 1 = right;
# let goatGlowHorn = 0; // glow intensity;
# let goatGlowBody = 0; // glow intensity;

# // points
# let starsCatchedHorn = 0;
# let starsCatchedButt = 0;
# let starsMissed = 0;

# // vizPos für 3 columns
# let vizPos3 = [
#   [ {x:40,y:40}                           , {x:200,y:40}, {x:300,y:40}              ],
#   [              {x:70,y:60}, {x:170,y:60}                            , {x:330,y:60}],
#   [ {x:40,y:80},                            {x:200,y:80}, {x:300,y:80}              ],
  
#   [               {x:70,y:160},                {x:200,y:160},                {x:330,y:160}],
#   [ {x:40,y:180},               {x:170,y:180},                {x:300,y:180}               ],
#   [               {x:70,y:200},                {x:200,y:200},                {x:330,y:200}]
# ]

# // vizPos für 6 columns
vizRects6 = [
   [ Rect(40, 40, 16, 16), Rect(70, 40, 16, 16), Rect(170, 40, 16, 16), Rect(200, 40, 16, 16), Rect(300, 40, 16, 16), Rect(330, 40, 16, 16)],
   [ Rect(40, 60, 16, 16), Rect(70, 60, 16, 16), Rect(170, 60, 16, 16), Rect(200, 60, 16, 16), Rect(300, 60, 16, 16), Rect(330, 60, 16, 16)],
   [ Rect(40, 80, 16, 16), Rect(70, 80, 16, 16), Rect(170, 80, 16, 16), Rect(200, 80, 16, 16), Rect(300, 80, 16, 16), Rect(330, 80, 16, 16)],

   [ Rect(40, 160, 16, 16), Rect(70, 160, 16, 16), Rect(170, 160, 16, 16), Rect(200, 160, 16, 16), Rect(300, 160, 16, 16), Rect(330, 160, 16, 16)],
   [ Rect(40, 180, 16, 16), Rect(70, 180, 16, 16), Rect(170, 180, 16, 16), Rect(200, 180, 16, 16), Rect(300, 180, 16, 16), Rect(330, 180, 16, 16)],
   [ Rect(40, 200, 16, 16), Rect(70, 200, 16, 16), Rect(170, 200, 16, 16), Rect(200, 200, 16, 16), Rect(300, 200, 16, 16), Rect(330, 200, 16, 16)]
]
vizRects = vizRects6

vizGoatRects = [ Rect(40, 300, 32, 32), Rect(54, 300, 32, 32), Rect(170, 300, 32, 32), Rect(184, 300, 32, 32), Rect(300, 300, 32, 32), Rect(314, 300, 32, 32)]

# // LED info
# let ledSegmentMap = [
#   [ {hub: 1, segment: 2}, {hub: 1, segment: 3}, {hub: 2, segment: 2}, {hub: 2, segment: 3}, {hub: 3, segment: 2}, {hub: 3, segment: 3}],
#   [ {hub: 1, segment: 1}, {hub: 1, segment: 4}, {hub: 2, segment: 1}, {hub: 2, segment: 4}, {hub: 3, segment: 1}, {hub: 3, segment: 4}],
#   [ {hub: 1, segment: 0}, {hub: 1, segment: 5}, {hub: 2, segment: 0}, {hub: 2, segment: 5}, {hub: 3, segment: 0}, {hub: 3, segment: 5}],
  
#   [ {hub: 4, segment: 2}, {hub: 4, segment: 3}, {hub: 5, segment: 2}, {hub: 5, segment: 3}, {hub: 6, segment: 2}, {hub: 6, segment: 3}],
#   [ {hub: 4, segment: 1}, {hub: 4, segment: 4}, {hub: 5, segment: 1}, {hub: 5, segment: 4}, {hub: 6, segment: 1}, {hub: 6, segment: 4}],
#   [ {hub: 4, segment: 0}, {hub: 4, segment: 5}, {hub: 5, segment: 0}, {hub: 5, segment: 5}, {hub: 6, segment: 0}, {hub: 6, segment: 5}]
# ]

# let vizPos; // initialized in setup

# // VISUALIZATION CODE
# // ==================
# function drawVisualization(){
#   background(245);
#   drawBg();
#   background('rgba(0, 0, 0, 0.6)');
#   drawStarSprites();
#   drawGoat();
#   drawCounters();
  
#   // Highlight Demo Stars
#   //stroke('red');
#   //strokeWeight(4);
#   //noFill();
#   //rect(40,60,30,45);
#   //strokeWeight(1)
  
# }

# function drawCounters() {
#   noStroke();
#   fill(255,255,255);
#   textSize(9);
#   text('Sterne fangen.', 145, 340);
#   textSize(7);
#   if(columns==3) {
#     text('(Mit Geiss drunter sein)', 145, 350);
#   } else {
#     text('(Mit Hörner drunter sein)', 145, 350);
#   }
#   textSize(9);
#   text('← → Bewegen', 145, 368);
#   text('↑ Aus letzter', 145, 385);
#   text('Reihe greifen.', 153, 395);
   
#   textSize(12);
#   fill(255,255,0);
#   text('Punkte: '+max(((starsCatchedHorn*10)+starsCatchedButt-starsMissed),0), 20,375);
#   textSize(9);
#   if (columns==3) {
#     text('Gefangen: '+starsCatchedHorn, 20,390);
#   } else {
#     text('Gefangen (Horn/Total): '+starsCatchedHorn+'/'+(starsCatchedHorn+starsCatchedButt), 20,390);
#   }
  
#   fill(150,150,150);
#   text('Verpasst: '+starsMissed, 320,390);
#   text('Start A: PgUp', 320,350);
#   text('Start B: PgDwn',320,360);
# }

# function drawStarSprites() {
#   let currentRow = 0;
#   let currentColumn = 0;
#   for (let row = 0; row < rows; row++) {
#     for (let column = 0; column < columns; column++) {
#       drawStar(row, column);
#     }  
#   }  
# }

# function drawStar(row, column) {
#   let glowing = stars[row][column];
#   let pos = vizPos[row][column];
#   let x = pos.x;
#   let y = pos.y;
  
#   noFill();
#   if(glowing) {
#     stroke(255,255,0);
#   } else {
#     stroke(150,150,150);
#   }
  
#   //rect(x,y,20,20);
  
#   beginShape();

#   vertex(x+15, y+ 2); // top spike
#   vertex(x+18, y+ 8); 
#   vertex(x+25, y+ 8); // upper right spike
#   vertex(x+20, y+12);
#   vertex(x+23, y+18); // lower right spike
#   vertex(x+15, y+13);
#   vertex(x+ 7, y+18); // lower left spike
#   vertex(x+10, y+12);
#   vertex(x+ 5, y+ 8); // upper left spike
#   vertex(x+12, y+ 8);
  
#   endShape(CLOSE);
  
  
# }

# function drawGoatPosition(drawGoatPos, drawGoatDir, doColor) {
#   let y = 310;
#   let x = 0;
  
#   if (drawGoatPos == 0) {
#     x = 50 + drawGoatDir*10;
#     y -= drawGoatDir*10;
#   } else if (drawGoatPos == 1) {
#     x = 160 + drawGoatDir*10;
#     y -= (20 + drawGoatDir*10);
#   } else if (drawGoatPos == 2) {
#     x = 300 + drawGoatDir*10;
#     y -= (40 + drawGoatDir*10);
#   }
  
#   if(doColor) {
#     stroke(255, 255,255-(goatGlowBody*50));
#     noFill();
#   }
  
#   rect(x,y,45,25); // body  
    
#   if(doColor) {
#     stroke(255,255,255);
#   }
  
#   rect(x,y+25,2,15);
#   rect(x+7,y+25,2,15);
#   rect(x+37,y+25,2,15);
#   rect(x+43,y+25,2,15);
  
#   if (drawGoatDir == 0) {
#     // looking left
#     rect(x,y-20,15,20); // head
    
#     if(doColor) {
#       stroke(255, 255,255-(goatGlowHorn*50));
#     }
    
#     rect(x-2,y-30,3,10); // horn
#     rect(x+14,y-30,3,10); // horn
#   } else {
#     // looking right
#     rect(x+30,y-20,15,20); // head
    
#     if(doColor) {
#       stroke(255, 255,255-(goatGlowHorn*50));
#     }
    
#     rect(x+28,y-30,3,10); // horn
#     rect(x+44,y-30,3,10); // horn
#   }
# }

# function drawGoat() {  
#   stroke(120,120,120);
#   noFill();
  
#   drawGoatPosition(0,0,false);  
#   drawGoatPosition(1,0,false);  
#   drawGoatPosition(2,0,false);
  
#   // if (columns==6) {
#     drawGoatPosition(0,1,false);
#     drawGoatPosition(1,1,false);
#     drawGoatPosition(2,1,false);
#   // }
    
#   drawGoatPosition(goatPos,goatDir,true);
    
#   if (goatGlowHorn>0) goatGlowHorn--;
#   if (goatGlowBody>0) goatGlowBody--;
  
# }

# function drawBgWindow(x, y) {  
#   fill(255,255,255);
#   stroke(180,180,180);
  
#   rect(x+30,y,30,20);
#   rect(x+30,y+20,30,20);
#   rect(x+30,y+40,30,20);
#   rect(x+60,y,30,20);
#   rect(x+60,y+20,30,20);
#   rect(x+60,y+40,30,20);
  
  
#   fill(80,140,80);
#   noStroke();
#   rect(x, y,30,60);
#   rect(x+90, y,30,60);
# }

# function drawBg() {
  
#   // Windows top row
#   drawBgWindow(10,40);
#   drawBgWindow(140,40);
#   drawBgWindow(270,40);
  
#   // windows middle row
#   drawBgWindow(10,160);
#   drawBgWindow(140,160);
#   drawBgWindow(270,160);
    
#   // window bottom small
#   fill(255,255,255);
#   stroke(180,180,180);
#   rect(335,280,40,50);
    
#   // window bottom big
#   stroke(180,80,0);
#   rect(30,280,110,70);
  
#   // door
#   fill(180,80,0);
#   rect(225, 272, 46, 98);
# }

# // LED control

# function GetStarHub(row, column) {
#   let segment = ledSegmentMap[row][column];
  
#   switch (segment.hub) {
#     case 1: 
#       return HUB_ADDR_STAR_1;
#     case 2:
#       return HUB_ADDR_STAR_2;
#     case 3:
#       return HUB_ADDR_STAR_3;
#     case 4:
#       return HUB_ADDR_STAR_4;
#     case 5:
#       return HUB_ADDR_STAR_5;
#     case 6:
#       return HUB_ADDR_STAR_6;
#   }
#   return '';
# }

# function GetLedApiUrl(row, column, starBright, starColour) {
#   let hub = GetStarHub(row, column);
#   if (hub == '') return '';
  
#   let segment = ledSegmentMap[row][column];
  
#   if(segment.bright == starBright && segment.colour == starColour) return '';
  
#   segment.bright = starBright;
#   segment.colour = starColour;
  
#   // API_ADDR = '/win';
#   // API_ARG_SEGMENT = '&SM=';
#   // API_ARG_BRIGHTNES = '&SB=';
#   // API_ARG_COLOR = '&CL=H' // rrggbb
  
#   return 'http://'+hub+API_ADDR+API_ARG_SEGMENT+segment.segment+API_ARG_BRIGHTNES+starBright+API_ARG_COLOR+starColour;
# }

# function SetStarLed(row, column) {  
#   let glowing = stars[row][column];
  
#   starBright = 0;
#   if (glowing) starBright = 255;
  
#   let apiCall = GetLedApiUrl(row, column, starBright, STAR_COLOR);
  
#   if (apiCall == '') return;
  
#   console.log('Calling '+apiCall);
  
#   var request = $.ajax({
#     url: apiCall,
#     method: "GET",
#     timeout: 5000
#   });
# }

# function UpdateLEDs() {
#   let currentRow = 0;
#   let currentColumn = 0;
#   for (let row = 0; row < rows; row++) {
#     for (let column = 0; column < columns; column++) {
#       SetStarLed(row, column);
#     }  
#   } 
# }

# // SETUP & DRAW
# // ============

# function reset(){
#   if(columns==3) {
#     vizPos = vizPos3;
#   } else {
#     vizPos = vizPos6;
#   }  
  
#   // reset points
#   starsCatchedHorn = 0;
#   starsCatchedButt = 0;
#   starsMissed = 0;
  
#   rowTemplate = Array(columns).fill(false);
#   stars = Array.from(Array(rows), () => [...rowTemplate]);
  
#   frameCount=0;
#   if(!isLooping())
#     loop();
# }

# function setup() {
#   createCanvas(400, 400);
#   frameRate(FRAME_RATE);
#   reset();
# }

# function draw() {
#   drawVisualization();  
#   UpdateLEDs();
#   doGameLoop();  
# }

# // GAME LOGIC CODE
# // ===============
# function doGameLoop() {
#   if (frameCount % STAR_MOVE_RATE == 0) {
#     handleLastStarRow();
#     moveStarsDown();
#     spawnNewStarRow();
#   }
#   if(frameCount>GAME_END_FRAMECOUNT) {
#     console.log('end');
#     noLoop();
#   }
# }

# function keyPressed() {
#   let turned = false;
#   //console.log(keyCode);
#   if(keyCode == 37) {
#     left();
#   } else if (keyCode == 39) {
#     right();
#   } else if (keyCode == 38) {
#     up();
#   } else if (keyCode == 33) {
#     restartA();
#   } else if (keyCode == 34) {
#     restartB();
#   }
# }

# function up() {
#     if (stars[rows-1][GetGoatHornColumn()]) {
#       starsCatchedHorn++;
#       stars[rows-1][GetGoatHornColumn()] = false;
#     }
# }

# function restartA() {
#     columns = 6;
#     reset();
# }

# function restartB() {
#     columns = 3;
#     reset();
# }

# // star movement actions
# function handleLastStarRow() {
#   // nothing yet
#   for (let column = 0; column < columns; column++) {
#     let isStar = stars[rows-1][column];
#     if (!isStar) continue;
    
#     if(column==GetGoatHornColumn()) {
#       goatGlowHorn=5;
#       starsCatchedHorn++;
#     } else if(column==GetGoatButtColumn()) {
#       goatGlowBody=5;
#       starsCatchedButt++;
#     } else {
#       starsMissed++;
#     }
#   }
#   console.log('starsCatchedHorn: '+starsCatchedHorn+', starsCatchedButt: '+starsCatchedButt+', starsMissed: '+starsMissed);
# }

def spawnNewStarRow(stars, stargroups):
    if(FRAME_COUNT>STAR_STOP_SPAWN_FRAMECOUNT):
        return

    if FRAME_COUNT % STAR_MOVE_RATE != 0:
        return


    spawnStar = False
    starLikelyhood = min(STAR_BASE_LIKELYHOOD + (FRAME_COUNT*STAR_TIMER_LIKELYHOOD), STAR_MAX_LIKELYHOOD);
    starCount = len(stars.sprites())

    for starNr in range(MAX_STARS):
        randomDraw = random.random()
        spawnStar = randomDraw < starLikelyhood

        if starCount <= FORCE_STAR_SPAWN_MIN:
            #print("Force star spawn")
            spawnStar=True
            starCount += 1

        #print(f"likelyHood: {starLikelyhood}, draw: {randomDraw}, spawn: {spawnStar}")

        if spawnStar:
            spawnColumn = random.randint(0, columns-1);
            #print(f"Spawning at {spawnColumn}")
            Star(spawnColumn, stargroups)

# // calc stuff
# function GetGoatHornColumn() {
#   if (columns==3) return goatPos;
#   // columns == 6:
#   return goatPos*2 + goatDir;
# }

# function GetGoatButtColumn() {
#   if (columns==3) return -1; // no butt column
#   return goatPos*2 + (1-goatDir);
# }

class Star(pg.sprite.Sprite):

    gridPosX = 0
    gridPosY = 0
    images: List[pg.Surface] = []


    def __init__(self, column, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.image = self.images[0]
        self.gridPosX = column
        self.gridPosY = -1
        self.rect = vizRects[self.gridPosY+1][self.gridPosX]
        self.facing = 0
        self.frame = 0

    def fall(self):
        self.gridPosY += 1
        if self.gridPosY < 6:
            self.rect = vizRects[self.gridPosY][self.gridPosX]
        else:
            self.land()

    def land(self):
        # TODO: check goat position and calculate points
        self.kill()


    def update(self, *args, **kwargs):
        #self.rect.move_ip(self.facing, 1)
        if self.frame % STAR_MOVE_RATE == 0:
            self.fall()

        if not SCREENRECT.contains(self.rect):
            self.facing = -self.facing
            self.rect.top = self.rect.bottom + 1
            self.rect = self.rect.clamp(SCREENRECT)
        self.frame = self.frame + 1


class Player(pg.sprite.Sprite):

    images: List[pg.Surface] = []
    gridPos = 0
    hornGlowing = False
    bodyGlowing = False

    def __init__(self, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.image = self.images[0]
        self.gridPos = 1
        self.facing = -1
        self.rect = Rect(0,0,0,0)
        self.reloading = 0
        self.origtop = self.rect.top
        self.updateImage()
        self.updateRect()

    def updateImage(self):
        if self.facing < 0:
            if self.hornGlowing:
                self.image = self.images[2]
            elif self.bodyGlowing:
                self.image = self.images[4]
            else:
                self.image = self.images[0]
        elif self.facing > 0:
            if self.hornGlowing:
                self.image = self.images[3]
            elif self.bodyGlowing:
                self.image = self.images[5]
            else:
                self.image = self.images[1]

    def updateRect(self):
        self.rect = vizGoatRects[int(self.gridPos*2)+max(self.facing,0)]

    def moveInGrid(self):        
        maxGoatPos = round(columns/2)-1
        if columns == 3:
            maxGoatPos = 2

        if self.facing < 0:
            self.gridPos = max(self.gridPos-1,0)
        elif self.facing > 0:
            self.gridPos = min(self.gridPos+1,maxGoatPos)


    def move(self, direction):
        if direction == 0:
            return

        turned = (self.facing != direction)
        self.facing = direction

        if not turned:
            self.moveInGrid()        

        #print(f"gridPos: {self.gridPos}, facing: {self.facing}")

        self.updateImage()
        self.updateRect()

    def jump(self):
        # todo
        return


def main(winstyle=0):
    # Initialize pygame
    if pg.get_sdl_version()[0] == 2:
        pg.mixer.pre_init(44100, 32, 2, 1024)
    pg.init()
    if pg.mixer and not pg.mixer.get_init():
        print("Warning, no sound")
        pg.mixer = None

    fullscreen = False
    # Set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    # Load images, assign to sprite classes
    # (do this before the classes are used, after screen setup)
    
    Player.images = [load_image(im) for im in ("goatL.png", "goatR.png", "goatLHorn.png", "goatRHorn.png", "goatLBody.png", "goatRBody.png")]
    img = load_image("star.png")
    Star.images = [img]

    ## decorate the game window
    # icon = pg.transform.scale(Alien.images[0], (32, 32))
    #pg.display.set_icon(icon)
    pg.display.set_caption("Pygame Star Catcher Goat")
    pg.mouse.set_visible(0)

    # create the background, tile the bgd image
    #bgdtile = load_image("background.gif")
    background = pg.Surface(SCREENRECT.size)
    #for x in range(0, SCREENRECT.width, bgdtile.get_width()):
    #    background.blit(bgdtile, (x, 0))
    #screen.blit(background, (0, 0))
    #pg.display.flip()


    # Create Some Starting Values
    clock = pg.time.Clock()

    # Initialize Game Groups
    stars = pg.sprite.Group()
    all = pg.sprite.RenderUpdates()

    # initialize our starting sprites
    global SCORE, FRAME_COUNT
    player = Player(all)
    #Star( 0,
    #    stars, all
    #)  # note, this 'lives' because it goes into a sprite group
    #if pg.font:
    #    all.add(Score(all))

    # Run our main loop whilst the player is alive.
    while player.alive():
        FRAME_COUNT += 1
        # get input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_RIGHT:
                player.move(1)
            if event.type == pg.KEYDOWN and event.key == pg.K_LEFT:
                player.move(-1)
            if event.type == pg.KEYDOWN and event.key == pg.K_UP:
                player.jump()

        keystate = pg.key.get_pressed()

        # clear/erase the last drawn sprites
        #all.clear(screen, background)
        all.clear(screen, background)

        # update all the sprites
        all.update()

        # handle player input
        #direction = keystate[pg.K_RIGHT] - keystate[pg.K_LEFT]
        #player.move(direction)
        #jumping = keystate[pg.K_UP]
        #player.jumping = jumping

        # Create new star
        # todo
        
        # draw the scene
        dirty = all.draw(screen)
        pg.display.update(dirty)

        # cap the framerate at 40fps. Also called 40HZ or 40 times per second.

        spawnNewStarRow(stars, (stars, all))

        clock.tick(FRAME_RATE)

    if pg.mixer:
        pg.mixer.music.fadeout(1000)
    pg.time.wait(1000)



# call the "main" function if running this script
if __name__ == "__main__":
    main()
    pg.quit()