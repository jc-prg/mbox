import os
# ------------------------
# control music playback
# ------------------------

import threading
import time
import operator
import logging
import vlc
import os.path

import modules.config_stage as stage
import modules.config_mbox  as mbox


from modules.config_mbox import *
from decimal             import *

# ------------------------
# THREADING CLASS

class speekThread (threading.Thread):

   def __init__(self, threadID, name, counter, database):
      '''set initial values to vars and start pygame.mixer'''

      # init thread
      threading.Thread.__init__(self)
      self.threadID     = threadID
      self.name         = name
      self.counter      = counter
      self.stopProcess  = False
      
      if stage.rollout == "prod":     self.instance     = vlc.Instance("--quiet")
      else:                           self.instance     = vlc.Instance()
            
      self.player       = self.instance.media_player_new()
      self.player.audio_set_volume(80)
      self.player.audio_set_mute(False)

      # init mixer
      #global music_plays, music_loaded, music_ctrl

   def play_file(self, filename):
      file = filename
      self.player.audio_set_volume(99)
      self.media = self.instance.media_new( file ) #str(file.encode('utf-8')) )
      self.player.set_media(self.media)
      self.player.play()
      
      time.sleep(2)
      
      state = ""
      while state == "State.Playing":
        state = self.player.get_state()
        if state != "State.Ended" and state != "State.Playing": 
          return "Error"
        
      return "Ended"

    
   def speek_message(self, message):

      if stage.speek_msg != "yes": return
   
      fname       = mbox.errormsg_dir + stage.language + "_" + message + ".mp3"
      fname_EN    = mbox.errormsg_dir + "EN_" + message + ".mp3"
      fname_UE    = mbox.errormsg_dir + stage.language + "_UNKNOWN-ERROR.mp3"
      fname_UE_EN = mbox.errormsg_dir + "EN_UNKNOWN-ERROR.mp3"
   
      if os.path.isfile(fname):
        self.play_file(fname)
      elif os.path.isfile(fname_EN):
        self.play_file(fname_EN)
      elif os.path.isfile(fname_UE):
        self.play_file(fname_UE)
      else:
        self.play_file(fname_UE)


