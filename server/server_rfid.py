#!/usr/bin/python2
#------------------------------------
# get events via REST API from mbox
# and control LED ...
# by jc://design/
#------------------------------------

from socket import *
import time
import requests, math
import os
import logging
import signal
import subprocess

import RPi.GPIO             as GPIO

import modules.jcJson       as jcJSON
import modules.config_stage as stage
import modules.config_mbox  as mbox

import modules_gpio.MFRC522 as MFRC522
import modules_gpio.config  as gpio

# set start time and write title/version/stage
#----------------------------------------------
mbox.start_time = time.time()
print("--------------------------------")
print(mbox.APIname_RFID + mbox.APIversion + "   (" + str(stage.rollout) + ")")
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
  logging.info("Start RFID module: TEST STAGE ("+get_active_stage()+")")
  url  = "http://127.0.0.1:"+str(stage.server_port)+"/api/"
  this_stage = "test"
else:
  logging.info("Start RFID module: PROD STAGE ("+get_active_stage()+")")
  url  = "http://127.0.0.1:"+str(stage.server_port)+"/api/"
  this_stage = "prod"


#-----------------------------------

cmd              = {}
cmd["status"]    = url+"status/"
cmd["setcard"]   = url+"set-card/" # + card_id

wait             = 0.5

ProcessRunning   = True
ServerRunning    = False

#----------------------

def call_api(command,card_id):
    data1 = {}
    logging.info("Read API: " + command + ":" + card_id)

    try:
      response = requests.put(cmd[command] + card_id + "/")
      data1     = response.json()

    except requests.exceptions.RequestException as e:
      logging.info("Error connecting to API: " + str(e))
      data1     = {}

    return data1

#----------------------

def loop_rfid_read():

    global ProcessRunning, other, MIFAREReader, this_stage

    i            = 0
    first_run    = 1
    last_active  = ""
    act_active   = ""
    card_id      = ""

    logging.info("Start RFID detection ...")

    while ProcessRunning:

        # switch on/off
        act_active = get_active_stage()

        #logging.info("STAGE..."+act_active+"/"+last_active+"//"+this_stage)
        if (act_active == "" or act_active != last_active):

            logging.info("STAGE...DIFFERENT ("+act_active+"/"+this_stage+")" )
            last_active = act_active


        if this_stage == act_active:

           # Scan for card
           (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

           # If a card is found
           if status == MIFAREReader.MI_OK:
               logging.info( "Card detected." )

               # Get the UID of the card
               (status,uid) = MIFAREReader.MFRC522_Anticoll()

               # If we have the UID, continue
               if status == MIFAREReader.MI_OK:

                  # Print UID
                  logging.info("Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3]))
                  card_id = str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])
                  call_api("setcard",card_id)
                  time.sleep(int(wait*3))
                  i = 1

           else:
               if card_id == "":
                  logging.info( "waiting ..." )

               else:
                  card_id == ""
                  if i > 0:
                     i = 0
                  elif i != -1:
                     call_api("setcard","no_card")
                     i = -1


           time.sleep(wait)




def end_all(end1,end2):
    global ProcessRunning
    ProcessRunning = False
    call_api("setcard","no_card")



#-----------------------------------


# Hook the SIGINT
signal.signal(signal.SIGINT, end_all)


# init loggin


#-----------------------------------

if __name__ == '__main__':

   # Create an object of the class MFRC522
   MIFAREReader = MFRC522.MFRC522()

   loop_rfid_read()

#-----------------------------------
