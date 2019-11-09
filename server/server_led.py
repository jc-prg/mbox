#!/usr/bin/python3
#------------------------------------
# get events via REST API from mbox
# and control LED ...
# by jc://design/
#------------------------------------

from socket import *
import RPi.GPIO as GPIO
import time
import requests, math
import os
import logging
import signal
import subprocess

import modules.jcJson       as jcJSON
import modules.config_stage as stage
import modules.config_mbox  as mbox
import modules_gpio.light   as led
import modules_gpio.config  as gpio

# set start time and write title/version/stage
#----------------------------------------------
mbox.start_time = time.time()
print("--------------------------------")
print(mbox.APIname_LED + mbox.APIversion + "   (" + str(stage.rollout) + ")")
print("--------------------------------")

# start and configure logging
#----------------------------------------------
import logging
if stage.test:
    if mbox.DEBUG:
       logging.basicConfig(level=logging.DEBUG)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
       logging.info("Start - Log-Level DEBUG ...")
    else:
       logging.basicConfig(level=logging.INFO)   # DEBUG, INFO, WARNING, ERROR, CRITICAL
       logging.info("Start - Log-Level INFO ...")
else:
   logging.basicConfig(level=logging.WARN)    # DEBUG, INFO, WARNING, ERROR, CRITICAL
   logging.info("Start - Log-Level WARN ...")

#-----------------------------------
# init
#-----------------------------------

# read from file, which stage should be use ... to switch between stages during runtime
def get_active_stage():
  settings = jcJSON.read("../../active")
  return settings["active_stage"]

if stage.test == True:
  logging.info("Start LED module: TEST STAGE ("+get_active_stage()+")")
  url  = "http://127.0.0.1:"+str(stage.server_port)+"/api/"
  this_stage = stage.rollout
else:
  logging.info("Start LED module: PROD STAGE ("+get_active_stage()+")")
  url  = "http://127.0.0.1:"+str(stage.server_port)+"/api/"
  this_stage = stage.rollout


#-----------------------------------

cmd              = {}
cmd["status"]    = url+"status/"

wait             = 0.5

ProcessRunning   = True
ServerRunning    = False

#----------------------

def call_api(command):
    data1 = {}
    logging.debug("Read API: " + command)

    try:
      response = requests.get(cmd[command])
      data1    = response.json()
    except requests.exceptions.RequestException as e:
      logging.info("Error connecting to API: " + str(e))
      data1     = {}

    return data1

def loop():
    '''read volume and switch on LED to show level'''

    global light, ProcessRunning, other

    i            = 0
    first_run    = 1
    last_active  = ""
    act_active   = ""
    light_error  = "0"
    light_stage  = "1"
    light_rfid   = "0"

    light.other  = "000000"
    light.volume = 0

    while ProcessRunning:

        # switch on/off
        act_active = get_active_stage()
        #logging.info("STAGE..."+act_active+"/"+last_active+"//"+this_stage)
        if (act_active == "" or act_active != last_active):
            logging.info("STAGE...DIFFERENT ("+act_active+")" )
            if (act_active == this_stage):  light.start_gpio()
            else:                           light.stop_gpio()
            last_active = act_active
            light.stage = this_stage

        # initial
        if first_run == 1:
            time.sleep(wait)
            a = 0
            light.other  = "111111"
            while a <= 10:
               light.volume = a
               time.sleep(0.3)
               a += 1

            light.other  = "111111"
            time.sleep(wait*3)
            first_run = 0

        else:
            # set status lights
            light.other = str(light_error) + "111" + str(light_stage) + str(light_rfid)

            # reduce requests
            time.sleep(wait)

            # check if ative stage
            if (act_active == this_stage):

                # if active check volume and show
                light_error = "0"
                data        = call_api("status")

                if "API" in data: logging.debug(str(data["API"]))

                if i == 0:
                    i = 1
                    if this_stage == "test": light_stage = "1"
                    else:                    light_stage = "1"
                else     :
                    i = 0
                    if this_stage == "test": light_stage = "0"
                    else:                    light_stage = "1"

                # if card is detected ...
                if "LOAD" in data:
                  if "RFID" in data["LOAD"]:
                    light_rfid = "0"
                    if   data["LOAD"]["RFID"] == mbox.demo_card:
                        first_run = 1

                    elif data["LOAD"]["RFID"] != "":
                        light_rfid = "1"
                        logging.info(data["LOAD"]["RFID"])

                # if not mute show volume level
                if "STATUS" in data:
                    if (data["STATUS"]["playback"]["mute"] == 0):
                        light.volume = round(data["STATUS"]["playback"]["volume"]*10)
                        logging.debug("Volume: "+str(light.volume))
                        #logging.info(this_stage+":Volume: "+str(light.volume))

                    # else blink with 1 LED
                    else:
                        if i == 0: light.volume = 0
                        else:      light.volume = 1
                        logging.debug("Volume: MUTE")

                # else blink with 1 LED - red (not connected)
                else:
                    if i == 0:
                        light_error = "0"
                        light.volume = 0
                    else:
                        light_error = "1"
                        light.volume = 0
                    logging.debug("Volume: ERROR")


def end_all(end1,end2):
    global light, ProcessRunning

    ProcessRunning = False
    light.stop()


def checkRunning():
   psAx1 = subprocess.check_output(["ps", "ax"])
   if "server.py" in str(psAx1):
     return True
   else:
     return False

#-----------------------------------


# Hook the SIGINT
signal.signal(signal.SIGINT, end_all)


# init loggin
logging.basicConfig(level=logging.INFO)
logging.info("Start LED control ...")


#-----------------------------------

if __name__ == '__main__':

   light = led.lightThread(3,"Thread LED Control",1,this_stage)
   light.start()
   light.destroy

   loop()

#-----------------------------------
