import time
import logging
import os.path

import modules.config_stage   as stage
import modules.config_mbox    as mbox
import modules.jcCouchDB      as jcCouch
import modules.music_load     as music_load
import modules.music_control  as music_ctrl
import modules.stream_control as radio_ctrl
import modules.speekmsg       as speek

from modules.runcmd         import *

#-------------------------------------------------

Status     = "Starting"
ExitPrg    = False
Stage      = mbox.initial_stage

#-------------------------------------------------

if stage.test:
    if mbox.DEBUG: logging.basicConfig(level=logging.DEBUG)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    else:          logging.basicConfig(level=logging.INFO)   # DEBUG, INFO, WARNING, ERROR, CRITICAL
else:              logging.basicConfig(level=logging.WARN)    # DEBUG, INFO, WARNING, ERROR, CRITICAL

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
    
def speek_message(message):
   fname       = mbox.errormsg_dir + stage.language + "_" + message + ".mp3"
   fname_EN    = mbox.errormsg_dir + "EN_" + message + ".mp3"
   fname_UE    = mbox.errormsg_dir + stage.language + "_UNKNOWN-ERROR.mp3"
   fname_UE_EN = mbox.errormsg_dir + "EN_UNKNOWN-ERROR.mp3"
   
   if os.path.isfile(fname):
     thread_music_ctrl.play_file(fname)
   elif os.path.isfile(fname_EN):
     thread_music_ctrl.play_file(fname_EN)
   elif os.path.isfile(fname_UE):
     thread_music_ctrl.play_file(fname_UE)
   else:
     thread_music_ctrl.play_file(fname_UE)

#-------------------------------------------------
# Load DB and threads for playback control
#-------------------------------------------------

logging.info("Load Speek Messages ..." + time_since_start())
thread_speek = speek.speekThread(4, "Thread Radio", 1, "")  #  jcJSON.read("music"), jcJSON.read("radio"))
thread_speek.start()
thread_speek.speek_message("STARTING")

logging.info("Load CouchDB ..." + time_since_start())
couch = jcCouch.jcCouchDB()

logging.info("Load Music Control ..." + time_since_start())
thread_music_ctrl = music_ctrl.musicThread(2, "Thread Music", 1, couch) # jcJSON.read("music"))
thread_music_ctrl.start()

logging.info("Load Music Import Module ..." + time_since_start())
thread_music_load = music_load.musicLoadingThread(3, "Thread Music Load", 1, couch) #  jcJSON.read("music"))
thread_music_load.start()

logging.info("Load WebStream Control ..." + time_since_start())
thread_radio_ctrl = radio_ctrl.radioThread(4, "Thread Radio", 1, couch)  #  jcJSON.read("music"), jcJSON.read("radio"))
thread_radio_ctrl.start()



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



