#include <SPI.h>
#include <RH_RF69.h>
#include <RHReliableDatagram.h>

String CONTROLLER_COLOR = "g";
// String CONTROLLER_COLOR = "b";

// ====
// PINS
// ====
#define RFM69_CS    8
#define RFM69_INT   7
#define RFM69_RST   4
//#define LED        13 // use LED_BUILTIN instead

#define BTN_R 9
#define BTN_Y 10
#define BTN_START 11
#define BTN_SELECT 12
#define BTN_UP A4
#define BTN_RIGHT A3
#define BTN_LEFT A2
#define BTN_DOWN A1

#define BUZZER A0

// ============
// Constants RF
// ============
#define RF69_FREQ 433.0

// Who am i?
#define MY_ADDRESS   2

// Where to send packets to!
#define DEST_ADDRESS 1

// ===============
// Constants Logic
// ===============
#define MIN_DELAY 10 // delay end of loop (normal mode)
// todo implement deep sleep with interrupt
#define SHALLOW_SLEEP_TIME 10000 //300000 // 5 min until loop slows down
#define SHALLOW_SLEEP_DELAY 1000 // delay end of loop (shallow sleep mode)
// -> in this state you need to press a button up to 1s to back to normal speed

#define SEND_REPEAT_FAST_COUNT 4 // after a change of pressed buttons: how many times to send state
#define SEND_REPEAT_SLOW_DELAY 100 // after fast re-sends, how often to re-send same state
#define SEND_REPEAT_SLOW_EMPTY_DELAY 1000 // after fast re-sends, if no buttons are pressed, how often to re-sed same state

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
// Singleton instance of the radio driver
RH_RF69 rf69(RFM69_CS, RFM69_INT);

// Class to manage message delivery and receipt, using the driver declared above
RHReliableDatagram rf69_manager(rf69, MY_ADDRESS);

int16_t packetnum = 0;  // packet counter, we increment per xmission

bool playMelodyHandler(int &melodyPos, int &melodyLength, float* melodyNotes, int* melodyTimings, unsigned long &melodyLastNoteTime) {
  if(melodyPos<-1) return false;
    
  unsigned long now = millis();
  bool playNext = false;

  if (melodyPos==-1) {
    playNext = true;
  } else {
    playNext = playNext || ((now - melodyLastNoteTime) > melodyTimings[melodyPos]);
  }

  if(!playNext) return true;

  melodyPos += 1;

  if(melodyPos>(melodyLength-1)) {
    melodyPos = -2;
    melodyLastNoteTime = 0;
  } else {
    if(melodyNotes[melodyPos]>0.1) // else pause
      tone(BUZZER, melodyNotes[melodyPos], melodyTimings[melodyPos]);
    melodyLastNoteTime  = millis();
  }

  return true;
}

bool playMelodyLoop() {
  boolean result = false;
  result = result || playMelodyHandler(pointPos, pointLength, pointNotes, pointTimings, pointLastNoteTime);
  result = result || playMelodyHandler(twinklePos, twinkleLength, twinkleNotes, twinkleTimings, twinkleLastNoteTime);
  result = result || playMelodyHandler(fanfarePos, fanfareLength, fanfareNotes, fanfareTimings, fanfareLastNoteTime);
  result = result || playMelodyHandler(chestPos, chestLength, chestNotes, chestTimings, chestLastNoteTime);
  return result;
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

void handleCommand(String command) {
  if (command.equals("play chest") || command.equals("p:c")) {
    playMelody(MELODY_CHEST);
  }
  
  if (command.equals("play point") || command.equals("p:p")) {
    playMelody(MELODY_POINT);
  }
  
  if (command.equals("play twinkle") || command.equals("p:t")) {
    playMelody(MELODY_TWINKLE);
  }
  
  if (command.equals("play fanfare") || command.equals("p:f")) {
    playMelody(MELODY_FANFARE);
  }
}

void setup() {
  Serial.begin(9600);

  // setup pins
  pinMode(RFM69_RST, OUTPUT);
  digitalWrite(RFM69_RST, LOW);

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

  // rf init
  // manual reset
  digitalWrite(RFM69_RST, HIGH);
  delay(10);
  digitalWrite(RFM69_RST, LOW);
  delay(10);

  if (!rf69_manager.init()) {
    Serial.println("RFM69 radio init failed");
    while (1);
  }
  Serial.println("RFM69 radio init OK!");
  // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM (for low power module)
  // No encryption
  if (!rf69.setFrequency(RF69_FREQ)) {
    Serial.println("setFrequency failed");
  }

  // If you are using a high power RF69 eg RFM69HW, you *must* set a Tx power with the
  // ishighpowermodule flag set like this:
  rf69.setTxPower(20, true);  // range from 14-20 for power, 2nd arg must be true for 69HCW

  // The encryption key has to be the same as the one in the client
  uint8_t key[] = { 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
                    0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08 };
  rf69.setEncryptionKey(key);

  Serial.print("RFM69 radio @");  Serial.print((int)RF69_FREQ);  Serial.println(" MHz");
  
  String color_command = "C:"+CONTROLLER_COLOR;
  char radiopacket[20];
  color_command.toCharArray(radiopacket, 20);
  Serial.print("Sending "); Serial.println(radiopacket);
  // Send a message to the DESTINATION!
  if (!rf69_manager.sendtoWait((uint8_t *)radiopacket, strlen(radiopacket), DEST_ADDRESS)) {
    Serial.println("Sending failed (no ack)");
  }

}

// Dont put this on the stack:
uint8_t buf[RH_RF69_MAX_MESSAGE_LEN];
uint8_t data[] = "  OK";

bool last_R = false;
bool last_Y = false;
bool last_START = false;
bool last_SELECT = false;
bool last_UP = false;
bool last_RIGHT = false;
bool last_LEFT = false;
bool last_DOWN = false;

bool curr_R = false;
bool curr_Y = false;
bool curr_START = false;
bool curr_SELECT = false;
bool curr_UP = false;
bool curr_RIGHT = false;
bool curr_LEFT = false;
bool curr_DOWN = false;

bool trigger_R = false;
bool trigger_Y = false;
bool trigger_START = false;
bool trigger_SELECT = false;
bool trigger_UP = false;
bool trigger_RIGHT = false;
bool trigger_LEFT = false;
bool trigger_DOWN = false;

bool released_R = false;
bool released_Y = false;
bool released_START = false;
bool released_SELECT = false;
bool released_UP = false;
bool released_RIGHT = false;
bool released_LEFT = false;
bool released_DOWN = false;

bool lastAnyButtonDown = false;
bool anyButtonDown = false;
bool anyTrigger = false;
bool lastButtonReleased = false;

char last_sent_state[20] = "";
int last_sent_count = 0;
unsigned long last_sent_count_reset_time = 0;
unsigned long last_sent_time = 0;

void loop() {
  if (rf69_manager.available()) {
    // Wait for a message addressed to us from the client
    uint8_t len = sizeof(buf);
    uint8_t from;
    // or use no ack?: if (rf69_manager.recvfrom(buf, &len, &from)) {
    if (rf69_manager.recvfromAck(buf, &len, &from)) {
    //if (rf69_manager.recvfrom(buf, &len, &from)) {
      buf[len] = 0; // zero out remaining string

      Serial.print("Got packet from #"); Serial.print(from);
      Serial.print(" [RSSI :");
      Serial.print(rf69.lastRssi());
      Serial.print("] : ");
      Serial.println((char*)buf);

      String command = buf;

      char *token = strtok(buf, ";");
      while (token != NULL) {
        String command = token;
        command.trim();
        handleCommand(command);
        token = strtok(NULL, ";");
      }
    }
  }

  int radiopacketPointer = 0;
  char radiopacket[20] = "";

  bool playing_melody;
  playing_melody = playMelodyLoop();

  // Read Buttons
  curr_R = digitalRead(BTN_R)==LOW;
  curr_Y = digitalRead(BTN_Y)==LOW;
  curr_START = digitalRead(BTN_START)==LOW;
  curr_SELECT = digitalRead(BTN_SELECT)==LOW;
  curr_UP = digitalRead(BTN_UP)==LOW;
  curr_DOWN = digitalRead(BTN_DOWN)==LOW;
  curr_LEFT = digitalRead(BTN_LEFT)==LOW;
  curr_RIGHT = digitalRead(BTN_RIGHT)==LOW;

  trigger_R = (!last_R) && curr_R;
  trigger_Y = (!last_Y) && curr_Y;
  trigger_START = (!last_START) && curr_START;
  trigger_SELECT = (!last_SELECT) && curr_SELECT;
  trigger_UP = (!last_UP) && curr_UP;
  trigger_RIGHT = (!last_RIGHT) && curr_RIGHT;
  trigger_LEFT = (!last_LEFT) && curr_LEFT;
  trigger_DOWN = (!last_DOWN) && curr_DOWN;

  released_R = last_R && (!curr_R);
  released_Y = last_Y && (!curr_Y);
  released_START = last_START && (!curr_START);
  released_SELECT = last_SELECT && (!curr_SELECT);
  released_UP = last_UP && (!curr_UP);
  released_RIGHT = last_RIGHT && (!curr_RIGHT);
  released_LEFT = last_LEFT && (!curr_LEFT);
  released_DOWN = last_DOWN && (!curr_DOWN);

  bool lastAnyButtonDown = last_R || last_Y || last_START || last_SELECT || last_UP || last_DOWN || last_LEFT || last_RIGHT;
  bool anyButtonDown = curr_R || curr_Y || curr_START || curr_SELECT || curr_UP || curr_DOWN || curr_LEFT || curr_RIGHT;
  bool anyTrigger = trigger_R || trigger_Y || trigger_START || trigger_SELECT || trigger_UP || trigger_DOWN || trigger_LEFT || trigger_RIGHT;
  bool lastButtonReleased = lastAnyButtonDown && (!anyButtonDown);

  if (curr_R) radiopacket[radiopacketPointer++] = 'R';
  if (curr_Y) radiopacket[radiopacketPointer++] = 'Y';
  if (curr_START) radiopacket[radiopacketPointer++] = 'S';
  if (curr_SELECT) radiopacket[radiopacketPointer++] = 's';
  if (curr_UP) radiopacket[radiopacketPointer++] = 'u';
  if (curr_DOWN) radiopacket[radiopacketPointer++] = 'd';
  if (curr_LEFT) radiopacket[radiopacketPointer++] = 'l';
  if (curr_RIGHT) radiopacket[radiopacketPointer++] = 'r';

  //if(trigger_R) playMelody(MELODY_POINT);
  //if(trigger_Y) playMelody(MELODY_TWINKLE);
  //if(trigger_START) playMelody(MELODY_FANFARE);
  //if(trigger_SELECT) playMelody(MELODY_CHEST);
  
  if (anyTrigger)
    tone(BUZZER, 45, 50);

  if(strcmp(last_sent_state, radiopacket)!=0) {
    last_sent_count = 0;
    last_sent_count_reset_time = millis();
  }

  bool doSend = false;
  doSend = last_sent_count < SEND_REPEAT_FAST_COUNT;
  if(!doSend) {
    if(strcmp(radiopacket, "") == 0) {
      doSend = last_sent_time + SEND_REPEAT_SLOW_EMPTY_DELAY < millis();
    } else {
      doSend = last_sent_time + SEND_REPEAT_SLOW_DELAY < millis();
    }
  }

  Serial.print("radiopacket: ");
  Serial.print(radiopacket);
  Serial.print(" last_sent_state: ");
  Serial.print(last_sent_state);
  Serial.print(" last_sent_count: ");
  Serial.print(last_sent_count);
  Serial.print(" last_sent_time: ");
  Serial.print(last_sent_time);
  Serial.print(" millis: ");
  Serial.print(millis());
  Serial.print(" doSend: ");  
  if (doSend) {
    Serial.println(" true");  
  } else {
    Serial.println(" false");  
  }

  // Check if we need to resend
  // if(anyButtonDown || lastButtonReleased) {
  if (doSend) {
    // Status LED we will send
    digitalWrite(LED_BUILTIN, HIGH);

    Serial.print("Sending "); Serial.println(radiopacket);
    // Send a message to the DESTINATION!
    if (!rf69_manager.sendtoWait((uint8_t *)radiopacket, strlen(radiopacket), DEST_ADDRESS)) {
      Serial.println("Sending failed (no ack)");
    }
    last_sent_time = millis();
    strcpy(last_sent_state, radiopacket);    
    last_sent_count += 1;
  }

  last_R = curr_R;
  last_Y = curr_Y;
  last_START = curr_START;
  last_SELECT = curr_SELECT;
  last_UP = curr_UP;
  last_DOWN = curr_DOWN;
  last_LEFT = curr_LEFT;
  last_RIGHT = curr_RIGHT;

  if(!playing_melody && (strcmp(last_sent_state, radiopacket)==0) && (last_sent_count_reset_time+SHALLOW_SLEEP_TIME<millis())) {
    delay(SHALLOW_SLEEP_DELAY);
  } else {
    delay(MIN_DELAY);
  }
  digitalWrite(LED_BUILTIN, LOW);
}