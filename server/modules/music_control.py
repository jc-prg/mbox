# ------------------------
# control music playback
# ------------------------

import threading
import time
import operator
import logging
import vlc

import modules.jcJson       as jcJSON
import modules.jcCouchDB    as jcCouch
import modules.config_stage as stage
import modules.config_mbox  as mbox
import modules.speakmsg     as speak

from modules.config_mbox import *
from decimal             import *

# ------------------------
# THREADING CLASS

class musicThread (threading.Thread):

   def __init__(self, threadID, name, counter, database):
      '''set initial values to vars and start pygame.mixer'''

      # init thread
      threading.Thread.__init__(self)
      self.threadID     = threadID
      self.name         = name
      self.counter      = counter
      self.stopProcess  = False

      self.music_list     = []
      self.music_list_p   = 1
      self.music_ctrl     = {}
      self.music_database = database
      self.music_loaded   = -1
      self.music_plays    = -1
      self.music_dir      = mbox.music_dir

      self.music_ctrl["device"]  = "music_box"
      self.music_ctrl["mute"]    = 0
      self.music_ctrl["status"]  = "init"
      self.music_ctrl["file"]    = ""
      self.music_ctrl["song"]    = {}
      self.music_ctrl["volume"]  = 0.4 # initial volume 
      self.music_ctrl["position"]= 0
      self.music_ctrl["length"]  = 0
      self.music_ctrl["playing"] = 0
      self.music_ctrl["state"]   = "Started"
      
      self.music_load_new   = False

      self.speak = speak.speakThread(4, "Thread speak", 1, "")  #  jcJSON.read("music"), jcJSON.read("radio"))
      self.speak.start()

      self.relevant_db  = self.music_database.databases["music"] # ["albums","album_info","tracks","files","cards"]
      self.vol_factor   = 0.8 # factor to limit audio level (max = 1.0)

      if stage.rollout == "prod":     self.instance     = vlc.Instance("--quiet")
      else:                           self.instance     = vlc.Instance()
      
      self.player       = self.instance.media_player_new()
      self.player.audio_set_volume(int(self.music_ctrl["volume"]*100))
      self.player.audio_set_mute(False)
      
      self.last_card_identified = ""

      # init mixer
      #global music_plays, music_loaded, music_ctrl

   def run(self):
      logging.info( "Starting " + self.name )
      musicPlayList(self)
      logging.info( "Exiting " + self.name )

   def stop(self):
      self.stopProcess = True

   def reload_data(self):
      self.music_data         = {}
      #self.music_data["data"] = self.database.readGroup("music")
      #self.store_data         = self.music_database.readGroup("music")

   #-------------------------

   def load_list(self,list):
      '''
      load playlist by list of filenames
      '''
      logging.info( "Load list: " + str(len(list)) )
      test = self.return_list(list)
      musicStartList(self,test)
      self.music_loaded = 1


   def load_list_uuid(self,list):
      '''
      load playlist by UUID
      '''
      if ("r_" not in list):
        logging.info( "Load playlist uuid: " + list )
        test = musicGetTracks(self,list)    # veraendert die reihenfolge?
        test = musicUuid2Files(self,test)   # veraendert die reihenfolge?
        musicStartList(self,test)
        self.music_ctrl["playlist_uuid"] = list
        self.music_loaded = 1

   def return_list(self,list):
      list2 = []
      for x in list:
        list2.append(x)
      return(list2)


   def stop_playback(self):
      '''
      stop running song
      '''
      self.player.stop()
      self.music_ctrl["playing"] = 0


   def pause_playback(self):
      '''
      pause / unpause running song
      '''
      logging.info("PAUSE: "+self.music_ctrl["state"])

      if (self.music_ctrl["state"] == "State.Playing"):
          self.player.pause()
          self.music_plays = 0
          self.music_ctrl["status"] = "pause"

      if (self.music_ctrl["state"] == "State.Paused"):
          self.player.play()
          self.music_plays = 1
          self.music_ctrl["status"] = "play"

      logging.info("PAUSE: "+self.music_ctrl["state"])


   def music_vol(self,up):
      '''
      control volume ...
      '''
      vol = float(self.music_ctrl["volume"])
      logging.info("MUSIC VOL: "+str(vol)+"/"+str(self.vol_factor)+"//"+str(up))

      if (up == "up" and vol < 1.0):
        vol = vol + 0.05
        print("up")
        
      elif (up == "down" and vol > 0.0):
        vol = vol - 0.05
        print("down")
        
      elif (isinstance(up, int) and up >= 0 and up <= 100):
        vol = up / 100
        print("set vol:"+str(vol))
        logging.warn("test ..."+str(vol))


      logging.info("MUSIC VOL:"+str(vol)+"/"+str(self.vol_factor))

      self.player.audio_set_volume(int(vol*100))
      self.music_ctrl["mute"]   = 0
      self.music_ctrl["volume"] = vol


   def music_mute(self):
      '''
      set to mute / unmute
      '''
      if self.music_ctrl["mute"] == 0:
          self.music_ctrl["mute"] = 1
          self.player.audio_set_volume(0)
      else:
          self.music_ctrl["mute"] = 0
          logging.info("VOL: "+str(self.music_ctrl["volume"]))
          self.player.audio_set_volume(int(self.music_ctrl["volume"]*100))


   def playlist_next(self,step):
      '''
      step back (-1) or forward (1)
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
      
   def playing_jump(self,percentage):
      '''
      jump to position in playing song
      '''
      percentage = float(percentage)   
      if percentage >= 0 and percentage <= 100:
          self.player.set_position(percentage/100)
          return "done"
      return "not found"
      
   def play_file(self, filename):
      '''
      play file via filename
      '''
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
          self.player.audio_set_volume(int(self.music_ctrl["volume"]*100))
          return "Error"
        
      self.player.audio_set_volume(int(self.music_ctrl["volume"]*100))
      return "Ended"

#------------------

def musicLoadRfidList(thread):
    '''
    load list connected to rfid
    '''
    if "cardUID" in mbox.rfid_ctrl:
      logging.debug("#################### " + mbox.rfid_ctrl["cardUID"])
      cardDB = thread.music_database.read_cache("cards")

      # check if card detected ...
      if (mbox.rfid_ctrl["cardUID"] != ""):
        logging.info("CardUID: "+mbox.rfid_ctrl["cardUID"])

        # check if playlist connected to card (and not radio)
        if (mbox.rfid_ctrl["cardUID"] in cardDB and not "r_" in cardDB[rfid_ctrl["cardUID"]][0]):

          if ("LastCard" not in thread.music_ctrl or thread.music_ctrl["LastCard"] != cardDB[mbox.rfid_ctrl["cardUID"]][0]):
            logging.info("Start Playlist: "+cardDB[mbox.rfid_ctrl["cardUID"]][0])
            thread.load_list_uuid(cardDB[mbox.rfid_ctrl["cardUID"]][0])
            thread.music_ctrl["LastCard"]      = cardDB[mbox.rfid_ctrl["cardUID"]][0]
            thread.music_load_new       = True

          else:
            logging.info("Card already started ...")

        # else stop playing
        else:
          thread.music_ctrl["LastCard"]       = ""
          thread.music_ctrl["playlist_uuid"]  = ""
          thread.player.stop()
          if mbox.rfid_ctrl["cardUID"] != thread.last_card_identified:
             logging.info("No Entry connected.")
             thread.last_card_identified = mbox.rfid_ctrl["cardUID"]
          
             if mbox.rfid_ctrl["cardUID"] not in cardDB: 
                thread.speak.speak_message("NO-MUSIC-CONNECTED-TO-CARD")
             
#          if not "r_" in cardDB[rfid_ctrl["cardUID"]][0]:  thread.speak.speak_message("NO-MUSIC-CONNECTED-TO-CARD")

#------------------

def musicPlaying(thread):
        '''
        Translate playback status to 0/1
        '''
        old_state                     = thread.music_ctrl["state"]
        thread.music_ctrl["state"]    = str(thread.player.get_state())
        
        if thread.music_ctrl["state"] == "State.Playing" or thread.music_ctrl["state"] == "State.Paused":
            thread.music_plays = 1
            logging.debug("Playing 01:"+thread.music_ctrl["state"]+"..."+str(thread.music_ctrl["playing"]))
        else:
            thread.music_plays = 0
            logging.debug("Playing 02:"+thread.music_ctrl["state"]+"..."+str(thread.music_ctrl["playing"]))

        thread.music_ctrl["playing"]  = thread.music_plays

#------------------

def musicSaveStatus(thread):
    '''
    Save playback status in the database
    '''
    data  = thread.music_database.read("status")
    
    if not "_saved" in data or data["_saved"] + 3 < time.time():
    
      data["music"]  = thread.music_ctrl
      data["_saved"] = time.time()

      if thread.music_ctrl["state"] == "State.Playing" or thread.music_ctrl["state"] == "State.Paused": 
        data["_device"] = "music"
    
      thread.music_database.write("status",data)

#------------------

def musicPlayList(thread):
    '''
    Play list, detect end of file and than play next
    '''
    wait_time = 0.5
    running   = True
    last_load = False  
    last_run  = thread.music_database.read("status")
    
    if "_device" in last_run and last_run["_device"] == "music" and last_run["music"]["playing"] == 1:
      logging.info("Load playlist and song from last run ...")
      last_load           = True
      last_music          = last_run["music"]
      thread.music_ctrl   = last_music
      thread.music_loaded = 1
      
      if "playlist_files" in last_music:
         thread.music_list     = last_music["playlist_files"]
         thread.music_list_p   = last_music["playlist_pos"]
         thread.music_load_new = True
         time.sleep(4)
         
    while running and not thread.stopProcess:

      # wait a moment ...
      time.sleep(wait_time)
      logging.debug("List active: " + str(thread.music_load_new) + "; List: " + str(len(thread.music_list)) + "; Position: " + str(thread.music_list_p) )

      musicLoadRfidList(thread)     # check if RFID card detected -> load playlist, if new
      musicPlaying(thread)          # check player state
      musicSaveStatus(thread)       # save playback status to database

      # start playing a new song ?
      logging.debug("CHECK: " + str(len(thread.music_list)) + "/" + str(thread.music_load_new))

      file    = ""
      # if additional song in the list and change detected ...
      if len(thread.music_list) > 0 and thread.music_load_new: 

        file = music_dir + thread.music_list[thread.music_list_p-1]
        logging.info("Play: " + file)

        thread.media = thread.instance.media_new( file ) #str(file.encode('utf-8')) )
        thread.player.set_media(thread.media)
        thread.player.play()
        time.sleep(2)
        
        # Jump to position if first load ...
        if last_load:
           position = (thread.music_ctrl["position"] / thread.music_ctrl["length"]) * 100
           thread.playing_jump(position)
           last_load = False

        # check player state
        musicPlaying(thread)

        # if music is still playing ... get playback status
        if thread.music_ctrl["playing"] != 0:

           thread.music_ctrl["file"]             = file
           thread.music_ctrl["song"]             = {}
           thread.music_ctrl["song"]             = musicGetInfo(thread,file.replace(music_dir,""))
           thread.music_ctrl["song"]["info"]     = "Title loaded"
           thread.music_ctrl["playlist"]         = musicGetInfoList(thread,thread.music_list)
           thread.music_ctrl["playlist_pos"]     = thread.music_list_p
           thread.music_ctrl["playlist_len"]     = len(thread.music_list)
           thread.music_ctrl["playlist_files"]   = thread.music_list           
           thread.music_ctrl["status"]           = "play"
           thread.music_ctrl["length"]           = float(thread.player.get_length()) / 1000
           thread.music_ctrl["position"]         = float(thread.player.get_time()) / 1000
           thread.music_load_new                 = False

        # if music is not playing
        else:

           thread.music_ctrl["file"]         = file
           thread.music_ctrl["song"]         = {}
           thread.music_ctrl["status"]       = "error"
           thread.music_ctrl["position"]     = -1 #thread.music.mixer.get_pos()
           thread.music_ctrl["length"]       = -1 #thread.music.mixer.get_length()

      # if song is playing ...
      if thread.music_load_new == False: 
      
          thread.music_ctrl["length"]    = float(thread.player.get_length()) / 1000
          thread.music_ctrl["position"]  = float(thread.player.get_time()) / 1000

          if thread.music_ctrl["state"] == "State.Ended":

            if thread.music_list_p < len(thread.music_list):     # If there are more tracks in the queue...

               thread.music_load_new = True
               thread.music_list_p = thread.music_list_p+1
               logging.info("Next song in list, position: " + str(thread.music_list_p))

            else:
               thread.music_load_new = True
               thread.music_list = []
               logging.info("Playlist empty, stop playing.")

#------------------

def musicStartList(thread,list):
    '''
    Play Songs from List, if Songs in List
    '''
    for x in list:
      logging.debug("Add 2 Playlist: " + x)

    logging.debug("Start List: "+str(len(list)) + "/" + str(len(thread.music_list)))
    thread.music_list   = list
    thread.music_list_p = 1

    # reset data that the loop reloads the playlist
    if len(thread.music_list) > 0:
       thread.player.stop()
       thread.music_plays    = 0
       thread.music_load_new = True

    # set data to show that playlist is empty
    else:
       thread.music_loaded   = 0
       thread.music_plays    = 0
       thread.music_load_new = True


#------------------

def musicGetInfoList(thread,file_list):
    '''
    get info for list of tracks based on filenames
    '''
    list_info  = []
    for x in file_list:
      file_info = musicGetInfo(thread,x)
      list_info.append(file_info)
    return list_info

#------------------

def musicGetInfo(thread,file):
    '''
    get info for a track based on filename
    '''
    file_info         = {}
    file_info["test"] = file

    songs = thread.music_database.read_cache("files")
    if file in songs:
      file_info = songs[file]

    return file_info

#------------------

def musicGetTracks(thread,album_uuid):
    '''
    return uuid form tracks for an album
    '''
    logging.debug("Read infos for album UUID: "  + album_uuid)

    # set vars
    tracks      = []
    track_list  = []
    track_order = {}

    #db            = thread.music_database.readGroup("music")
    db_album_info  = thread.music_database.read_cache("album_info")
    db_playlists   = thread.music_database.read_cache("playlists")
    db_tracks      = thread.music_database.read_cache("tracks")

    logging.debug("test // " + album_uuid)

    # read data from db IF Album
    if "a_" in album_uuid and album_uuid in db_album_info:
       songs       = db_album_info                      # db["album_info"]
       tracks      = songs[album_uuid]["tracks"]
       track_info  = db_tracks                          # db["tracks"]
       track_list  = sortAlbumTracks(tracks,track_info)

    # read data from db IF Playlist
    elif "p_" in album_uuid and album_uuid in db_playlists:
       songs       = db_playlists                       # db["playlists"]
       tracks1     = songs[album_uuid]["tracks"]
       tracks      = []
       track_info  = db_tracks                          # db["tracks"]

       for key in tracks1:
         if "t_"   in key: tracks.append(key)
         elif "a_" in key:
           tracks2 = db_album_info[key]["tracks"]       # db["album_info"][key]["tracks"]
           tracks2 = sortAlbumTracks(tracks2,track_info)
           for key2 in tracks2: tracks.append(key2)

       track_list = tracks
       
    else:
       thread.speak.speak_message("UNVALID-ENTRY-CONNECTED-TO-CARD")

    return track_list


def sortAlbumTracks(tracks,track_info):
     '''
     sort albums bei track number
     '''
     track_order = {}
     track_list  = []

     # check / read track order
     for x in tracks:

        if x not in track_info: return tracks

        track_i = track_info[x]                # produces errors -> added check before
        track_o = track_i["track_num"][0]

        if "/" in str(track_o):
          track_o = track_o.split("/")[0]

        try:
          track_order[x] = int(track_o)
        except:
          return tracks

     track_order = sorted(track_order.items(), key=operator.itemgetter(1))

     for x in track_order:
        track_list.append(x[0])

     return track_list


#------------------

def musicUuid2Files(thread,uuid_list):
    '''
    return filenames based on an uuid names for a list
    '''
    file_list = []
    songs = thread.music_database.read_cache("tracks")
    for x in uuid_list:
      #print songs[x]["file"]
      file_list.append(songs[x]["file"])

    return file_list

#------------------
