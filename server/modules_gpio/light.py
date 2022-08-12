#!/usr/bin/python2 
# -*- coding: utf8 -*-
# ---------------------------

# ------------------------------------
# LED for jc://mbox/
# (c) Christoph Kloth
# ------------------------------------

from multiprocessing import Process, Value
from socket import *

import RPi.GPIO as GPIO
import threading
import logging
import time
import os

import modules_gpio.config as led

# -----------------------------------

SDI = led.led_pins["SDI"]
RCLK = led.led_pins["RCLK"]
SRCLK = led.led_pins["SRCLK"]


# -----------------------------------

class lightThread(threading.Thread):

    def __init__(self, threadID, name, counter, stage):
        """set initial values to vars"""

        # init thread
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.stopProcess = False

        self.led_init = {}
        self.led_init["OFF"] = [0x00]
        self.led_init["ALL"] = [0xff]
        self.led_init["INIT"] = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]
        self.led_speed = 0.1
        self.led_string = ['00001111', '11111111']
        self.volume = 0
        self.stage = stage
        self.on = False
        self.other = "000000"

    def run(self):
        logging.info(self.stage + ":Starting " + self.name)
        self.setup()
        self.init()

        write_volume(self)

        logging.info(self.stage + ":Exiting " + self.name)

    def stop(self):
        """stop led loop"""

        self.stopProcess = True
        self.destroy()

    # ---------------------------------
    def setup(self):
        """start GPIO"""

        # global GPIO, SDI, RCLK, SRCLK
        self.start_gpio()

    def start_gpio(self):

        if self.on: return
        logging.info(self.stage + ":GPIO setup")
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        try:
            GPIO.setup(SDI, GPIO.OUT)
            GPIO.setup(RCLK, GPIO.OUT)
            GPIO.setup(SRCLK, GPIO.OUT)
            GPIO.output(SDI, GPIO.LOW)
            GPIO.output(RCLK, GPIO.LOW)
            GPIO.output(SRCLK, GPIO.LOW)
            self.on = True
        except:
            logging.warn(self.stage + ":Error initializing GPIO")

    def stop_gpio(self):
        '''stop GPIO to avoid error for next start'''

        if not self.on: return
        logging.info(self.stage + ":Clean GPIO")
        GPIO.cleanup()
        self.on = False

    def destroy(self):
        """stop GPIO to avoid error for next start"""

        if not self.on: return
        logging.info(self.stage + ":Clean GPIO")
        GPIO.cleanup()
        self.on = False

    def hc595_in(self, dat):
        """send data to a single register"""

        global GPIO, SDI, RCLK, SRCLK
        if self.on != True: return

        for bit in range(0, 8):
            GPIO.output(SDI, 0x80 & (dat << bit))
            GPIO.output(SRCLK, GPIO.HIGH)
            time.sleep(0.001)
            GPIO.output(SRCLK, GPIO.LOW)

    def hc595_in_multi(self, dat):
        """send data to two or more register"""

        global GPIO, SDI, RCLK, SRCLK
        if self.on != True: return

        i = 0
        while i < len(dat):

            for bit in range(0, 8):
                GPIO.output(SDI, 0x80 & (dat[i] << bit))
                GPIO.output(SRCLK, GPIO.HIGH)
                time.sleep(0.001)
                GPIO.output(SRCLK, GPIO.LOW)

            time.sleep(self.led_speed)
            i = i + 1

    def hc595_out(self):
        """send data out"""

        global GPIO, SDI, RCLK, SRCLK
        if self.on != True: return

        GPIO.output(RCLK, GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(RCLK, GPIO.LOW)

    # ---------------------------------

    def init(self):
        """Test all LEDs"""

        logging.debug(self.stage + ":Init LEDs")
        LEDtest = self.led_init["INIT"]

        for i in range(0, len(LEDtest)):
            self.hc595_in_multi([0x00, LEDtest[i]])
            self.hc595_out()

        for i in range(0, len(LEDtest)):
            self.hc595_in_multi([LEDtest[i], 0x00])
            self.hc595_out()

    # ---------------------------------

    def write_string(self, string):
        """write byte string"""

        self.hc595_in_multi([int(string[0], 2), int(string[1], 2)])
        self.hc595_out()


# ---------------------------------
other = "111111"


def write_volume(thread):
    """
    write volume
    """

    vol = [
        ["00", "00000000"],
        ["00", "00000001"],
        ["00", "00000011"],
        ["00", "00000111"],
        ["00", "00001111"],
        ["00", "00011111"],
        ["00", "00111111"],
        ["00", "01111111"],
        ["00", "11111111"],
        ["01", "11111111"],
        ["11", "11111111"],
        ["00", "00000000"],
        ["00", "00000001"],
        ["00", "00000010"],
        ["00", "00000100"],
        ["00", "00001000"],
        ["00", "00010000"],
        ["00", "00100000"],
        ["00", "01000000"],
        ["00", "10000000"],
        ["01", "00000000"],
        ["10", "00000000"],
    ]

    running = True
    while running and not thread.stopProcess:

        if thread.volume > 100:
            index = int(thread.volume / 100)
        else:
            index = int(thread.volume)

        try:
            a = vol[index]
        except Exception as e:
            logging.error("Error Volume Index: " + str(index))

        b = [thread.other + a[0], a[1]]
        logging.info(thread.stage + ":Volume: " + str(thread.volume) + "/" + b[0] + " " + b[1])
        thread.write_string(b)
        time.sleep(0.1)

    # logging.info("Volume: "+vol[self.volume][0]+vol[self.volume][1])
    # self.write_string(vol)
    # time.sleep(self.led_speed)

# -----------------------------------
