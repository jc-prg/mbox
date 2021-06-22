# ------------------------
# control music playback
# ------------------------

import threading
import time, os
import operator
import logging
import vlc
import requests
import urllib.request

from xml.etree import cElementTree as ET
from pprint import pprint

import modules.jcJson       as jcJSON
import modules.jcCouchDB    as jcCouch
import modules.config_stage as stage
import modules.config_mbox  as mbox
import modules.speakmsg     as speak
import modules.runcmd       as runcmd

from modules.music_podcast import *
from modules.config_mbox   import *
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
      self.play_uuid     = ""
      self.play_url      = ""
      self.play_status   = 0
      self.play_position = 0
      self.player_status = ""
      self.volume_factor = 0.8       # default factor to limit audio level (max = 1.0)
      self.volume_start  = 0.4       # initial volume
      self.volume        = self.volume_start
      self.volume_mute   = False
      
      self.speak          = speak.speakThread(4, name + " VLC Player / Speak", 1, "")  #  jcJSON.read("music"), jcJSON.read("radio"))
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
        self.player.audio_set_volume(int(self.volume*100))
        self.player.audio_set_mute(self.volume_mute)
        
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
      self.player.audio_set_volume(int(vol * self.volume_factor * 100))
      self.volume_mute   = False
      self.volume        = vol


   def volume_up(self,up):
      '''
      set volume - step up or down
      '''
      vol = float(self.volume)
      if (up == "up" and vol < 100):                         vol = vol + 0.05
      elif (up == "down" and vol > 0):                       vol = vol - 0.05
      elif (isinstance(up, int) and up >= 0 and up <= 100):  vol = up / 100

      self.player.audio_set_volume(int(vol * self.volume_factor * 100))
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
      get position in current playing or pause file
      '''
      if self.player_status == "State.Playing" or self.player_status == "State.Paused": 
         position = float(self.player.get_time()) / 1000
      else:
         position = 0
      return position

   
   def get_length(self):
      '''
      get length of current playing or pause file
      '''
      if self.player_status == "State.Playing" or self.player_status == "State.Paused": 
         length = float(self.player.get_length()) / 1000
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
          self.player.audio_set_volume(0)
      else:
          self.volume_mute = 0
          self.player.audio_set_volume(int(self.volume*self.volume_factor*100))

      
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

            
# ------------------------

      
class musicControlThread(threading.Thread):

   def __init__(self, threadID, name, device, database, podcast):
      '''
      set initial values to vars and start VLC
      '''
      threading.Thread.__init__(self)
      self.threadID      = threadID
      self.name          = name
      self.running       = True

      self.music_list      = []
      self.music_list_p    = 1
      self.music_list_uuid = ""
      self.music_database  = database
      self.music_loaded    = -1
      self.music_plays     = -1
      self.music_dir       = mbox.music_dir
      self.music_device    = device
      self.music_load_new  = False
      self.music_ctrl      = {}
      self.music_ctrl      = self.control_data(state="Started")
      self.music_type      = ""
      self.music_podcast   = podcast
      
      self.relevant_db     = self.music_database.databases["music"]
      self.speak           = speak.speakThread(4, name + " / Speak", 1, "")  #  jcJSON.read("music"), jcJSON.read("radio"))
      self.speak.start()

      
   def run(self):
      '''
      loop: check if track in playlist, stream ... and play status
      '''
      wait_time = 0.1
      last_load = False  
      last_run  = self.music_database.read("status")

      logging.info("Starting music player ("+self.name+") ...")
      self.player = musicPlayer(self.threadID, self.name)
      self.player.start()

      if self.player.connected and "_device" in last_run and last_run["_device"] == "music" and last_run["music"]["playing"] == 1:
        logging.info("Load playlist and song from last run ...")
        last_load           = True
        last_music          = last_run["music"]
        self.music_ctrl     = last_music
        self.music_loaded   = 1      
        if "playlist_files" in last_music:
          self.music_list     = last_music["playlist_files"]
          self.music_list_p   = last_music["playlist_pos"]
          self.music_load_new = True

      time.sleep(4)
      while self.running:     

         time.sleep(wait_time)         
         if not self.player.connected:
            logging.error("Player not connected!")
            self.running = False
            break

         self.playlist_load_rfid()
         self.playback_save_status()
         self.music_plays = self.player.playing()       
         
         logging.debug("Active playlist: " + str(self.music_load_new) + "; List: " + str(len(self.music_list)) + "; Position: " + str(self.music_list_p) )
         if self.music_load_new and len(self.music_list) > 0 and int(self.music_list_p) <= len(self.music_list):
         
            self.music_load_new  = False
            current_path         = self.music_list[int(self.music_list_p)-1]
            current_list         = self.playlist_info()
            
            if not self.music_list_uuid.startswith("r_"):
               current_info         = self.metadata_by_filename(current_path)
               current_info["info"] = "Title loaded"
               
            else:
               database                  = self.music_database.read_cache("radio")
               current_stream            = database[self.music_list_uuid]
               current_stream["podcast"] = self.music_podcast.get_podcasts(self.music_list_uuid)
               
               if current_stream["podcast"] != {}:
                  current_info         = current_stream["podcast"]
                  current_list["list"] = []
                  for filename in current_list["files"]:
                     track_uuid = current_info["track_url"][filename]
                     track_info = current_info["tracks"][track_uuid]
                     current_list["list"].append(track_info)
                  current_uuid         = current_info["track_url"][current_path]
                  current_info         = current_info["tracks"][current_uuid]
                  current_info["uuid"] = current_uuid
                  current_info["info"] = "Title loaded"
                  
                  #self.speak.speak_text(current_info["title"])
                  
               else:
                  current_info    = {
                     "file"    : current_path,
                     "stream"  : current_stream
                     }
                  current_info["stream"]["uuid"] = self.music_list_uuid
               
                        
            if current_path.startswith("http"): 
               self.player.stop()
               self.speak.speak_text(current_info["title"])
               self.player.play_stream(current_path)
            else:                               
               self.player.stop()
               self.player.play_file(mbox.music_dir + current_path)
            
            if last_load:
               logging.debug("Jump to position in song from last run ...")
               position  = (self.music_ctrl["position"] / self.music_ctrl["length"]) * 100
               self.set_position()
               last_load = False

            if self.player.play_status == 1: self.music_ctrl = self.control_data(state="play",  song=current_info, playlist=current_list)
            else:                            self.music_ctrl = self.control_data(state="error", song={}, playlist=current_list)
            

         if not self.music_load_new and self.player.playing == 1:
         
            self.music_ctrl["length"]    = float(self.player.get_length())   / 1000
            self.music_ctrl["position"]  = float(self.player.get_position()) / 1000
         
            if self.music_ctrl["state"] == "State.Ended":
            
               if self.music_list_p < len(self.music_list):
                 self.music_load_new = True
                 self.music_list_p   = int(self.music_list_p)+1
                 logging.info("Next song in list, position: " + str(self.music_list_p) + "/" + str(len(self.music_list)))

               else:
                 self.music_load_new = True
                 self.music_list     = []
                 self.music_list_p   = 1
                 self.music_type     = ""
                 logging.info("Playlist empty, stop playing.")

      logging.info("Stopped music player ("+self.name+").")     
      

   def stop(self):
      '''
      Stop music control
      '''
      self.player.stop()
      self.player.running = False
      self.running        = False


   def volume(self,vol):
      '''
      player volume
      '''
      self.player.set_volume(vol)
      self.music_ctrl["volume"] = self.player.volume


   def volume_up(self,up):
      '''
      player volume
      '''
      self.player.volume_up(up)
      self.music_ctrl["volume"] = self.player.volume


   def playlist_info(self):
      '''
      prepare playlist info based on loaded playlist
      ''' 
      current_list = {}
      current_list["uuid"]       = ""
      current_list["position"]   = self.music_list_p
      current_list["length"]     = len(self.music_list)
      current_list["files"]      = self.music_list
      current_list["list"]       = []
      for filename in self.music_list:
        file_info = self.metadata_by_filename(filename)
        current_list["list"].append(file_info)
      return current_list


   def playlist_load_uuid(self, playlist_uuid, position=1):
      '''
      load list from album, playlist or stream -> put to playlist array
      '''
      self.music_list      = []
      self.music_list_p    = int(position)
      self.music_load_new  = True
      self.music_list_uuid = playlist_uuid

      if playlist_uuid.startswith("a_"):   self.music_type   = "Album"
      elif playlist_uuid.startswith("p_"): self.music_type   = "Playlist"
      elif playlist_uuid.startswith("t_"): self.music_type   = "Track"
      elif playlist_uuid.startswith("r_"): self.music_type   = "Stream"
      else:                                self.music_type   = ""
      
      if self.music_type == "Stream":      self.music_device = "radio"
      else:                                self.music_device = "music_box"

      if self.music_device == "music_box":
         track_list           = self.playlist_by_uuid(playlist_uuid)
         track_db             = self.music_database.read_cache("tracks")
      else:
         podcast              = self.music_podcast.get_podcasts(playlist_uuid)
         if "track_list" in podcast:
           track_list           = podcast["track_list"]
           track_db             = podcast["tracks"]
           if len(track_list) > 0:
             self.music_type   = "Podcast"
      
      for track in track_list:
        if track in track_db and "file" in track_db[track]:
           self.music_list.append(track_db[track]["file"])
        if track.startswith("http"):
           self.music_list.append(track)
                   

            
   def playlist_load_rfid(self):
      '''
      check rfid card value and load connected playlist -> put to playlist array
      '''
      if "cardUID" in mbox.rfid_ctrl:
      
        logging.debug("Load UUID from RFID-Card: " + mbox.rfid_ctrl["cardUID"])
        database = self.music_database.read_cache("cards")

        if (mbox.rfid_ctrl["cardUID"] != ""):

          logging.info("CardUID: "+mbox.rfid_ctrl["cardUID"])
          if mbox.rfid_ctrl["cardUID"] in database:            

            if "LastCard" not in self.music_ctrl or self.music_ctrl["LastCard"] != database[mbox.rfid_ctrl["cardUID"]][0]:
              logging.info("Start Playlist: "+database[mbox.rfid_ctrl["cardUID"]][0])
              self.playlist_load_uuid(database[mbox.rfid_ctrl["cardUID"]][0])
              self.music_ctrl["LastCard"]  = database[mbox.rfid_ctrl["cardUID"]][0]
              
            else:
              logging.info("Card already started ...")

          else:
            self.player.stop()
            self.music_ctrl["LastCard"]       = ""
            self.control_data(state="error")

            if mbox.rfid_ctrl["cardUID"] != self.last_card_identified:
              logging.info("No Entry connected.")
              self.last_card_identified = mbox.rfid_ctrl["cardUID"]
          
              if mbox.rfid_ctrl["cardUID"] not in cardDB: 
                 self.speak.speak_message("NO-MUSIC-CONNECTED-TO-CARD")
                 
   def playlist_next(self,stop):
      '''
      jump within the playlist
      '''
      logging.debug("Next song: "+str(step)+"+"+str(self.music_list_p)+" ("+str(len(self.music_list))+")" )

      # back // if position > 0
      if step < 0 and self.music_list_p + step > 0:
        self.player.stop()
        self.music_list_p        = self.music_list_p + step       # set new position in playlist
        self.music_load_new      = True
        return "done"

      # forward // if position < length of list
      elif step > 0 and self.music_list_p + step <= len(self.music_list):
        self.player.stop()
        self.music_list_p        = self.music_list_p + step       # set new position in playlist
        self.music_load_new      = True
        return "done"

      # stop playing if beginning or end ...
      else:
        self.player.stop()
        self.music_list_p        = 0                              # set new position in playlist
        self.music_load_new      = False

      return "not found"

      
   def playback_save_status(self):
      '''
      write current playlist, track and position to config
      '''
      data  = self.music_database.read("status")    
      if not "_saved" in data or data["_saved"] + 3 < time.time():
        data["music"]  = self.music_ctrl
        data["_saved"] = time.time()
        if self.music_ctrl["state"] == "State.Playing" or self.music_ctrl["state"] == "State.Paused": 
           data["_device"] = "music"
        self.music_database.write("status",data)

      
   def metadata_by_filename(self,filename):
      '''
      return metadata from db by filename
      '''
      database = self.music_database.read_cache("files")
      filename = filename.replace(mbox.music_dir, "")
      if not filename in database:
         logging.error("Filename not in DB ("+filename+").")
         return {}
      else:
         return database[filename]

      
   def metadata_by_uuid(self,get_uuid):
      '''
      return metadata from db by filename
      '''
      database = self.music_database.read_cache("tracks")
      if not get_uuid.startswith("t_"):
         logging.error("It's not a track.")
         return {}
      elif not get_uuid in database:
         logging.error("Track not found in DB.")
         return {}
      else:
         return database[get_uuid]

      
   def playlist_by_uuid(self,get_uuid):
      '''
      return tracks from db by uuid
      '''
      track_list = []      
      if get_uuid.startswith("t_"):
         track_list = [ get_uuid ]
         
      elif get_uuid.startswith("a_"):
         database = self.music_database.read_cache("album_info")
         if get_uuid in database: 
            track_list = database[get_uuid]["tracks"]
         else: 
            logging.error("Album not found: "+get_uuid)
            track_list = []
         
      elif get_uuid.startswith("p_"):
         database_p = self.music_database.read_cache("playlists")
         database_a = self.music_database.read_cache("album_info")
         if get_uuid in database_p: 
            tracks     = database_p[get_uuid]["tracks"]
            track_list = []
            for track in tracks:
               if track.startswith("t_"):                            track_list.append(track)
               elif track.startswith("a_") and track in database_a:  track_list.extend(database_a[track]["tracks"])
         else:
            logging.error("Album / track not found: "+get_uuid)
            track_list = []
      
      elif get_uuid.startswith("r_"):         
         database = self.music_database.read_cache("radio")        
         if get_uuid in database: 
            stream_url = database[get_uuid]["stream_url"]
                      
            if stream_url.endswith(".m3u"):   track_list = [ stream_url ]
            elif stream_url.endswith(".mp3"): track_list = [ stream_url ]
            elif stream_url.endswith(".rss"): 
            
               get_tracks_rss(rss_url=stream_url, playlist_uuid=get_uuid)
               
               logging.warning("RSS Feed / Podcast-List not implemented yet!")
               track_list = []
            else: 
               logging.warning("Unknown URL format. Try out ...")
               track_list = [ stream_url ]

      else:
         logging.error("Unknown ID Type!")
      
      return track_list
            
      
   def control_data(self,state,song={},playlist={}):
      '''
      set and return control data
      '''
      if state != "Started":
        if "LastCard" in self.music_ctrl: last_card = self.music_ctrl["LastCard"]
        else:                             last_card = ""
        
        if "stream" in song:
          stream = song["stream"]
          song   = {}
        else:
          stream = {}

        self.music_ctrl = {
          "device"        : self.music_device,
          "type"          : self.music_type,
          "mute"          : self.player.volume_mute,
          "status"        : self.player.player_status,
          "connected"     : self.player.connected,
          "file"          : self.player.play_url,
          "song"          : song,
          "stream"        : stream,
          "playlist"      : playlist["list"],
          "playlist_pos"  : playlist["position"],
          "playlist_len"  : playlist["length"],
          "playlist_files": playlist["files"],
          "playlist_uuid" : self.music_list_uuid,
          "volume"        : self.player.volume,
          "position"      : self.player.get_position(),
          "length"        : self.player.get_length(),
          "playing"       : self.player.playing(),
          "state"         : state,
          "LastCard"      : last_card
          }
      else:
        self.music_ctrl = {
          "device"        : self.music_device,
          "mute"          : False,
          "status"        : "",
          "connected"     : False,
          "file"          : "",
          "song"          : {},
          "stream"        : {},
          "playlist"      : [],
          "playlist_pos"  : -1,
          "playlist_len"  : -1,
          "playlist_files": [],
          "playlist_uuid" : "",
          "volume"        : 0.4,
          "position"      : -1,
          "length"        : -1,
          "playing"       : -1,
          "state"         : state,
          "type"          : "",
          "LastCard"      : ""
          }
      return self.music_ctrl




