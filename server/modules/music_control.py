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

from modules.config_mbox import *
from decimal             import *

# ------------------------

music_list        = list()
music_list_active = False

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

      self.relevant_db  = self.music_database.databases["music"] # ["albums","album_info","tracks","files","cards"]
      self.vol_factor   = 0.8 # factor to limit audio level (max = 1.0)

      self.instance     = vlc.Instance("--quiet")
      self.player       = self.instance.media_player_new()
      self.player.audio_set_volume(int(self.music_ctrl["volume"]*100))
      self.player.audio_set_mute(False)

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
      logging.info( "Load list: " + str(len(list)) )
      test = self.return_list(list)
      musicStartList(self,test)
      self.music_loaded = 1


   def load_list_uuid(self,list):
      if ("r_" not in list):
        logging.info( "Load playlist uuid: " + list )
        test = musicGetTracks(self,list)    # veraendert die reihenfolge?
        test = musicUuid2Files(self,test)   # veraendert die reihenfolge?
        musicStartList(self,test)
        self.music_ctrl["playlist_uuid"] = list
        self.music_loaded = 1
      else:
        return


   def return_list(self,list):
      list2 = []
      for x in list:
        list2.append(x)
      return(list2)


   def stop_playback(self):
      '''stop running song'''

      self.player.stop()
      self.music_ctrl["playing"] = 0


   def pause_playback(self):
      '''pause / unpause running song'''

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
      '''control volume ...'''

      vol = float(self.music_ctrl["volume"])
      logging.info("MUSIC VOL: "+str(vol)+"/"+str(self.vol_factor)+"//"+str(up))

      if (up == "up" and vol < 1.0):
        vol = vol + 0.05
        print("up")
      elif (vol > 0.0):
        vol = vol - 0.05
        print("down")

      logging.info("MUSIC VOL:"+str(vol)+"/"+str(self.vol_factor))

      self.player.audio_set_volume(int(vol*100))
      self.music_ctrl["mute"]   = 0
      self.music_ctrl["volume"] = vol


   def music_mute(self):
      '''set to mute'''

      if self.music_ctrl["mute"] == 0:
          self.music_ctrl["mute"] = 1
          self.player.audio_set_volume(0)
      else:
          self.music_ctrl["mute"] = 0
          logging.info("VOL: "+str(self.music_ctrl["volume"]))
          self.player.audio_set_volume(int(self.music_ctrl["volume"]*100))


   def playlist_next(self,step):
      '''step back (-1) or forward (1)'''

      global music_list_active
      logging.debug("Next song: "+str(step)+"+"+str(self.music_list_p)+" ("+str(len(self.music_list))+")" )

      # back // if position > 0
      if step < 0 and self.music_list_p + step > 0:
        self.player.stop()
        self.music_list_p = self.music_list_p + step       # set new position in playlist
        music_list_active = False                          # set var for play next title in playlist
        return "done"

      # forward // if position < length of list
      elif step > 0 and self.music_list_p + step <= len(self.music_list):
        self.player.stop()
        self.music_list_p = self.music_list_p + step       # set new position in playlist
        music_list_active = False                          # set var for play next title in playlist
        return "done"

      # stop playing if beginning or end ...
      else:
        self.player.stop()
        self.music_list_p = 0                              # set new position in playlist
        music_list_active = True                           # set var for play next title in playlist

      return "not found"

#------------------

def musicLoadRfidList(thread):
    '''load list connected to rfid'''


    if "cardUID" in mbox.rfid_ctrl:
      logging.info("#################### " + mbox.rfid_ctrl["cardUID"])
      cardDB = thread.music_database.read("cards")

      # check if card detected ...
      if (mbox.rfid_ctrl["cardUID"] != ""):
        logging.info("CardUID: "+mbox.rfid_ctrl["cardUID"])

        # check if playlist connected to card (and not radio)
        if (mbox.rfid_ctrl["cardUID"] in cardDB and not "r_" in cardDB[rfid_ctrl["cardUID"]][0]):

          if ("LastCard" not in thread.music_ctrl or thread.music_ctrl["LastCard"] != cardDB[mbox.rfid_ctrl["cardUID"]][0]):
            logging.info("Start Playlist: "+cardDB[mbox.rfid_ctrl["cardUID"]][0])
            thread.load_list_uuid(cardDB[mbox.rfid_ctrl["cardUID"]][0])
            thread.music_ctrl["LastCard"]      = cardDB[mbox.rfid_ctrl["cardUID"]][0]
            music_list_active = False

          else:
            logging.info("Card already started ...")

        # else stop playing
        else:
          logging.info("No Playlist connected.")
          thread.music_ctrl["LastCard"]       = ""
          thread.music_ctrl["playlist_uuid"]  = ""
          thread.player.stop()

#------------------

def musicPlaying(thread):

        thread.music_ctrl["state"] = str(thread.player.get_state())
        thread.music_plays = 0

        if thread.music_ctrl["state"] == "State.Playing" or thread.music_ctrl["state"] == "State.Paused":
            thread.music_plays = 1
            logging.debug("Playing 01:"+thread.music_ctrl["state"])
        else:
            thread.music_plays = 0
            logging.debug("Playing 02:"+thread.music_ctrl["state"])

        thread.music_ctrl["playing"]  = thread.music_plays

        logging.debug("......"+str(thread.music_ctrl["state"])+"..."+str(thread.music_ctrl["playing"]))

def musicPlayList(thread):
    '''pygame event handler'''

    global music_list_active #, music_dir #, music_ctrl

    running = True
    while running and not thread.stopProcess:

      time.sleep(1)
      logging.debug("List active: " + str(music_list_active) + "; List: " + str(len(thread.music_list)) + "; Position: " + str(thread.music_list_p) )

      # check if RFID card detected -> load playlist, if new
      musicLoadRfidList(thread)

      # check player state
      musicPlaying(thread)

      # start playing a new song (music_list_active = False):
      logging.debug("CHECK: " + str(len(thread.music_list)) + "/" + str(music_list_active))
      time.sleep(2)

      file    = ""
      if len(thread.music_list) > 0 and not music_list_active:

        file = music_dir + thread.music_list[thread.music_list_p-1]
        logging.info("Play: " + file)

        thread.media = thread.instance.media_new( file ) #str(file.encode('utf-8')) )
        thread.player.set_media(thread.media)
        thread.player.play()
        time.sleep(1)

        musicPlaying(thread)

        if thread.music_ctrl["playing"] != 0:

           thread.music_ctrl["file"]         = file
           thread.music_ctrl["song"]         = {}
           thread.music_ctrl["song"]         = musicGetInfo(thread,file.replace(music_dir,""))
           thread.music_ctrl["song"]["info"] = "Title loaded"
           thread.music_ctrl["playlist"]     = musicGetInfoList(thread,thread.music_list)
           thread.music_ctrl["playlist_pos"] = thread.music_list_p
           thread.music_ctrl["playlist_len"] = len(thread.music_list)
           thread.music_ctrl["status"]       = "play"
           thread.music_ctrl["length"]       = float(thread.player.get_length()) / 1000
           thread.music_ctrl["position"]     = thread.player.get_time() #/1000
           music_list_active                 = True

        else:

           thread.music_ctrl["file"]         = file
           thread.music_ctrl["song"]         = {}
           thread.music_ctrl["status"]       = "error"
           thread.music_ctrl["position"]     = -1 #thread.music.mixer.get_pos()
           thread.music_ctrl["length"]       = -1 #thread.music.mixer.get_length()

      # handle event for end of song
      if music_list_active == True:
          thread.music_ctrl["position"]  = thread.player.get_time() #/1000
          if thread.music_ctrl["state"] == "State.Ended":

            if thread.music_list_p < len(thread.music_list):     # If there are more tracks in the queue...

               music_list_active   = False
               thread.music_list_p = thread.music_list_p+1
               logging.info("Next song in list, position: " + str(thread.music_list_p))

            else:
               music_list_active = False
               thread.music_list = []
               logging.info("Playlist empty, stop playing.")

#------------------

def musicStartList(thread,list):
    '''Play Songs from List, if Songs in List'''

    for x in list:
      logging.debug("Add 2 Playlist: " + x)

    global music_list_active, music_dir
    logging.debug("Start List: "+str(len(list)) + "/" + str(len(thread.music_list)))
    thread.music_list   = list
    thread.music_list_p = 1

    # reset data that the loop reloads the playlist
    if len(thread.music_list) > 0:
       thread.player.stop()
       thread.music_plays = 0
       music_list_active  = False

    # set data to show that playlist is empty
    else:
       thread.music_loaded = 0
       thread.music_plays  = 0
       music_list_active   = False


#------------------

def musicGetInfoList(thread,file_list):
    ''' get info for list of tracks based on filenames '''

    list_info  = []
    for x in file_list:
      file_info = musicGetInfo(thread,x)
      list_info.append(file_info)
    return list_info

#------------------

def musicGetInfo(thread,file):
    ''' get info for a track based on filename '''

    file_info         = {}
    file_info["test"] = file

    songs = thread.music_database.read_cache("files")
    if file in songs:
      file_info = songs[file]

    return file_info

#------------------

def musicGetTracks(thread,album_uuid):
    '''return uuid form tracks for an album'''

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
    if "a_" in album_uuid:
       songs       = db_album_info                      # db["album_info"]
       tracks      = songs[album_uuid]["tracks"]
       track_info  = db_tracks                          # db["tracks"]

    # read data from db IF Playlist
    elif "p_" in album_uuid:
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


    # sort by song number if album
    if "a_" in album_uuid:
      track_list = sortAlbumTracks(tracks,track_info)

    else:
      track_list = tracks

    return track_list


def sortAlbumTracks(tracks,track_info):
     '''sort albums bei track number'''

     track_order = {}
     track_list  = []

     # check / read track order
     for x in tracks:
        track_i = track_info[x]
        track_o = track_i["track_num"][0]
        track_order[x] = int(track_o)

     track_order = sorted(track_order.items(), key=operator.itemgetter(1))

     for x in track_order:
        track_list.append(x[0])

     return track_list


#------------------

def musicUuid2Files(thread,uuid_list):

    ''' return filenames based on an uuid names for a list '''

    file_list = []
    songs = thread.music_database.read_cache("tracks")
    for x in uuid_list:
      #print songs[x]["file"]
      file_list.append(songs[x]["file"])

    return file_list

#------------------