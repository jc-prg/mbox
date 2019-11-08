#!/usr/bin/python2
# -*- coding: utf8 -*-
#---------------------------
# -> NOT IN USE AT THE MOMENT

import configparser
import sys, getopt
import time, binascii
import netaddr, signal
import logging
import uuid
import copy
import json
import couchdb

from os import path
from Crypto.Cipher import AES
from multiprocessing import Process

import modules.config_stage   as stage
import modules.config_mbox    as mbox
import modules.jcJson         as jcJSON
import modules.jcCouchDB      as jcCouch
import modules.music_load     as music_load
import modules.music_control  as music_ctrl
import modules.stream_control as radio_ctrl

from modules.runcmd         import *

#---------------------------

Status     = "Starting"
ExitPrg    = False
Stage      = mbox.initial_stage

#-------------------------------------------------

if stage.test:
    if mbox.DEBUG: logging.basicConfig(level=logging.DEBUG)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    else:          logging.basicConfig(level=logging.INFO)   # DEBUG, INFO, WARNING, ERROR, CRITICAL
else:              logging.basicConfig(level=logging.WARN)    # DEBUG, INFO, WARNING, ERROR, CRITICAL

#-------------------------------------------------

logging.info("Load CouchDB ...")
couch = jcCouch.jcCouchDB()

logging.info("Load Music Control ...")
thread_music_ctrl = music_ctrl.musicThread(2, "Thread Music", 1, couch) # jcJSON.read("music"))
thread_music_ctrl.start()

logging.info("Load Music Import Module ...")
thread_music_load = music_load.musicLoadingThread(3, "Thread Music Load", 1, couch) #  jcJSON.read("music"))
thread_music_load.start()

logging.info("Load WebStream Control ...")
thread_radio_ctrl = radio_ctrl.radioThread(4, "Thread Radio", 1, couch)  #  jcJSON.read("music"), jcJSON.read("radio"))
thread_radio_ctrl.start()

#-------------------------------------------------

def time_since_start():
    current_time = time.time()
    return (current_time - mbox.start_time)

#-------------------------------------------------

def ErrorMsg(code,info=""):
    if info != "": info = "(" + info + ")"

    message = mbox.error_messages

    if code in message:
      if int(code) >= 300:
        data = {}
        data["Code"]    = code
        data["Msg"]     = message[code]
        data["Info"]    = message[code] + " " + info
        return data

      else:
        return message[code]

    else:
        return "UNKNOWN ERROR CODE"

#---------------------------

def dataInit():
    d = { "API"          : {
              "name"     : "mBox",
              "version"  : mbox.APIversion,
              "stage"    : Stage,
              "rollout"  : stage.rollout
              },
	}
    return d


#-------------------------------------------------
# Server specific functions
#-------------------------------------------------

def readMusicData():
    global thread_music, thread_radio
    data               = {}
    data               = jcJSON.read("music")
    thread_music_ctrl.music_data  = data
    thread_radio_ctrl.music_data  = data
    thread_music_load.music_data  = data
    return data

def writeMusicData(data):
    global thread_music, thread_radio
    jcJSON.write("music",data)
    thread_music_ctrl.music_data  = data
    thread_radio_ctrl.music_data  = data
    thread_music_load.music_data  = data
    return

def reloadMusicData(all):
    data         = {}
    data         = readMusicData()
    data["data"] = music.reloadMusic(data["data"],all)

    writeMusicData(data)
    return data

#-------------------------------------------------

def readRadioData():
    global thread_music, thread_radio
    data                = {}
    data                = jcJSON.read("radio")
    thread_radio_ctrl.music_radio = data
    return data

def writeRadioData(data):
    global thread_music, thread_radio
    writeRadioData(data)
    thread_radio_ctrl.radio_data = data
    return

#-------------------------------------------------
# Device Status
#-------------------------------------------------

def deviceStatus():
    '''return control data from active device'''

    global thread_radio_ctrl, thread_music_ctrl

    if mbox.active_device == "radio":
      ctrl           = thread_radio_ctrl.music_ctrl
      ctrl["volume"] = thread_music_ctrl.music_ctrl["volume"]

    elif mbox.active_device == "music_box":
      ctrl           = thread_music_ctrl.music_ctrl
    else:
      ctrl           = thread_music_ctrl.music_ctrl
    return ctrl


def checkDevice():
    '''check which device is active (as rfid can change this in the background)'''

    global thread_radio_ctrl, thread_music_ctrl

    if   thread_music_ctrl.music_ctrl["playing"] != 0:  mbox.active_device = "music_box"
    elif thread_radio_ctrl.music_ctrl["playing"] != 0:  mbox.active_device = "radio"
    else:                                               mbox.active_device = ""

    logging.info("Check Device: Music ("+str(thread_music_ctrl.music_ctrl["playing"])+") Radio ("+str(thread_radio_ctrl.music_ctrl["playing"])+") - " + mbox.active_device)

    return mbox.active_device



#-------------------------------------------------
# Stop all threads (if pressed Ctrl+C)
#-------------------------------------------------

def end_all(n1,n2):

  global thread_radio_ctrl, thread_music_ctrl, thread_music_load

  logging.warn("Stop Application")

  thread_music_ctrl.stop()
  thread_radio_ctrl.stop_playback()
  thread_radio_ctrl.stop()
  thread_music_load.stop()

  raise RuntimeError("Server going down")



