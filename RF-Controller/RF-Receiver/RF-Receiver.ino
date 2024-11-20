// rf69 demo tx rx.pde
// -*- mode: C++ -*-
// Example sketch showing how to create a simple addressed, reliable
// messaging client with the RH_RF69 class.
// It is designed to work with the other example RadioHead69_AddrDemo_TX.
// Demonstrates the use of AES encryption, setting the frequency and
// modem configuration.

#include <SPI.h>
#include <RH_RF69.h>
#include <RHReliableDatagram.h>
#include <Keyboard.h>

/************ Radio Setup ***************/

// Change to 434.0 or other frequency, must match RX's freq!
#define RF69_FREQ 433.0

// Who am i? (client address)
#define MY_ADDRESS   1

// Where to send packets to!
// #define DEST_ADDRESS 2 // we answer to whoever sends

// What are the buttons mapped to?
#define BTN_KEY_R KEY_RETURN
#define BTN_KEY_Y ' '
#define BTN_KEY_START KEY_ESC
#define BTN_KEY_SELECT KEY_BACKSPACE
#define BTN_KEY_UP KEY_UP_ARROW
#define BTN_KEY_DOWN KEY_DOWN_ARROW
#define BTN_KEY_LEFT KEY_LEFT_ARROW
#define BTN_KEY_RIGHT KEY_RIGHT_ARROW


// First 3 here are boards w/radio BUILT-IN. Boards using FeatherWing follow.
#if defined (__AVR_ATmega32U4__)  // Feather 32u4 w/Radio
  #define RFM69_CS    8
  #define RFM69_INT   7
  #define RFM69_RST   4
  #define LED        13
#endif

#define MIN_DELAY 10
#define CONNECTION_LOST_TIMEOUT 10000

// Singleton instance of the radio driver
RH_RF69 rf69(RFM69_CS, RFM69_INT);

// Class to manage message delivery and receipt, using the driver declared above
RHReliableDatagram rf69_manager(rf69, MY_ADDRESS);

bool USE_SERIAL = true; // false;

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

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(1000);
  //while (!Serial) delay(1); // Wait for Serial Console (comment out line if no computer)

  pinMode(LED, OUTPUT);
  pinMode(RFM69_RST, OUTPUT);
  digitalWrite(RFM69_RST, LOW);

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
    Serial.println("RFM69 setFrequency failed");
  }

  // If you are using a high power RF69 eg RFM69HW, you *must* set a Tx power with the
  // ishighpowermodule flag set like this:
  rf69.setTxPower(20, true);  // range from 14-20 for power, 2nd arg must be true for 69HCW

  // The encryption key has to be the same as the one in the server
  uint8_t key[] = { 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
                    0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08 };
  rf69.setEncryptionKey(key);

  Serial.print("RFM69 radio @");  Serial.print((int)RF69_FREQ);  Serial.println(" MHz");
}

// Dont put this on the stack:
uint8_t data[] = "And hello back to you";
// Dont put this on the stack:
uint8_t buf[RH_RF69_MAX_MESSAGE_LEN];

#define command_send_buffer_size 20
String command_send_buffer[command_send_buffer_size];
int csb_add_index = 0;
int csb_send_index = 0;

unsigned long last_received_time = 0;
String connection_state = "CONNECTION: UNKNOWN";
String last_color_state = "COLOR:g";
String last_button_state = "BUTTONS:";

void loop() {
  // parse commands from serial
  if(Serial.available()>0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.equals("state")) {
      Serial.println(last_color_state);
      Serial.println(connection_state);
      Serial.println(last_button_state);
    } else if (command.equals("serial on")) {
      // deprecated command?
      USE_SERIAL = true;
      
      if(last_R) Keyboard.release(BTN_KEY_R);
      if(last_Y) Keyboard.release(BTN_KEY_Y);
      if(last_START) Keyboard.release(BTN_KEY_START);
      if(last_SELECT) Keyboard.release(BTN_KEY_SELECT);
      if(last_UP) Keyboard.release(BTN_KEY_UP);
      if(last_DOWN) Keyboard.release(BTN_KEY_DOWN);
      if(last_LEFT) Keyboard.release(BTN_KEY_LEFT);
      if(last_RIGHT) Keyboard.release(BTN_KEY_RIGHT);

      return;
    } else if (command.equals("serial off")) {
      // deprecated command?
      USE_SERIAL = false;
      
      last_R = false;
      last_Y = false;
      last_START = false;
      last_SELECT = false;
      last_UP = false;
      last_DOWN = false;
      last_LEFT = false;
      last_RIGHT = false;
      return;
    } else if (!command.equals("")) { // command for controller
      int csb_index = (csb_add_index+1) % command_send_buffer_size;

      if(csb_index==csb_send_index) {
        Serial.println("Warning: command send buffer full!");
      } else {
        command_send_buffer[csb_index] = command;
        csb_add_index = csb_index;
      }

      /* int str_len = command.length() + 1;
      char cmddata[str_len];
      command.toCharArray(cmddata, str_len);

      //if (!rf69_manager.sendtoWait(cmddata, sizeof(cmddata), DEST_ADDRESS)) {
      if (!rf69_manager.sendto(cmddata, sizeof(cmddata), DEST_ADDRESS)) {
        Serial.println("RFM69 Sending failed (no ack)");
      } */
    }
  }

  // receive data from RF
  if (rf69_manager.available()) {
    // Wait for a message addressed to us from the client
    uint8_t len = sizeof(buf);
    uint8_t from;
    
    //if (rf69_manager.recvfromAck(buf, &len, &from)) {
    if (rf69_manager.recvfromAck(buf, &len, &from)) {      
      bool print = !connection_state.equals("CONNECTION:OK");
      connection_state = "CONNECTION:OK";
      last_received_time = millis();
      if (print) {
        Serial.println(connection_state);
      }
      // first of all send queued commands
      if(csb_send_index!=csb_add_index) {
        String commands = "";
        while(csb_send_index!=csb_add_index) {
          commands += command_send_buffer[csb_send_index] + ";" ;
          csb_send_index = (csb_send_index + 1) % command_send_buffer_size;
        }
        commands.trim();
        commands = commands.substring(0, commands.length() - 1);
        
        int str_len = commands.length() + 1;
        char cmddata[str_len];
        commands.toCharArray(cmddata, str_len);
        Serial.println("Sending:"+commands);

        if (!rf69_manager.sendtoWait(cmddata, sizeof(cmddata), from)) {
          Serial.println("RFM69 Sending failed (no ack)");
        }
      }

      // Handle received
      buf[len] = 0; // zero out remaining string
      
      String received = String((char*)buf);
      if(received.startsWith("C:")) {
        String serial_out = "COLOR:"+received.substring(2);
        Serial.println(serial_out);
        last_color_state = serial_out;
      } else if(USE_SERIAL) {
        String serial_out = "BUTTONS:"+String((char*)buf);
        Serial.println(serial_out);
        last_button_state = serial_out;
      } else {

        Serial.print("RFM69 Got packet from #"); Serial.print(from);
        Serial.print(" [RSSI :");
        Serial.print(rf69.lastRssi());
        Serial.print("] : ");
        Serial.println((char*)buf);

        curr_R = false;
        curr_Y = false;
        curr_START = false;
        curr_SELECT = false;
        curr_UP = false;
        curr_DOWN = false;
        curr_LEFT = false;
        curr_RIGHT = false;

        for (int i=0; i < len; i++) {
          switch(buf[i]) {
            case 'R':
              curr_R = true;
              break;
            case 'Y':
              curr_Y = true;
              break;
            case 'S':
              curr_START = true;
              break;
            case 's':
              curr_SELECT = true;
              break;
            case 'u':
              curr_UP = true;
              break;
            case 'd':
              curr_DOWN = true;
              break;
            case 'l':
              curr_LEFT = true;
              break;
            case 'r':
              curr_RIGHT = true;
              break;
          }
        }
      }
    } else {
      bool print = !connection_state.equals("CONNECTION:UNSTABLE");
      connection_state = "CONNECTION: UNSTABLE";
      if (print) {      
        Serial.println(connection_state);
      }
    }
  } else {
    if (!connection_state.equals("CONNECTION:LOST")) {
      if (last_received_time + CONNECTION_LOST_TIMEOUT < millis()) {
        connection_state = "CONNECTION:LOST";
        Serial.println(connection_state);
      }
    }
  }
  if(!USE_SERIAL) {
    // update button states
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

    // send Keyboard events
    if(trigger_R) Keyboard.press(BTN_KEY_R);
    if(trigger_Y) Keyboard.press(BTN_KEY_Y);
    if(trigger_START) Keyboard.press(BTN_KEY_START);
    if(trigger_SELECT) Keyboard.press(BTN_KEY_SELECT);
    if(trigger_UP) Keyboard.press(BTN_KEY_UP);
    if(trigger_DOWN) Keyboard.press(BTN_KEY_DOWN);
    if(trigger_LEFT) Keyboard.press(BTN_KEY_LEFT);
    if(trigger_RIGHT) Keyboard.press(BTN_KEY_RIGHT);

    if(released_R) Keyboard.release(BTN_KEY_R);
    if(released_Y) Keyboard.release(BTN_KEY_Y);
    if(released_START) Keyboard.release(BTN_KEY_START);
    if(released_SELECT) Keyboard.release(BTN_KEY_SELECT);
    if(released_UP) Keyboard.release(BTN_KEY_UP);
    if(released_DOWN) Keyboard.release(BTN_KEY_DOWN);
    if(released_LEFT) Keyboard.release(BTN_KEY_LEFT);
    if(released_RIGHT) Keyboard.release(BTN_KEY_RIGHT);

    // prepare next loop
    last_R = curr_R;
    last_Y = curr_Y;
    last_START = curr_START;
    last_SELECT = curr_SELECT;
    last_UP = curr_UP;
    last_DOWN = curr_DOWN;
    last_LEFT = curr_LEFT;
    last_RIGHT = curr_RIGHT;
  }

  delay(MIN_DELAY);
}