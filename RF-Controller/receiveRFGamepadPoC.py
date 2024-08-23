#!/usr/bin/env python3

import argparse
import signal
import sys
import time
import logging

from rpi_rf import RFDevice

rfdevice = None

expectedProtocol=2
baseValue=604700672
minValue=604700672 # all buttons pressed
maxValue=604765952 # no buttons pressed

# pylint: disable=unused-argument
def exithandler(signal, frame):
    rfdevice.cleanup()
    sys.exit(0)

# from https://stackoverflow.com/a/9945785
def is_set(x, n):
    return x & 2 ** n != 0

logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S',
                    format='%(asctime)-15s - [%(levelname)s] %(module)s: %(message)s', )

parser = argparse.ArgumentParser(description='Receives a decimal code via a 433/315MHz GPIO device')
parser.add_argument('-g', dest='gpio', type=int, default=27,
                    help="GPIO pin (Default: 27)")
args = parser.parse_args()

signal.signal(signal.SIGINT, exithandler)
rfdevice = RFDevice(args.gpio)
rfdevice.enable_rx()
timestamp = None
logging.info("Listening for codes on GPIO " + str(args.gpio))
while True:
    if rfdevice.rx_code_timestamp != timestamp:
        timestamp = rfdevice.rx_code_timestamp
        value = rfdevice.rx_code
        value = value - baseValue
        valueA = value & 255
        valueB = (~(value >> 8)) & 255

        if valueA == valueB:
            logging.info(f"received: {valueA}")
            if is_set(value, 0):
                logging.info("Red Button Pressed")
            if is_set(value, 1):
                logging.info("Yellow Button Pressed")
            if is_set(value, 2):
                logging.info("Start Button Pressed")
            if is_set(value, 3):
                logging.info("Select Button Pressed")
            if is_set(value, 4):
                logging.info("Up Button Pressed")
            if is_set(value, 5):
                logging.info("Right Button Pressed")
            if is_set(value, 6):
                logging.info("Left Button Pressed")
            if is_set(value, 7):
                logging.info("Down Button Pressed")
        #logging.info(str(rfdevice.rx_code) +
        #             " [pulselength " + str(rfdevice.rx_pulselength) +
        #             ", protocol " + str(rfdevice.rx_proto) + "]")
    time.sleep(0.01)
rfdevice.cleanup()
