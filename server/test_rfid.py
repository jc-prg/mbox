#!/usr/bin/python2
#------------------------------------
# get events via REST API from mbox
# and control LED ...
# by jc://design/
#------------------------------------

print("TEST")

from socket import *
import time
import requests
import logging
import signal

import modules.jcJson       as jcJSON
import modules.config_stage as stage
import modules.config_mbox  as mbox

# set start time and write title/version/stage
#----------------------------------------------
mbox.start_time = time.time()
print("--------------------------------")
print(mbox.APIname_RFID + mbox.APIversion + "   (" + str(stage.rollout) + ")")
print("--------------------------------")

#---------------------------------------------

import RPi.GPIO             as GPIO
import modules_gpio.config  as gpio
import modules_rfid.MFRC522 as MFRC522

#---------------------------------------------

stage.test = True

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

wait             = 0.5

ProcessRunning   = True
ServerRunning    = False

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

           # reset card_id for testing
           card_id      = ""

           # Scan for card
           (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

           # If a card is found
           if status == MIFAREReader.MI_OK:
               logging.info( "Card detected ... " +str(status)  )

               # Get the UID of the card
               (status,uid) = MIFAREReader.MFRC522_Anticoll()

               # If we have the UID, continue
               if status == MIFAREReader.MI_OK:

                  # Print UID
                  logging.info("Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3]))
                  card_id = str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])
                  #call_api("setcard",card_id)
                  print(card_id)
                  time.sleep(int(wait*3))
                  i = 1

           else:
               if card_id == "":
                  logging.info( "waiting ... " + str(status) )

               else:
                  card_id == ""
                  if i > 0:
                     i = 0
                  elif i != -1:
                     #call_api("setcard","no_card")
                     i = -1


           time.sleep(wait)




def end_all(end1,end2):
    global ProcessRunning
    ProcessRunning = False


#-----------------------------------


# Hook the SIGINT
signal.signal(signal.SIGINT, end_all)


# init loggin


#-----------------------------------

if __name__ == '__main__':

   print("test")

   # Create an object of the class MFRC522
   MIFAREReader = MFRC522.MFRC522()

   loop_rfid_read()

#-----------------------------------
