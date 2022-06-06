#!/usr/bin/python3
#------------------------------------
# get events via REST API from mbox
# and control LED ...
# by jc://design/
#------------------------------------

#from socket import *
import RPi.GPIO as GPIO
import time
import requests
import logging
import signal
import subprocess

import modules.json_db       as jcJSON
import modules.config_stage as stage
import modules.config_mbox  as mbox
import modules_gpio.light   as led
import modules_gpio.config  as gpio

# set start time and write title/version/stage
#----------------------------------------------
mbox.start_time = time.time()
print("----------------------------------------")
print(" TEST : " + mbox.api_name_LED + mbox.api_version + "   (" + str(stage.rollout) + ")")
print("----------------------------------------")

# start and configure logging
#----------------------------------------------

stage.init_logging(mbox.api_name_LED + mbox.api_version + "   (test-script/" + str(stage.log_level) + ")", '/log/server_LED.log')


#-----------------------------------
# init
#-----------------------------------

wait             = 0.5
ProcessRunning   = True
ServerRunning    = False

#----------------------

def loop():
    '''read volume and switch on LED to show level'''

    global light, ProcessRunning, other
    test = [
          ["00000000","00000000"],
          ["00000000","00000001"],
          ["00000000","00000011"],
          ["00000000","00000111"],
          ["00000000","00001111"],
          ["00000000","00011111"],
          ["00000000","00111111"],
          ["00000000","01111111"],
          ["00000000","11111111"],
          ["00000001","11111111"],
          ["00000011","11111111"],
          ["00000111","11111111"],
          ["00001111","11111111"],
          ["00011111","11111111"],
          ["00111111","11111111"],
          ["01111111","11111111"],
          ["11111111","11111111"],
          ["00000000","00000000"],
          ["00000000","00000001"],
          ["00000000","00000010"],
          ["00000000","00000100"],
          ["00000000","00001000"],
          ["00000000","00010000"],
          ["00000000","00100000"],
          ["00000000","01000000"],
          ["00000000","10000000"],
          ["00000001","00000000"],
          ["00000010","00000000"],
          ["00000100","00000000"],
          ["00001000","00000000"],
          ["00010000","00000000"],
          ["00100000","00000000"],
          ["01000000","00000000"],
          ["10000000","00000000"]
    ]

    a = 0
    while ProcessRunning:

        time.sleep(wait)
        light.write_string(test[a])
        logging.info(str(test[a]))
        
        if a < 33:  a += 1
        else:       a =  0



def end_all(end1,end2):
    global light, ProcessRunning

    ProcessRunning = False
    light.stop()


#-----------------------------------


# Hook the SIGINT
signal.signal(signal.SIGINT, end_all)


# init loggin
logging.basicConfig(level=logging.INFO)
logging.info("Start LED control ...")


#-----------------------------------

if __name__ == '__main__':

   light = led.lightThread(3,"Thread LED Control",1,stage.rollout)
   light.start_gpio()
#   light.start()
#   light.destroy

   loop()

#-----------------------------------
