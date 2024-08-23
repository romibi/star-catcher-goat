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

// ====
// Code
// ====
RCSwitch mySwitch = RCSwitch();

// code by https://stackoverflow.com/a/47990
inline int bit_set_to(int number, int n, bool x) {
    return (number & ~((int)1 << n)) | ((int)x << n);
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
}

int sentDelay = REPEAT_DELAY+1;
unsigned int sentValue = 65534;
int sentCount = 0;

void loop() {
  unsigned int value = 0;
  unsigned int valueCorrection = 0;
  unsigned long sendValue = 0;

  // Read Buttons
  value = bit_set_to(value, 0, digitalRead(BTN_R)==LOW);
  value = bit_set_to(value, 1, digitalRead(BTN_Y)==LOW);
  value = bit_set_to(value, 2, digitalRead(BTN_START)==LOW);
  value = bit_set_to(value, 3, digitalRead(BTN_SELECT)==LOW);
  value = bit_set_to(value, 4, digitalRead(BTN_UP)==LOW);
  value = bit_set_to(value, 5, digitalRead(BTN_RIGHT)==LOW);
  value = bit_set_to(value, 6, digitalRead(BTN_LEFT)==LOW);
  value = bit_set_to(value, 7, digitalRead(BTN_DOWN)==LOW);

  // Check if we need to resend
  if(value == sentValue) {
    if(sentCount <= SEND_REPEAT_FAST_COUNT) {
      sentCount++;
    } else {
      // value is unchanged and we sent it already a few times quickly, can wait longer now
      sentDelay += MIN_DELAY;
  
      if(sentDelay < REPEAT_DELAY) {
        // sent not long ago, wait and redo loop
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

  delay(MIN_DELAY);  
  digitalWrite(LED_BUILTIN, LOW);
}