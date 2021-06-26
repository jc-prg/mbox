import time
import logging
import os.path

import modules.config_stage      as stage
import modules.config_mbox       as mbox

import modules.jcCouchDB         as jcCouch

import modules.music_load        as music_load
import modules.music_podcast     as music_podcast
import modules.music_control     as music_ctrl
import modules.music_speak       as music_speak

from   modules.jcRunCmd          import *

#-------------------------------------------------
#
# server
# modules/server_cmd
# modules/server_init
# modules/server_read-json
# modules/jcCouch
# modules/jcJson
# modules/music_load
# modules/music_podcast
# modules/music_control
# modules/music_player
# modules/music_metadata
# modules/jcRunCmd
# modules/speakmsg
# modules_gpio/*
# modules_rfid/*
#
#-------------------------------------------------

Status     = "Starting"
ExitPrg    = False
Stage      = mbox.initial_stage

#-------------------------------------------------

if stage.test:
    if mbox.DEBUG: logging.basicConfig(level=logging.DEBUG)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    else:          logging.basicConfig(level=logging.INFO)   # DEBUG, INFO, WARNING, ERROR, CRITICAL
else:              logging.basicConfig(level=logging.WARN)   # DEBUG, INFO, WARNING, ERROR, CRITICAL

#-------------------------------------------------
# basic server functions
#-------------------------------------------------

def time_since_start():
    current_time = time.time()
    time_info    = int((current_time - mbox.start_time))
    return "  ("+ str(time_info) +"s)"

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
    
def speak_message(message):
   fname       = mbox.errormsg_dir + stage.language + "_" + message + ".mp3"
   fname_EN    = mbox.errormsg_dir + "EN_" + message + ".mp3"
   fname_UE    = mbox.errormsg_dir + stage.language + "_UNKNOWN-ERROR.mp3"
   fname_UE_EN = mbox.errormsg_dir + "EN_UNKNOWN-ERROR.mp3"
   
   if os.path.isfile(fname):       thread_music_ctrl.play_file(fname)
   elif os.path.isfile(fname_EN):  thread_music_ctrl.play_file(fname_EN)
   elif os.path.isfile(fname_UE):  thread_music_ctrl.play_file(fname_UE)
   else:                           thread_music_ctrl.play_file(fname_UE)

#-------------------------------------------------
# Load DB and threads for playback control
#-------------------------------------------------

logging.info("Load Speak Messages ..." + time_since_start())
thread_speak = music_speak.speakThread(4, "Thread Speak", 1, "")  #  jcJSON.read("music"), jcJSON.read("radio"))
thread_speak.start()
thread_speak.speak_message("STARTING")

logging.info("Load CouchDB ..." + time_since_start())
couch = jcCouch.jcCouchDB()

logging.info("Load Music Import Module ..." + time_since_start())
thread_music_load = music_load.musicLoadingThread(3, "Thread Music Load", 1, couch) #  jcJSON.read("music"))
thread_music_load.start()

logging.info("Load NEW Podcast Load ..." + time_since_start())
thread_podcast = music_podcast.podcastThread(6, "Thread Podcast", couch)
thread_podcast.start()

logging.info("Load NEW Playlist Control ..." + time_since_start())
thread_music_ctrl = music_ctrl.musicControlThread(5, "Thread Music Control", "music_box", couch, thread_podcast)
thread_music_ctrl.start()


#-------------------------------------------------
# Device Status
#-------------------------------------------------

def deviceStatus():
    '''
    return control data from active device
    '''
    ctrl = thread_music_ctrl.music_ctrl
    return ctrl


def checkDevice():
    '''
    check which device is active (as rfid can change this in the background)
    '''
    play_status   = str(thread_music_ctrl.music_plays)
    play_type     = thread_music_ctrl.music_ctrl["type"]
    play_position = str(thread_music_ctrl.music_list_p) + "/" + str(len(thread_music_ctrl.music_list))
    play_volume   = str(thread_music_ctrl.music_ctrl["volume"])

    logging.info("Check Device: Play=" + play_status + " / Type="+ play_type + " / Pos=" + play_position + " / Vol=" + play_volume)

    if play_type == "Stream":  mbox.active_device = "radio"
    else:                      mbox.active_device = "music_box"

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
  thread_music_ctrl.stop()
  thread_podcast.stop()

  raise RuntimeError("Server going down")



