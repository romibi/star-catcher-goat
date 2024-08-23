#include <RCSwitch.h> // see https://github.com/sui77/rc-switch

// =========
// Constants
// =========
#define REPEAT_DELAY 1000
#define MIN_DELAY 10

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
  pinMode(BTN_R, INPUT);
  pinMode(BTN_Y, INPUT);
  pinMode(BTN_START, INPUT);
  pinMode(BTN_SELECT, INPUT);
  pinMode(BTN_UP, INPUT);
  pinMode(BTN_RIGHT, INPUT);
  pinMode(BTN_LEFT, INPUT);
  pinMode(BTN_DOWN, INPUT);
}

int sentDelay = REPEAT_DELAY+1;
unsigned int sentValue = 65534;

void loop() {
  unsigned int value = 0;
  unsigned int valueCorrection = 0;
  unsigned long sendValue = 0;

  // Read Buttons
  value = bit_set_to(value, 0, digitalRead(BTN_R)==HIGH);
  value = bit_set_to(value, 1, digitalRead(BTN_Y)==HIGH);
  value = bit_set_to(value, 2, digitalRead(BTN_START)==HIGH);
  value = bit_set_to(value, 3, digitalRead(BTN_SELECT)==HIGH);
  value = bit_set_to(value, 4, digitalRead(BTN_UP)==HIGH);
  value = bit_set_to(value, 5, digitalRead(BTN_RIGHT)==HIGH);
  value = bit_set_to(value, 6, digitalRead(BTN_LEFT)==HIGH);
  value = bit_set_to(value, 7, digitalRead(BTN_DOWN)==HIGH);

  // Check if we need to resend
  if(value == sentValue) {
    // value is unchanged, can wait longer
    sentDelay += MIN_DELAY;
  
    if(sentDelay < REPEAT_DELAY) {
      // sent not long ago, wait and redo loop
      delay(MIN_DELAY);
      return;
    }
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
  Serial.print(value+256, BIN);
  Serial.print(" -> ");
  Serial.print(valueCorrection, BIN);
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