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
import gtts

import modules.config_stage as stage
import modules.config_mbox  as mbox


from modules.config_mbox import *
from decimal             import *

# ------------------------
# THREADING CLASS

class speakThread (threading.Thread):

   def __init__(self, threadID, name, counter, database):
      '''set initial values to vars and start pygame.mixer'''

      # init thread
      threading.Thread.__init__(self)
      self.threadID       = threadID
      self.name           = name
      self.counter        = counter
      self.stopProcess    = False
      self.default_volume = 70;
      
      if stage.rollout == "prod":     self.instance     = vlc.Instance("--quiet")
      else:                           self.instance     = vlc.Instance()
            
      self.player       = self.instance.media_player_new()

      # init mixer
      #global music_plays, music_loaded, music_ctrl

   def play_file(self, filename):
      self.media = self.instance.media_new( filename ) #str(file.encode('utf-8')) )
      self.player.set_media(self.media)
      self.player.play()
      
      time.sleep(2)
      
      state = ""
      while state == "State.Playing":
        state = self.player.get_state()
        if state != "State.Ended" and state != "State.Playing": 
          return "Error"
        
      return "Ended"
      
      
   def speak_text(self, text):
      '''
      Use google API to speech from text
      '''
      filename = "/tmp/music-box-speech.mp3"
      language = stage.language.lower()
      try:
         tts = gtts.gTTS(text, lang=language)
         tts.save(filename)
         self.play_file(filename)
         duration = self.player.get_length() / 1000
         time.sleep(duration)
               
      except Exception as e:
         logging.error("Could not speak message ("+text+").")
         logging.error(" -> gtts error: "+str(e))

      logging.info("Speak_text: "+text+" ("+str(duration)+")")
    

    
   def speak_message(self, message):
      '''
      play spoken messages from prerecorded files
      '''
      
      self.player.audio_set_volume(self.default_volume)
      self.player.audio_set_mute(False)

      if stage.speak_msg != "yes": return
   
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

      #time.sleep(1.5)
      duration = self.player.get_length() / 1000
      time.sleep(duration)

