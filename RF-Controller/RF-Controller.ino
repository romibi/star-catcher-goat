#include <RCSwitch.h> // see https://github.com/sui77/rc-switch

// =========
// Constants
// =========
#define REPEAT_DELAY 1000
#define MIN_DELAY 10
#define SEND_REPEAT_FAST_COUNT 10

#define SEND_BTNS_OFF_TIMES 10
#define SEND_START_VALUE 604700672 // 0010 0100 0000 1011 00..

// ====
// PINS
// ====
//#define LED 13 // use LED_BUILTIN instead

// Note: although i'm using a Feather 32u4 Radio with RFM69HCW Module, the RF Module libraries (RadioHead) seem to not be compatible
// (See https://learn.adafruit.com/adafruit-feather-32u4-radio-with-rfm69hcw-module)
// with the RF Receiver I'm using on the Raspberry PI. Therefore I'm using the RF Transmitter from the same package on Pin 12
// (Same/Similar to https://www.instructables.com/RF-433-MHZ-Raspberry-Pi/ )
#define RF_DATA_TX 12
#define RF_PULSE_LENGTH 670
#define RF_PROTOCOL 2

#define BTN_R 5
#define BTN_Y 6
#define BTN_START A0
#define BTN_SELECT A1
#define BTN_UP A2
#define BTN_RIGHT A3
#define BTN_LEFT A4
#define BTN_DOWN A5

#define BUZZER 11

// ================
// Constants Melody
// ================
#define nPAUSE 0.0
#define nC1   32.703
#define nCis1 34.648
#define nD1   36.708
#define nDis1 38.891
#define nE1   41.203
#define nF1   43.203
#define nFis1 46.249
#define nG1   48.999
#define nGis1 51.913
#define nA1   55.000
#define nAs1  58.270
#define nB1   61.735

#define nC4   261.63
#define nCis4 277.18
#define nD4   293.67
#define nDis4 311.13
#define nE4   329.63
#define nF4   349.23
#define nFis4 369.99
#define nG4   392.00
#define nGis4 415.30
#define nA4   440.00
#define nAs4  466.16
#define nB4   493.88

#define nC5   523.25
#define nCis5 551.37
#define nD5   587.33
#define nDis5 622.25
#define nE5   659.26
#define nF5   698.46
#define nFis5 739.99
#define nG5   783.99
#define nGis5 830.61

#define nG5  783.99
#define nA5  880.00
#define nB5  987.77
#define nC6 1046.5
#define nD6 1174.7
#define nE6 1318.5
#define nF6 1396.9
#define nG6 1568.0
#define nA6 1760.0
#define nG7 3136.0
#define nA7 3520.0
#define nC7 2093.0

#define MELODY_TWINKLE 1
unsigned long twinkleLastNoteTime = 0;
int twinklePos = -2; // -2 stopped, -1 starting
int twinkleLength = 5;
float twinkleNotes[] = {nG5, nB5, nD6, nG6, nG7};
int twinkleTimings[] = {100, 100, 100,  25,  50};

#define MELODY_POINT 2
unsigned long pointLastNoteTime = 0;
int pointPos = -2; // -2 stopped, -1 starting
int pointLength = 2;
float pointNotes[] = {nG6, nG7};
int pointTimings[] = { 25,  50};

#define MELODY_FANFARE 3
unsigned long fanfareLastNoteTime = 0;
int fanfarePos = -2; // -2 stopped, -1 starting
int fanfareLength = 12;
float fanfareNotes[] = {nE4, nPAUSE, nE4, nPAUSE, nE4, nPAUSE, nE4, nC4, nD4, nE4, nDis4, nE4};
int fanfareTimings[] = { 60,      6,  60,      6,  60,      8, 200, 200, 200, 100,  100, 400};

#define MELODY_CHEST 4
unsigned long chestLastNoteTime = 0;
int chestPos = -2; // -2 stopped, -1 starting
int chestLength = 53;
float chestNotes[] = {nG4, nA4,   nB4,   nCis5,    nG4, nA4, nB4,   nCis5,    nGis4, nAs4,  nC5, nD5,    nGis4, nAs4, nC5,   nD5,    
                      nA4, nB4,   nCis5, nDis5,    nA4, nB4, nCis5, nDis5,    nAs4,  nC5,   nD5, nE5,    nAs4,  nC5,  nD5,   nE5,    
                      nB4, nCis5, nDis5, nF5,      nC5, nD5, nE5,   nFis5,    nCis5, nDis5, nF5, nG5,    nD5,   nE5,  nFis5, nGis5,    
                      nPAUSE,                                                 nA4,   nAs4,  nB4, nC5                                };
int chestTimings[] = {100, 100,   100,   100,      100, 100, 100,   100,      100,   100,   100, 100,    100,   100,  100,   100,
                      100, 100,   100,   100,      100, 100, 100,   100,      100,   100,   100, 100,    100,   100,  100,   100,
                      100, 100,   100,   100,      100, 100, 100,   100,      100,   100,   100, 100,    100,   100,  100,   100,
                      800,                                                    200,   200,   200, 400                                };


// ====
// Code
// ====
RCSwitch mySwitch = RCSwitch();

// code by https://stackoverflow.com/a/47990
inline int bit_set_to(int number, int n, bool x) {
    return (number & ~((int)1 << n)) | ((int)x << n);
}

void playMelodyHandler(int &melodyPos, int &melodyLength, float* melodyNotes, int* melodyTimings, unsigned long &melodyLastNoteTime) {
  if(melodyPos<-1) return;
    
  unsigned long now = millis();
  bool playNext = false;

  if (melodyPos==-1) {
    playNext = true;
  } else {
    playNext = playNext || ((now - melodyLastNoteTime) > melodyTimings[melodyPos]);
  }

  if(!playNext) return;

  melodyPos += 1;

  if(melodyPos>(melodyLength-1)) {
    melodyPos = -2;
    melodyLastNoteTime = 0;
  } else {
    if(melodyNotes[melodyPos]>0.1) // else pause
      tone(BUZZER, melodyNotes[melodyPos], melodyTimings[melodyPos]);
    melodyLastNoteTime  = millis();
  }
}

void playMelodyLoop() {
  playMelodyHandler(pointPos, pointLength, pointNotes, pointTimings, pointLastNoteTime);
  playMelodyHandler(twinklePos, twinkleLength, twinkleNotes, twinkleTimings, twinkleLastNoteTime);
  playMelodyHandler(fanfarePos, fanfareLength, fanfareNotes, fanfareTimings, fanfareLastNoteTime);
  playMelodyHandler(chestPos, chestLength, chestNotes, chestTimings, chestLastNoteTime);
}

void playMelody(int melody) {
  switch(melody) {
    case MELODY_TWINKLE:
      twinklePos = -1;
      break;
    case MELODY_POINT:
      pointPos = -1;
      break;
    case MELODY_FANFARE:
      fanfarePos = -1;
      break;
    case MELODY_CHEST:
      chestPos = -1;
      break;
  }
}

void setup() {
  Serial.begin(9600);
  
  // Transmitter is connected to Arduino Pin #10  
  mySwitch.enableTransmit(RF_DATA_TX);

  // Optional set pulse length.
  mySwitch.setPulseLength(RF_PULSE_LENGTH);
  
  // Optional set protocol (default is 1, will work for most outlets)
  mySwitch.setProtocol(RF_PROTOCOL);  

  // setup pins
  pinMode(LED_BUILTIN, OUTPUT);

  pinMode(BTN_R, INPUT_PULLUP);
  pinMode(BTN_Y, INPUT_PULLUP);
  pinMode(BTN_START, INPUT_PULLUP);
  pinMode(BTN_SELECT, INPUT_PULLUP);
  pinMode(BTN_UP, INPUT_PULLUP);
  pinMode(BTN_RIGHT, INPUT_PULLUP);
  pinMode(BTN_LEFT, INPUT_PULLUP);
  pinMode(BTN_DOWN, INPUT_PULLUP);

  pinMode(BUZZER, OUTPUT);
}

int sentDelay = REPEAT_DELAY+1;
unsigned int sentValue = 65534;
int sentCount = 0;

bool curr_R = false;
bool curr_Y = false;
bool curr_START = false;
bool curr_SELECT = false;
bool curr_UP = false;
bool curr_RIGHT = false;
bool curr_LEFT = false;
bool curr_DOWN = false;

bool last_R = false;
bool last_Y = false;
bool last_START = false;
bool last_SELECT = false;
bool last_UP = false;
bool last_RIGHT = false;
bool last_LEFT = false;
bool last_DOWN = false;

void loop() {
  unsigned int value = 0;
  unsigned int valueCorrection = 0;
  unsigned long sendValue = 0;
  int button = false;
  int aButtonPressed = false;

  playMelodyLoop();

  // Read Buttons
  curr_R = digitalRead(BTN_R)==LOW;
  curr_Y = digitalRead(BTN_Y)==LOW;
  curr_START = digitalRead(BTN_START)==LOW;
  curr_SELECT = digitalRead(BTN_SELECT)==LOW;
  curr_UP = digitalRead(BTN_UP)==LOW;
  curr_DOWN = digitalRead(BTN_DOWN)==LOW;
  curr_LEFT = digitalRead(BTN_LEFT)==LOW;
  curr_RIGHT = digitalRead(BTN_RIGHT)==LOW;
  
  value = bit_set_to(value, 0, curr_R);
  value = bit_set_to(value, 1, curr_Y);
  value = bit_set_to(value, 2, curr_START);
  value = bit_set_to(value, 3, curr_SELECT);
  value = bit_set_to(value, 4, curr_UP);
  value = bit_set_to(value, 5, curr_RIGHT);
  value = bit_set_to(value, 6, curr_LEFT);
  value = bit_set_to(value, 7, curr_DOWN);
  
  if (curr_R) {
    // do more stuff

    if(!last_R) {
      playMelody(MELODY_POINT);
      aButtonPressed = true;
    }
  }
  
  if (curr_Y) {
    // do more stuff

    if(!last_Y) {
      playMelody(MELODY_TWINKLE);
      aButtonPressed = true;
    }
  }
  
  if (curr_START) {
    // do more stuff

    if(!last_START) {
      playMelody(MELODY_FANFARE);
      aButtonPressed = true;
    }
  }
  
  if (curr_SELECT) {
    // do more stuff

    if(!last_SELECT) {
      playMelody(MELODY_CHEST);
      aButtonPressed = true;
    }
  }
  
  if (curr_UP) {
    // do more stuff

    if(!last_UP) {
      aButtonPressed = true;
    }
  }
  
  if (curr_DOWN) {
    // do more stuff

    if(!last_DOWN) {
      aButtonPressed = true;
    }
  }
  
  if (curr_RIGHT) {
    // do more stuff
    
    if(!last_RIGHT) {
      aButtonPressed = true;
    }
  }
  
  if (curr_LEFT) {
    // do more stuff

    if(!last_LEFT) {
      aButtonPressed = true;
    }
  }
  
  if (aButtonPressed)
    tone(BUZZER, 45, 50);

  // Check if we need to resend
  if(value == sentValue) {
    if(sentCount <= SEND_REPEAT_FAST_COUNT) {
      sentCount++;
    } else {
      // value is unchanged and we sent it already a few times quickly, can wait longer now
      sentDelay += MIN_DELAY;
  
      if(sentDelay < REPEAT_DELAY) {
        // sent not long ago, wait and redo loop
        
        // Todo: remove duplicate lines
        last_R = curr_R;
        last_Y = curr_Y;
        last_START = curr_START;
        last_SELECT = curr_SELECT;
        last_UP = curr_UP;
        last_DOWN = curr_DOWN;
        last_LEFT = curr_LEFT;
        last_RIGHT = curr_RIGHT;

        delay(MIN_DELAY);
        return;
      }
    }
  } else {
    sentCount = 0;
  }

  // Status LED we will send
  digitalWrite(LED_BUILTIN, HIGH);

  // reset sent status values
  sentDelay = 0;
  sentValue = value;
  
  // Calculate Number to send (Magic starting number + error detection)
  valueCorrection = ((~value)&255) << 8; // negate 8 bits and shift 8 to left
  sendValue = SEND_START_VALUE + valueCorrection + value; // add together with normal value plus start value

  // Serial debug out values
  String printVal = String(value+256, BIN); // prevent leading zeros from beeing ommitted by adding 2^8 and replacing first char with a space
  printVal[0] = ' ';
  Serial.print("Button-Values:"+printVal);
  Serial.print(" ->");
  printVal = String(valueCorrection+65536, BIN); // prevent leading zeros from beeing ommitted by adding 2^16 and replacing first char with a space
  printVal[0] = ' ';
  Serial.print(printVal);
  Serial.print(" -> ");
  Serial.print(sendValue, BIN);
  Serial.print(" -> ");
  Serial.print(sendValue, DEC);
  Serial.println("");

  // Send IT
  mySwitch.send(sendValue, 32);

  last_R = curr_R;
  last_Y = curr_Y;
  last_START = curr_START;
  last_SELECT = curr_SELECT;
  last_UP = curr_UP;
  last_DOWN = curr_DOWN;
  last_LEFT = curr_LEFT;
  last_RIGHT = curr_RIGHT;

  delay(MIN_DELAY);  
  digitalWrite(LED_BUILTIN, LOW);
}