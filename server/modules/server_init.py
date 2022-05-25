import time
import logging
import os.path

import modules.config_stage as stage
import modules.config_mbox as mbox

import modules.jcCouchDB as jcCouch

import modules.music_load as music_load
import modules.music_control as music_ctrl
import modules.music_vlc as music_vlc
import modules.music_speak as music_speak
import modules.music_player as music_player
import modules.music_podcast as music_podcast

from modules.jcRunCmd import *

# -------------------------------------------------
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
# -------------------------------------------------

Status = "Starting"
ExitPrg = False
Stage = mbox.initial_stage


# -------------------------------------------------
# basic server functions
# -------------------------------------------------

def time_since_start():
    current_time = time.time()
    time_info = int((current_time - mbox.start_time)*100)/100
    return "  (" + str(time_info) + "s)"


# -------------------------------------------------

def ErrorMsg(code, info=""):
    if info != "": info = "(" + info + ")"

    message = mbox.error_messages

    if code in message:
        if int(code) >= 300:
            data = {"Code": code, "Msg": message[code], "Info": message[code] + " " + info}
            return data
        else:
            return message[code]
    else:
        return "UNKNOWN ERROR CODE"


# ---------------------------

def dataInit():
    d = {"API": {
        "name": "mBox",
        "version": mbox.APIversion,
        "stage": Stage,
        "rollout": stage.rollout
    },
    }
    return d


# -------------------------------------------------
# Load DB and threads for playback control
# -------------------------------------------------

logging.info("Load Modules ..." + time_since_start())

thread_vlc = music_vlc.VlcThread(time_since_start())
thread_vlc.start()

thread_speak = music_speak.SpeakThread(thread_vlc, time_since_start())
thread_speak.start()
thread_speak.speak_message("STARTING")

thread_player = music_player.MusicPlayer(thread_vlc, thread_speak, time_since_start())
thread_player.start()

thread_couch = jcCouch.jcCouchDB(stage.data_db, thread_speak, time_since_start())

thread_podcast = music_podcast.PodcastThread(thread_couch, thread_speak, time_since_start())
thread_podcast.start()

thread_music_load = music_load.MusicLoadingThread(thread_couch, time_since_start())
thread_music_load.start()

thread_music_ctrl = music_ctrl.MusicControlThread("music_box", thread_couch, thread_player, thread_speak, thread_podcast, time_since_start())
thread_music_ctrl.start()

# -------------------------------------------------
# Device Status
# -------------------------------------------------

def deviceStatus():
    """
    return control data from active device
    """
    ctrl = thread_music_ctrl.music_ctrl
    return ctrl


def end_all(n1, n2):
    """
    Stop all threads (if pressed Ctrl+C)
    """
    global thread_radio_ctrl, thread_music_ctrl, thread_music_load

    logging.warning("Stop Application")

    thread_vlc.stop()
    thread_speak.stop()
    thread_player.stop()

    thread_music_load.stop()
    thread_music_ctrl.stop()
    thread_podcast.stop()

    raise RuntimeError("Server going down")
