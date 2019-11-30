#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import modules_rfid.MFRC522      as MFRC522
import modules.jcJson            as jcJSON
import modules.config_stage      as stage
import signal
import threading
import time
import logging

#-----------------------------------
# init
#-----------------------------------

exitFlag  = 0
rfid_ctrl = {}

logging.basicConfig(level=logging.INFO)

# read from file, which stage should be use ... to switch between stages during runtime
def get_active_stage():
  settings = jcJSON.read("../../active")
  return settings["active_stage"]

if stage.test == True:  this_stage = "test"
else:                   this_stage = "prod"

#------------------------------

# THREADING CLASS

class rfidThread (threading.Thread):

   def __init__(self, threadID, name, counter):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name     = name
      self.counter  = counter
      self.stopProcess = False

   def run(self):
      logging.info( "Starting " + self.name )
      rfidRead(self)
      logging.info( "Exiting " + self.name )

   def stop(self):
      self.stopProcess = True


# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Check card reader for ID
def rfidRead(thread):

  global MIFAREReader, rfid_ctrl, continueReading

  # endless loop
  continueReading = True
  while continueReading and not thread.stopProcess:

    # Wait a few seconds
    time.sleep(0.5)

    # check if ative stage
    if (get_active_stage() == this_stage):

      # Scan for card
      (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

      # If a card is found
      if status == MIFAREReader.MI_OK:
        logging.info( "Card detected" )

      # Get the UID of the card
      (status,uid) = MIFAREReader.MFRC522_Anticoll()

      # If we have the UID, continue
      if status == MIFAREReader.MI_OK:

        # Print UID
        logging.info("Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3]))
        rfid_ctrl["cardUID"] = str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])

        time.sleep(5)

        rfid_ctrl["cardUID"] = ""
