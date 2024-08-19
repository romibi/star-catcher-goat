// difficulty settings
let STAR_BASE_LIKELYHOOD = 0.3; // at start 30% chance of 1 star. (15% for 2nd star)
let STAR_MAX_LIKELYHOOD = 0.95; // max chance of 95% for 1 star (47.5% for 2nd star)
let STAR_TIMER_LIKELYHOOD = 0.0005; // star spawn likely hood increase over time
let FORCE_STAR_SPAWN_MIN = 2; // if 2 or less stars 1 star spawns 100%
let MAX_STARS = 2; // max stars per row

// LED Stuff
// mixed content error: https://support.mozilla.org/de/kb/Wie-beeinflussen-Inhalte-die-nicht-sicher-sind-meine-Sicherheit
STAR_COLOR = 'FF9000';

HUB_ADDR_STAR_1 = '192.168.1.107';
HUB_ADDR_STAR_2 = '';
HUB_ADDR_STAR_3 = '';
HUB_ADDR_STAR_4 = '';
HUB_ADDR_STAR_5 = '';
HUB_ADDR_STAR_6 = '';

// change color of segment 1 (0) to green: http://192.168.1.107/win&SM=0&SB=255&CL=H00FF00
API_ADDR = '/win';
API_ARG_SEGMENT = '&SM=';
API_ARG_BRIGHTNES = '&SB=';
API_ARG_COLOR = '&CL=H'

// speed
let FRAME_RATE = 10; // fps
let STAR_MOVE_RATE = 10; // stars move every x frames

// game end
let STAR_STOP_SPAWN_FRAMECOUNT = 1120; // no more stars after 112 seconds
let GAME_END_FRAMECOUNT = 1200; // stop game loop after 120 seconds

// how many stars? 6x3 or 6x6
let rows = 6;
let columns = 6; // code works with 3 or 6 columns

// game status:
let rowTemplate = Array(columns).fill(false);
let stars = Array.from(Array(rows), () => [...rowTemplate]);
let goatPos = 0; // 0 = column 0&1, 1 = column 2&3, 2 = column 4&5
let goatDir = 0; // 0 = left, 1 = right;
let goatGlowHorn = 0; // glow intensity;
let goatGlowBody = 0; // glow intensity;

// points
let starsCatchedHorn = 0;
let starsCatchedButt = 0;
let starsMissed = 0;

// vizPos für 3 columns
let vizPos3 = [
  [ {x:40,y:40}                           , {x:200,y:40}, {x:300,y:40}              ],
  [              {x:70,y:60}, {x:170,y:60}                            , {x:330,y:60}],
  [ {x:40,y:80},                            {x:200,y:80}, {x:300,y:80}              ],
  
  [               {x:70,y:160},                {x:200,y:160},                {x:330,y:160}],
  [ {x:40,y:180},               {x:170,y:180},                {x:300,y:180}               ],
  [               {x:70,y:200},                {x:200,y:200},                {x:330,y:200}]
]

// vizPos für 6 columns
let vizPos6 = [
  [ {x:40,y:40}, {x:70,y:40}, {x:170,y:40}, {x:200,y:40}, {x:300,y:40}, {x:330,y:40}],
  [ {x:40,y:60}, {x:70,y:60}, {x:170,y:60}, {x:200,y:60}, {x:300,y:60}, {x:330,y:60}],
  [ {x:40,y:80}, {x:70,y:80}, {x:170,y:80}, {x:200,y:80}, {x:300,y:80}, {x:330,y:80}],
  
  [ {x:40,y:160}, {x:70,y:160}, {x:170,y:160}, {x:200,y:160}, {x:300,y:160}, {x:330,y:160}],
  [ {x:40,y:180}, {x:70,y:180}, {x:170,y:180}, {x:200,y:180}, {x:300,y:180}, {x:330,y:180}],
  [ {x:40,y:200}, {x:70,y:200}, {x:170,y:200}, {x:200,y:200}, {x:300,y:200}, {x:330,y:200}]
]

// LED info
let ledSegmentMap = [
  [ {hub: 1, segment: 2}, {hub: 1, segment: 3}, {hub: 2, segment: 2}, {hub: 2, segment: 3}, {hub: 3, segment: 2}, {hub: 3, segment: 3}],
  [ {hub: 1, segment: 1}, {hub: 1, segment: 4}, {hub: 2, segment: 1}, {hub: 2, segment: 4}, {hub: 3, segment: 1}, {hub: 3, segment: 4}],
  [ {hub: 1, segment: 0}, {hub: 1, segment: 5}, {hub: 2, segment: 0}, {hub: 2, segment: 5}, {hub: 3, segment: 0}, {hub: 3, segment: 5}],
  
  [ {hub: 4, segment: 2}, {hub: 4, segment: 3}, {hub: 5, segment: 2}, {hub: 5, segment: 3}, {hub: 6, segment: 2}, {hub: 6, segment: 3}],
  [ {hub: 4, segment: 1}, {hub: 4, segment: 4}, {hub: 5, segment: 1}, {hub: 5, segment: 4}, {hub: 6, segment: 1}, {hub: 6, segment: 4}],
  [ {hub: 4, segment: 0}, {hub: 4, segment: 5}, {hub: 5, segment: 0}, {hub: 5, segment: 5}, {hub: 6, segment: 0}, {hub: 6, segment: 5}]
]

let vizPos; // initialized in setup

// VISUALIZATION CODE
// ==================
function drawVisualization(){
  background(245);
  drawBg();
  background('rgba(0, 0, 0, 0.6)');
  drawStarSprites();
  drawGoat();
  drawCounters();
  
  // Highlight Demo Stars
  //stroke('red');
  //strokeWeight(4);
  //noFill();
  //rect(40,60,30,45);
  //strokeWeight(1)
  
}

function drawCounters() {
  noStroke();
  fill(255,255,255);
  textSize(9);
  text('Sterne fangen.', 145, 340);
  textSize(7);
  if(columns==3) {
    text('(Mit Geiss drunter sein)', 145, 350);
  } else {
    text('(Mit Hörner drunter sein)', 145, 350);
  }
  textSize(9);
  text('← → Bewegen', 145, 368);
  text('↑ Aus letzter', 145, 385);
  text('Reihe greifen.', 153, 395);
   
  textSize(12);
  fill(255,255,0);
  text('Punkte: '+max(((starsCatchedHorn*10)+starsCatchedButt-starsMissed),0), 20,375);
  textSize(9);
  if (columns==3) {
    text('Gefangen: '+starsCatchedHorn, 20,390);
  } else {
    text('Gefangen (Horn/Total): '+starsCatchedHorn+'/'+(starsCatchedHorn+starsCatchedButt), 20,390);
  }
  
  fill(150,150,150);
  text('Verpasst: '+starsMissed, 320,390);
  text('Start A: PgUp', 320,350);
  text('Start B: PgDwn',320,360);
}

function drawStarSprites() {
  let currentRow = 0;
  let currentColumn = 0;
  for (let row = 0; row < rows; row++) {
    for (let column = 0; column < columns; column++) {
      drawStar(row, column);
    }  
  }  
}

function drawStar(row, column) {
  let glowing = stars[row][column];
  let pos = vizPos[row][column];
  let x = pos.x;
  let y = pos.y;
  
  noFill();
  if(glowing) {
    stroke(255,255,0);
  } else {
    stroke(150,150,150);
  }
  
  //rect(x,y,20,20);
  
  beginShape();

  vertex(x+15, y+ 2); // top spike
  vertex(x+18, y+ 8); 
  vertex(x+25, y+ 8); // upper right spike
  vertex(x+20, y+12);
  vertex(x+23, y+18); // lower right spike
  vertex(x+15, y+13);
  vertex(x+ 7, y+18); // lower left spike
  vertex(x+10, y+12);
  vertex(x+ 5, y+ 8); // upper left spike
  vertex(x+12, y+ 8);
  
  endShape(CLOSE);
  
  
}

function drawGoatPosition(drawGoatPos, drawGoatDir, doColor) {
  let y = 310;
  let x = 0;
  
  if (drawGoatPos == 0) {
    x = 50 + drawGoatDir*10;
    y -= drawGoatDir*10;
  } else if (drawGoatPos == 1) {
    x = 160 + drawGoatDir*10;
    y -= (20 + drawGoatDir*10);
  } else if (drawGoatPos == 2) {
    x = 300 + drawGoatDir*10;
    y -= (40 + drawGoatDir*10);
  }
  
  if(doColor) {
    stroke(255, 255,255-(goatGlowBody*50));
    noFill();
  }
  
  rect(x,y,45,25); // body  
    
  if(doColor) {
    stroke(255,255,255);
  }
  
  rect(x,y+25,2,15);
  rect(x+7,y+25,2,15);
  rect(x+37,y+25,2,15);
  rect(x+43,y+25,2,15);
  
  if (drawGoatDir == 0) {
    // looking left
    rect(x,y-20,15,20); // head
    
    if(doColor) {
      stroke(255, 255,255-(goatGlowHorn*50));
    }
    
    rect(x-2,y-30,3,10); // horn
    rect(x+14,y-30,3,10); // horn
  } else {
    // looking right
    rect(x+30,y-20,15,20); // head
    
    if(doColor) {
      stroke(255, 255,255-(goatGlowHorn*50));
    }
    
    rect(x+28,y-30,3,10); // horn
    rect(x+44,y-30,3,10); // horn
  }
}

function drawGoat() {  
  stroke(120,120,120);
  noFill();
  
  drawGoatPosition(0,0,false);  
  drawGoatPosition(1,0,false);  
  drawGoatPosition(2,0,false);
  
  // if (columns==6) {
    drawGoatPosition(0,1,false);
    drawGoatPosition(1,1,false);
    drawGoatPosition(2,1,false);
  // }
    
  drawGoatPosition(goatPos,goatDir,true);
    
  if (goatGlowHorn>0) goatGlowHorn--;
  if (goatGlowBody>0) goatGlowBody--;
  
}

function drawBgWindow(x, y) {  
  fill(255,255,255);
  stroke(180,180,180);
  
  rect(x+30,y,30,20);
  rect(x+30,y+20,30,20);
  rect(x+30,y+40,30,20);
  rect(x+60,y,30,20);
  rect(x+60,y+20,30,20);
  rect(x+60,y+40,30,20);
  
  
  fill(80,140,80);
  noStroke();
  rect(x, y,30,60);
  rect(x+90, y,30,60);
}

function drawBg() {
  
  // Windows top row
  drawBgWindow(10,40);
  drawBgWindow(140,40);
  drawBgWindow(270,40);
  
  // windows middle row
  drawBgWindow(10,160);
  drawBgWindow(140,160);
  drawBgWindow(270,160);
    
  // window bottom small
  fill(255,255,255);
  stroke(180,180,180);
  rect(335,280,40,50);
    
  // window bottom big
  stroke(180,80,0);
  rect(30,280,110,70);
  
  // door
  fill(180,80,0);
  rect(225, 272, 46, 98);
}

// LED control

function GetStarHub(row, column) {
  let segment = ledSegmentMap[row][column];
  
  switch (segment.hub) {
    case 1: 
      return HUB_ADDR_STAR_1;
    case 2:
      return HUB_ADDR_STAR_2;
    case 3:
      return HUB_ADDR_STAR_3;
    case 4:
      return HUB_ADDR_STAR_4;
    case 5:
      return HUB_ADDR_STAR_5;
    case 6:
      return HUB_ADDR_STAR_6;
  }
  return '';
}

function GetLedApiUrl(row, column, starBright, starColour) {
  let hub = GetStarHub(row, column);
  if (hub == '') return '';
  
  let segment = ledSegmentMap[row][column];
  
  if(segment.bright == starBright && segment.colour == starColour) return '';
  
  segment.bright = starBright;
  segment.colour = starColour;
  
  // API_ADDR = '/win';
  // API_ARG_SEGMENT = '&SM=';
  // API_ARG_BRIGHTNES = '&SB=';
  // API_ARG_COLOR = '&CL=H' // rrggbb
  
  return 'http://'+hub+API_ADDR+API_ARG_SEGMENT+segment.segment+API_ARG_BRIGHTNES+starBright+API_ARG_COLOR+starColour;
}

function SetStarLed(row, column) {  
  let glowing = stars[row][column];
  
  starBright = 0;
  if (glowing) starBright = 255;
  
  let apiCall = GetLedApiUrl(row, column, starBright, STAR_COLOR);
  
  if (apiCall == '') return;
  
  console.log('Calling '+apiCall);
  
  var request = $.ajax({
    url: apiCall,
    method: "GET",
    timeout: 5000
  });
}

function UpdateLEDs() {
  let currentRow = 0;
  let currentColumn = 0;
  for (let row = 0; row < rows; row++) {
    for (let column = 0; column < columns; column++) {
      SetStarLed(row, column);
    }  
  } 
}

// SETUP & DRAW
// ============

function reset(){
  if(columns==3) {
    vizPos = vizPos3;
  } else {
    vizPos = vizPos6;
  }  
  
  // reset points
  starsCatchedHorn = 0;
  starsCatchedButt = 0;
  starsMissed = 0;
  
  rowTemplate = Array(columns).fill(false);
  stars = Array.from(Array(rows), () => [...rowTemplate]);
  
  frameCount=0;
  if(!isLooping())
    loop();
}

function setup() {
  createCanvas(400, 400);
  frameRate(FRAME_RATE);
  reset();
}

function draw() {
  drawVisualization();  
  UpdateLEDs();
  doGameLoop();  
}

// GAME LOGIC CODE
// ===============
function doGameLoop() {
  if (frameCount % STAR_MOVE_RATE == 0) {
    handleLastStarRow();
    moveStarsDown();
    spawnNewStarRow();
  }
  if(frameCount>GAME_END_FRAMECOUNT) {
    console.log('end');
    noLoop();
  }
}

function keyPressed() {
  let turned = false;
  //console.log(keyCode);
  if(keyCode == 37) {
    left();
  } else if (keyCode == 39) {
    right();
  } else if (keyCode == 38) {
    up();
  } else if (keyCode == 33) {
    restartA();
  } else if (keyCode == 34) {
    restartB();
  }
}

function left() {
    turned = (goatDir==1);
    goatDir=0;
    if(!turned && goatPos>0) goatPos--;
}

function right() {
    turned = (goatDir==0);
    goatDir=1;    
    let maxGoatPos = (columns/2)-1;
    if(columns==3) 
      maxGoatPos = 2;
    if(!turned && goatPos< maxGoatPos) goatPos++;
}

function up() {
    if (stars[rows-1][GetGoatHornColumn()]) {
      starsCatchedHorn++;
      stars[rows-1][GetGoatHornColumn()] = false;
    }
}

function restartA() {
    columns = 6;
    reset();
}

function restartB() {
    columns = 3;
    reset();
}

// star movement actions
function handleLastStarRow() {
  // nothing yet
  for (let column = 0; column < columns; column++) {
    let isStar = stars[rows-1][column];
    if (!isStar) continue;
    
    if(column==GetGoatHornColumn()) {
      goatGlowHorn=5;
      starsCatchedHorn++;
    } else if(column==GetGoatButtColumn()) {
      goatGlowBody=5;
      starsCatchedButt++;
    } else {
      starsMissed++;
    }
  }
  console.log('starsCatchedHorn: '+starsCatchedHorn+', starsCatchedButt: '+starsCatchedButt+', starsMissed: '+starsMissed);
}

function moveStarsDown() {
  for (let row = rows-1; row >= 1; row--) {
    for (let column = 0; column < columns; column++) {
      stars[row][column] = stars[row-1][column];
    }
  }
}

function clearNewRow() {
  for (let column = 0; column < columns; column++) {
    stars[0][column] = false;
  }
}

function spawnNewStarRow() {
  clearNewRow();
  
  if (frameCount>STAR_STOP_SPAWN_FRAMECOUNT) return;
  
  let spawnStar = false;
  let starLikelyhood = min(STAR_BASE_LIKELYHOOD + (frameCount*STAR_TIMER_LIKELYHOOD), STAR_MAX_LIKELYHOOD);
  
  let starCount = GetStarCount();
  
  for (let starNr = 1; starNr <= MAX_STARS; starNr++) {
    let randomDraw = random(1);
    spawnStar = (randomDraw < starLikelyhood);
    if(starCount<=FORCE_STAR_SPAWN_MIN) {
      console.log('force star spawn');
      spawnStar=true;
      starCount++;
    }
    console.log('likelyHood: '+starLikelyhood+', draw: '+randomDraw+', spawn: '+spawnStar);
    if (spawnStar) {
      let spawnRow = min(floor(random(rows+1)),rows)-1;
      stars[0][spawnRow] = true;
    }
    starLikelyhood = starLikelyhood/2;
  }
}

// calc stuff
function GetGoatHornColumn() {
  if (columns==3) return goatPos;
  // columns == 6:
  return goatPos*2 + goatDir;
}

function GetGoatButtColumn() {
  if (columns==3) return -1; // no butt column
  return goatPos*2 + (1-goatDir);
}

function GetStarCount() {  
  let count = 0; 
  for (let row = 0; row < rows; row++) {
    for (let column = 0; column < columns; column++) {
      if (stars[row][column]) count++;
    }
  }
  return count;
}