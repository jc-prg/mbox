# ------------------------
# control music playback
# ------------------------

import threading
import time, os
import logging
import vlc
import requests
import urllib.request

from xml.etree import cElementTree as ET

import modules.jcRunCmd      as runcmd
import modules.config_stage  as stage
import modules.config_mbox   as mbox
import modules.music_speak   as speak

from decimal               import *

# ------------------------

class musicPlayer(threading.Thread):

   def __init__(self, threadID, name):
      '''
      create VLC player
      '''
      threading.Thread.__init__(self)
      self.threadID      = threadID
      self.name          = name + " VLC-Player"
      self.running       = True

      self.connected     = False
      self.internet      = False
      self.player        = ""
      self.play_uuid     = ""
      self.play_url      = ""
      self.play_status   = 0
      self.play_position = 0
      self.player_status = ""
      self.volume_factor = 1         # default factor to limit audio level (max = 1.0)
      self.volume_start  = 0.4       # initial volume
      self.volume        = self.volume_start
      self.volume_mute   = False
      
      self.speak          = speak.speakThread(4, name + " VLC Player / Speak", 1, "") 
      self.speak.start()

      
   def run(self):
      '''
      run player
      '''
      logging.info("Starting VLC player ("+self.name+") ...")
      try:
        logging.info("Connecting to audio device via VLC ...")
        if stage.rollout == "prod":     self.instance     = vlc.Instance("--quiet")
        else:                           self.instance     = vlc.Instance()
      
        self.connected    = True
        self.player       = self.instance.media_player_new()
        self.set_volume(self.volume)
#        self.player.audio_set_mute(self.volume_mute)
        
      except Exception as e:
        self.connected    = False
        logging.error("VLC-error connecting to audio device: "+str(e))

      while self.running:
         time.sleep(0.5)
         self.play_status = self.playing()

      logging.info("Stopped VLC player ("+self.name+").")
      return
      
      
   def set_volume(self,vol):
      '''
      set volume
      '''
      if self.player != "":
        self.player.audio_set_volume(int(vol * self.volume_factor * 100))
        self.volume_mute   = False
        self.volume        = vol
      else:
        logging.warning("Player not loaded yet")


   def volume_up(self,up):
      '''
      set volume - step up or down
      '''
      vol = float(self.volume)
      if (up == "up" and vol < 100):                         vol = vol + 0.05
      elif (up == "down" and vol > 0):                       vol = vol - 0.05
      elif (isinstance(up, int) and up >= 0 and up <= 100):  vol = up / 100

      self.set_volume(vol)
      self.volume_mute   = False
      self.volume        = vol


   def pause(self):
      '''
      pause / unpause running song
      '''
      if (self.player_status == "State.Playing"):
          self.player.pause()
          self.play_status = 0

      if (self.player_status == "State.Paused"):
          self.player.play()
          self.play_status = 1
          
          
   def set_position(self,percentage):
      '''
      set position in current stream or file
      '''
      percentage = float(percentage)   
      if percentage >= 0 and percentage <= 100:
          self.player.set_position(percentage/100)
      
      
   def get_position(self):
      '''
      get position in current playing or pause file -> 1000 / seconds
      '''
      if self.player_status == "State.Playing" or self.player_status == "State.Paused": 
         position = float(self.player.get_time()) 
      else:
         position = 0
      return position

   
   def get_length(self):
      '''
      get length of current playing or pause file ->  1000 / seconds
      '''
      if self.player_status == "State.Playing" or self.player_status == "State.Paused": 
         length = float(self.player.get_length())
      else:
         length = 0
      return length


   def stop(self):
      '''
      stop playback
      '''
      self.player.stop()
      self.play_status = 0

      
   def mute(self,value=""):
      '''
      mute / unmute player
      '''
      if self.volume_mute == 0 or value == True:
          self.volume_mute = 1
          self.set_volume(0)
      else:
          self.volume_mute = 0
          self.set_volume(self.volume)

      
   def play_file(self,path):
      '''
      play audio file, react on position var
      '''
      self.player.stop()
      
      if not os.path.exists( path ) and not path.startswith("http"):
         self.speak.speak_message("FILE-NOT-FOUND")
         return "Error"

      self.media = self.instance.media_new( path ) #str(file.encode('utf-8')) )
      try:
        self.player.set_media(self.media)
        self.player.play()
        self.play_url = path
        
      except Exception as e:
        logging.error("Player ("+self.name+"): Could not start playback - "+path+" - "+str(e))
        self.speak.speak_message("COULD-NOT-START-PLAYBACK")
        return "Error"
      
      time.sleep(2)
      if self.play_status == 0:
         logging.error("Player ("+self.name+"): Could not start playback - " + str(self.play_status))
         self.speak.speak_message("UNKNOWN-ERROR")
         return "Error"

      return "Play"

            
   def play_stream(self,url):
      '''
      play audio stream, react on position var
      '''
      if not self.internet_connection():
         return "Error"
         
      if url.endswith(".m3u"):
         url = self.get_stream_m3u(url)
         return self.play_file(url)
         
      elif url.endswith(".mp3"):
         return self.play_file(url)
         
      else:
         return "not implemented yet"


   def playing(self):
      '''
      translate playback status to 0/1
      '''
      old_state             = self.player_status
      self.player_status    = str(self.player.get_state())
        
      if self.player_status == "State.Stopped" or self.player_status == "State.NothingSpecial":
         self.play_status = 0
         logging.debug("Playing:"+self.play_url+"..."+str(self.play_status))
      else:
         self.play_status = 1

      logging.debug("Playing:"+old_state+" -> "+self.player_status+" ("+str(self.play_status)+")")        
      return self.play_status
      
      
   def get_stream_m3u(self, url):
      '''
      get mp3 file from url with m3u
      '''
      logging.info("Load playlist URL from m3u ("+url+")")

      try:
        response = requests.get(url)
        playlist = response.text
      except requests.exceptions.RequestException as e:
        logging.debug("Can't open the playlist from m3u: " + str(e))
        self.speak.speak_message("CANT-OPEN-STREAM")
        return ""
        
      streams = playlist.replace("\r","")
      streams = streams.split("\n")
      return_url = ""

      i=0
      for stream in streams:
        logging.info("... line: "+stream)
        if "#" in stream: 
           logging.info("... comment: "+stream)

        elif "http" in stream and i==0: 
           logging.info("... url: "+stream)
           return_url = stream
           i=1

      if return_url == "":
        logging.debug("No URL found in m3u-file:"+url)
        self.speak.speak_message("CANT-OPEN-STREAM")
        
      return return_url
      
      
   def internet_connection(self):
      '''
      check if connection to internet exists
      '''
      host_ip   = stage.server_dns
      host      = ['spiegel.de','google.com']
      ping_ip   = False
      error_msg = ""

      logging.debug("check if internet is connected - ping dns server")
      for key in host_ip:
        if runcmd.ping(key):
          ping_ip = True
          break

      logging.debug("check if dns is working correctly - ping domain names")
      count     = 0
      while count < len(host):
         try:
            connect = runcmd.ping(host[count])
            if connect and ping_ip:
                error_msg = "CONNECTED"
                self.internet_connection_error(error_msg)
                logging.warning("Internet connection OK: " + host[count])
                return error_msg

            elif ping_ip:
                error_msg = "DNS-ERROR"
                self.internet_connection_error(error_msg)
                logging.warning("Connection OK, DNS for Domain doesnt work: "+host[count])

            else:
                error_msg = "NO-CONNECTION"
                self.internet_connection_error(error_msg)
                logging.warning("Internet connection ERROR: " + host[count])

         except requests.exceptions.RequestException as e:
            error_msg = "NO-CONNECTION"
            logging.warning("Error connecting to INTERNET ("+host[count]+"): " + str(e))

         count = count + 1
      
      if error_msg == "DNS-ERROR":
          logging.error("Could not connect to INTERNET!")
          self.speak.speak_message("CONNECTION-ERROR-RESTART-SHORTLY")
          time.sleep(20)
          return False
          
      elif error_msg != "CONNECTED":
          logging.error("Could not connect to INTERNET!")
          self.speak.speak_message("NO-INTERNET-CONNECTION")
          time.sleep(0.5)
          self.speak.speak_message("TRY-AGAIN-IN-A-MINUTE")
          time.sleep(20)
          self.music_ctrl["LastCard"] = ""
          return False
          
      return True


   def internet_connection_error(self,info):
      '''
      write error message to log file
      '''
      f = open("/log/internet_connect", "w+")
      f.write(info)
      f.close()

