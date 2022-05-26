import time
import logging
import modules.config_stage as stage
import modules.config_mbox as mbox

import modules.couch_db as couch_db
import modules.music_load as music_load
import modules.music_control as music_ctrl
import modules.music_vlc as music_vlc
import modules.music_speak as music_speak
import modules.music_player as music_player
import modules.music_podcast as music_podcast

from modules.jcRunCmd import *


Status = "Starting"
ExitPrg = False
Stage = mbox.initial_stage

thread_vlc = None
thread_speak = None
thread_player = None
thread_couch = None
thread_podcast = None
thread_music_load = None
thread_music_ctrl = None


def time_since_start():
    current_time = time.time()
    time_info = int((current_time - mbox.start_time)*100)/100
    return "  (" + str(time_info) + "s)"


def start_modules():
    """
    load modules as threads
    """
    global thread_vlc, thread_speak, thread_player, thread_couch, thread_podcast, thread_music_load, thread_music_ctrl
    logging.info("Load Modules ..." + time_since_start())

    thread_vlc = music_vlc.VlcThread(time_since_start())
    thread_vlc.start()

    thread_speak = music_speak.SpeakThread(thread_vlc, time_since_start())
    thread_speak.start()
    thread_speak.speak_message("STARTING")

    thread_player = music_player.MusicPlayer(thread_vlc, thread_speak, time_since_start())
    thread_player.start()

    thread_couch = couch_db.CouchDB(stage.data_db, thread_speak, time_since_start())

    thread_podcast = music_podcast.PodcastThread(thread_couch, thread_speak, time_since_start())
    thread_podcast.start()

    thread_music_load = music_load.MusicLoadingThread(thread_couch, time_since_start())
    thread_music_load.start()

    thread_music_ctrl = music_ctrl.MusicControlThread("music_box", thread_couch, thread_player, thread_speak, thread_podcast, time_since_start())
    thread_music_ctrl.start()


def end_modules():
    """
    Stop all threads (if pressed Ctrl+C)
    """
    logging.warning("Stop Application")

    thread_vlc.stop()
    thread_speak.stop()
    thread_player.stop()

    thread_music_load.stop()
    thread_music_ctrl.stop()
    thread_podcast.stop()

    raise RuntimeError("Server going down")
