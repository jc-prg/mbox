#-------------------------------------------
# Web stream playback control
#-------------------------------------------

import subprocess
import curses
import time
import threading
import logging
import requests
import vlc

import modules.config_stage as stage
import modules.config_mbox as mbox

#-------------------------------------------

logging.basicConfig(level=logging.INFO)

#-------------------------------------------

class radioThread (threading.Thread):
   '''class for radio player ...'''

   #--------------------------------------

   def __init__(self, threadID, name, counter, database):
      '''set initial values to vars and start radio'''

      threading.Thread.__init__(self)
      self.playlist_url = ""
      self.stopProcess  = False
      self.music_ctrl   = {}
      self.volume       = 50
      self.mute         = 0
      self.database     = database
      self.name         = name

      self.music_ctrl["device"]   = "radio"
      self.music_ctrl["mute"]     = self.mute
      self.music_ctrl["volume"]   = self.volume/100
      self.music_ctrl["playing"]  = 0
      self.music_ctrl["status"]   = "stop"
      self.music_ctrl["stream"]   = {}
      self.music_ctrl["channel_info"]    = ""

      self.instance     = vlc.Instance("--quiet")
      self.player       = self.instance.media_player_new()
      self.player.audio_set_volume(self.volume)
      self.player.audio_set_mute(False)

   def run(self):
      logging.info( "Starting " + self.name )

      while self.stopProcess == False:
         self.music_ctrl["volume"] = self.volume/100
         self.music_ctrl["mute"]   = self.mute
         #self.volume = self.music_ctrl["volume"]
         #self.mute   = self.music_ctrl["mute"]

         if (self.mute == 0):
           self.set_volume(self.volume)
         else:
           self.set_volume(0)
         self.load_if_rfid()
         #self.music_ctrl["channel_info"]  = self.current_play()
         time.sleep(2)

      logging.info( "Exiting " + self.name )

   def stop(self):
      self.stopProcess = True

   #--------------------------------------

   def load(self,playlist,pl_data,pl_uuid):
      if "m3u" in playlist:
        logging.info("Load playlist URL from m3u ("+playlist+")")
        streams = self.get_url(playlist).replace("\r","")
        logging.info("PL"+streams)
        streams = streams.split("\n")

        i=0
        for stream in streams:
          logging.info("... line: "+stream)
          if "#" in stream: 
            logging.info("... comment: "+stream)
            
          elif "http" in stream and i==0: 
            logging.info("... url: "+stream)
            self.playlist_url = stream
            i=1
            
      else:
        streams = [playlist]
        self.playlist_url = streams[0]
           
      self.music_ctrl["file"]           = playlist
      self.music_ctrl["stream"]         = pl_data
      self.music_ctrl["stream"]["uuid"] = pl_uuid

      #subprocess.Popen(["mpc", "clear"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      #subprocess.Popen(["mpc", "load", playlist], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      #self.playlist_name = self.current_play()

      logging.info("Load playlist ("+self.playlist_url+")")
      self.media = self.instance.media_new(self.playlist_url)
      self.player.set_media(self.media)
      self.player.play()
      self.playlist_name = playlist

   def play(self):
      logging.info("Start playback of playlist")
      self.music_ctrl["status"]   = "play"
      self.music_ctrl["playing"]  = 1
      self.player.play()

   def pause_playback(self):
      logging.info("(un)pause playback of playlist")
      if self.music_ctrl["status"]  == "pause":
        self.player.play()
        self.music_ctrl["playing"]  = 1
        self.music_ctrl["status"]   = "play"
      elif self.music_ctrl["status"] == "play":
        self.player.stop()
        self.music_ctrl["playing"]  = 1
        self.music_ctrl["status"]   = "pause"

   def stop_playback(self):
      logging.info("Stop playback of playlist")
      self.music_ctrl["status"]   = "stop"
      self.music_ctrl["playing"]  = 0
      self.player.stop()

   def current_play(self):
      logging.debug("Get infos from current playback")
      self.current = subprocess.check_output(["mpc", "current"])
      return self.current

   def set_volume(self,volume):
      logging.debug("Set stream volume to "+str(volume))
      #subprocess.Popen(["mpc", "volume", str(vol[0])], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      self.player.audio_set_volume(int(volume))

#------------------

   def get_url(self,url):
       #logging.info("Read URL: " + url)

       try:
           response = requests.get(url)
           data1    = response.text
       except requests.exceptions.RequestException as e:
           logging.debug("Error connecting to API: " + str(e))
           data1    = ""

       #logging.info(data1)
       return data1



#------------------

   def load_if_rfid(self):  ################### in progress #########################
      '''load list connected to rfid'''

      cardDB  = self.database.read_cache("cards")
      radioDB = self.database.read_cache("radio")

      if "cardUID" in mbox.rfid_ctrl:

        logging.info("**************** "+mbox.rfid_ctrl["cardUID"]+"**"+str(self.music_ctrl["playing"]))

        # check if card detected ...
        if (mbox.rfid_ctrl["cardUID"] != ""):
          logging.debug("CardUID: "+mbox.rfid_ctrl["cardUID"]+" ... check if radio connected")

          # check if radio connected to card
          if (mbox.rfid_ctrl["cardUID"] in cardDB and "r_" in cardDB[mbox.rfid_ctrl["cardUID"]][0]):
            channelID = cardDB[mbox.rfid_ctrl["cardUID"]][0]
            if ("LastCard" not in self.music_ctrl or self.music_ctrl["LastCard"] != channelID or str(self.music_ctrl["playing"]) == 0):
              logging.info("Start Radio: "+channelID)#.encode('utf-8'))
              self.load( radioDB[channelID]["stream_url"], radioDB[channelID], channelID)
              self.play()
              self.music_ctrl["LastCard"]       = channelID
              self.music_ctrl["playlist_uuid"]  = channelID
            else:
              logging.debug("Radio: +++++++++++++")

          # else stop playing
          else:
            logging.debug("No Radio connected.")
            self.music_ctrl["LastCard"]       = ""
            self.music_ctrl["playlist_uuid"]  = ""
            self.stop_playback()


   #--------------------------------------

   # subprocess.Popen(["mpc", "prev", "-q"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   # subprocess.Popen(["mpc", "next", "-q"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)



def test_radio():
  '''Start stream for 5 seconds and test playback'''

  thread1 = radioThread(1, "Thread Web Radio", 1)
  thread1.start()
  thread1.load("http://streams.br.de/bayern3_2.m3u")
  thread1.set_volume(0.5)
  thread1.play()

  print("Test RADIO Stream:")
  print(thread1.current_play())

  time.sleep(5)

  thread1.stop()

#test_radio()

