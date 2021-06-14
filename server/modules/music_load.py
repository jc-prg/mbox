#---------------------------------
# Manage Music Files
#---------------------------------

import modules.config_stage  as stage
import modules.config_mbox   as mbox
import modules.jcJson        as jcJSON
import modules.jcCouchDB     as jcCouch

from modules.config_mbox     import *
from modules.runcmd          import *
from modules.music_metadata  import *

#from mutagen.id3         import ID3
#from mutagen.mp3         import MP3
#from mutagen.mp4         import MP4, MP4Cover

import eyed3
import os
import uuid
import logging
import threading
import time

#---------------------------------

class musicLoadingThread (threading.Thread):

   def __init__(self, threadID, name, counter, database):
      '''set initial values to vars and start pygame.mixer'''

      # init thread
      threading.Thread.__init__(self)
      self.threadID        = threadID
      self.name            = name
      self.counter         = counter
      self.stopProcess     = False

      self.reload_all        = False
      self.reload_new        = False
      self.reload_img        = False
      self.reload_progress   = 0
      self.reload_time_start = 0
      self.reload_time_left  = 0
      self.music_database    = database

      self.supported_img     = [".jpg",".jpeg",".JPG",".png",".PNG"]
      self.supported_mp3     = [".mp3",".MP3"]
      self.supported_mp4     = [".mp4",".m4a",".MP4",".M4A"]  # .M4P metadata can be read but music is DRM protected -> convert to use this file format
      self.supported_mpX     = [".mp3",".MP3",".mp4",".m4a",".MP4",".M4A"]

   #------

   def run(self):
      '''control reload of music data'''

      logging.info( "Starting " + self.name )
      while not self.stopProcess:

        # reload cached data in the background when changed something
        if self.music_database.changed_data:
            self.music_database.fill_cache()
            self.music_database.changed_data = False


        # set start time for reloading
        if self.reload_all or self.reload_new or self.reload_img:
            self.reload_time_start = time.time()

        # reload all data delete existing
        if self.reload_all:
            logging.info( "Starting Reload ALL" )

            self.store_data        = self.music_database.readGroup("music")
            self.store_data        = reloadMusic(self.store_data, True,  self)
            for key in self.store_data:
               self.music_database.write(key,self.store_data[key])

        # check if new files and load data for new files
        elif self.reload_new:
            logging.info( "Starting Reload NEW" )

            self.store_data      = self.music_database.readGroup("music")
            self.store_data      = reloadMusic(self.store_data, False,  self)
            for key in self.store_data:
               self.music_database.write(key,self.store_data[key])

        # check if new images in directories available
        elif self.reload_img:
            logging.info( "Starting Reload IMAGES" )

            self.store_data      = self.music_database.read("album_info")
            self.store_data      = reloadCoverImages(self.store_data, self)

            self.music_database.write("album_info",self.store_data)

        # clean progress and reload request
        if self.reload_all or self.reload_new or self.reload_img:

            self.music_database.fill_cache()
            self.music_database.changed_data = False

            self.reload_progress   = 0
            self.reload_time_start = 0

            self.reload_all        = False
            self.reload_new        = False
            self.reload_img        = False


        time.sleep(2)

      logging.info( "Exiting " + self.name )


   def stop(self):
      '''Stop thread to reload music data'''

      self.stopProcess = True


#---------------------------------

def readFiles(dir):
    '''
    get all files from directory
    dont return files, if a file ".dont-scan" exists in directory
    '''
    
    command = "find -L "+dir+" -maxdepth 4"
    logging.info("Read files: " + command)
      
    list,error=runCmd(command)
    files=list.splitlines()
    
    noscan       = []
    files_return = []
    if len(files) > 1:
      for directory in files:
        if ".dont-scan" in directory:
          dir_parts = directory.split("/")
          dir_parts = dir_parts[:-1]
          noscan.append("/".join(dir_parts))
    
      for filename in files:
        scan = True
        
        for entry in noscan:
          if entry in filename: 
            scan = False
         
        if scan == True: 
          files_return.append(filename)

    logging.info("Dont scan directories: "+str(noscan))
    
    return files_return

#------------------------------------

def AlbumByPath(file):
    '''separate infos from path'''

    global music_dir

    album     = ""
    localpath = file.replace(music_dir,"")
    list      = localpath.split("/")
    list.pop(len(list)-1)
    for x in list:
      album = album + "_" + x

    return album


#------------------------------------

def checkIfCardExists(data_cards,album,artist,uuid):
    '''Check for JPG files in the folder again without reloading the music'''

    update_time = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
    for card_id in data_cards:

      # check if card
      if "," in card_id:

        # if data error
        if len(data_cards[card_id]) < 3: return data_cards, ""

        # check if album and artist exist
        if data_cards[card_id][1] == album and data_cards[card_id][2] == artist:

          data_cards[card_id][0] = uuid                                                       # replace old UUID by current UUID

          if len(data_cards[card_id]) > 3:  data_cards[card_id][3] = update_time              # add date when replaced UUID last time
          else:                             data_cards[card_id].append(update_time)

          return data_cards, card_id	    # return data and card_id

    return data_cards, ""

#------------------------------------

def checkIfPlaylistEntryExists(data, entry_uuid, entry_ref):
    '''
    check album and track list, if track or file exists
    '''
    check_uuid = "NOT FOUND"
    check_ref  = "NOT FOUND"
    
    if entry_uuid.startswith("a_"):
       if entry_uuid in data["album_info"]: 
          check_uuid = entry_uuid
       else:
         for album_uuid in data["album_info"]:
           if data["album_info"][album_uuid]["albumpath"] == entry_ref:
             check_uuid = album_uuid
             check_ref  = data["album_info"][album_uuid]["albumpath"]
       
    elif entry_uuid.startswith("t_"):
       if entry_uuid in data["tracks"]: 
          check_uuid = entry_uuid
       else:
         for track_uuid in data["tracks"]:
           if data["tracks"][track_uuid]["file"] == entry_ref:
             check_uuid = track_uuid
             check_ref  = data["tracks"][track_uuid]["file"]

    logging.debug("checkIfPlaylistEntryExists : "+entry_uuid+" -> "+check_uuid)
    return check_uuid

#------------------------------------

def checkIfSupported(supported_formats,file_name):
     supported = False
     for type in supported_formats:
          if type in file_name: supported = True
     return supported

#------------------------------------

def reloadCoverImages(data,thread=""):
    '''Check for JPG files in the folder again without reloading the music'''

    global music_dir, music_cover
    files            = readFiles(music_dir)
    files_amount     = len(files)
    files_count      = 0
    files_percentage = 0

    # remove old entries
    for key in data:
        data[key]["cover_images"]["dir"] = []

    # check list of files
    for file in files:

       files_count      += 1
       files_percentage  = float(files_count) / float(files_amount) * 100
       if thread != "":
          thread.reload_progress  = files_percentage
          current_time = time.time()
          thread.reload_time_required = time.time() - thread.reload_time_start
          thread.reload_time_left     = thread.reload_time_required * (100 - files_percentage) / files_percentage
       logging.info("Reload progress: "+str(files_percentage)+"%")


       # check if image file in folder (and take last one as alternative cover)
       if os.path.isfile(file) and checkIfSupported(thread.supported_img,file) == True:

          for key in data:
              file_e = file.replace("/","_")
              if (data[key]["albumpath"] in file_e):
                  file_e = file.replace(music_dir,"")
                  data[key]["cover_images"]["dir"].append(file_e)
                  data[key]["cover_images"]["active"] = "dir"

    return data


#------------------------------------


def reloadMusic_getCurrentWithoutErrors(data_current):
    '''
    if only new files shall be loaded, the current data have to be prepare as base
    therefor all db entries with errors will be deleted as they will be detected again (if they still exist)
    '''

    data_keys   = ["albums","album_info","artists","files","tracks"]
    data_reload = {}
    logging_msg = []
    
    for key in data_keys:
       data_reload[key] = {}
    
    for x in data_current["albums"]:
       if "#error" in x:  logging_msg.append("albums: "+x)
       else:              data_reload["albums"][x] = data_current["albums"][x]
       
    for x in data_current["artists"]:
       if "#error" in x:  logging_msg.append("artists: "+x)
       else:              data_reload["artists"][x] = data_current["artists"][x]
       
    for x in data_current["files"]:
       if "#error" in data_current["files"][x]["artist"]:       logging_msg.append("files: "+x)
       else:                                                    data_reload["files"][x] = data_current["files"][x]
       
    for x in data_current["tracks"]:
       if "#error" in data_current["tracks"][x]["artist"]:      logging_msg.append("tracks: "+x)
       else:                                                    data_reload["tracks"][x] = data_current["tracks"][x]
       
    for x in data_current["album_info"]:
       if "#error" in data_current["album_info"][x]["artist"]:  logging_msg.append("album_info: "+x)
       else:                                                    data_reload["album_info"][x] = data_current["album_info"][x]
       
    for x in logging_msg:
       logging.info(x)
       
    return data_reload

#------------------------------------

def reloadMusic_setProgessInfo(count, total, thread):
    '''
    '''

    files_percentage  = float(count) / float(total) * 100
    if thread != "":
       thread.reload_progress      = files_percentage
       current_time                = time.time()
       thread.reload_time_required = time.time() - thread.reload_time_start
       thread.reload_time_left     = thread.reload_time_required * (100 - files_percentage) / files_percentage
       if files_percentage == 100: thread.reload_time_left = 0

    logging.debug("Reload progress: "+str(files_percentage)+"%")
    
#------------------------------------
    
def reloadMusic_createAlbumInfo(track_data):
    '''
    create album info from track data
    '''
    album_info    = {}
    album_dir     = {}
    sorted_tracks = {}

    # recreate album_infos based on tracks: (1) get all paths from tracks
    for track in track_data:
        file_path = track_data[track]["file"]
        temp      = file_path.split("/")
        file_name = temp[len(temp)-1]
        file_path = file_path.replace(file_name,"")
        if "album_uuid" in track_data[track]:  album_dir[file_path] = track_data[track]["album_uuid"]
        else:                                  album_dir[file_path] = "NEW_ENTRY"
        
    # recreate album_infos based on tracks: (2) get album infos from tracks and check if it's a compilation (more than 1 artist)
    for album_path in album_dir:

        album_uuid   = album_dir[album_path]
        if album_uuid == "NEW_ENTRY":
           album_uuid = "a_"+str(uuid.uuid1())
           
        album_data = {
             "uuid"         : album_uuid,
             "artist"       : "",
             "album"        : "",
             "albumname"    : "",
             "albumpath"    : album_path,
             "albumlength"  : 0,
             "albumsize"    : 0,
             "compilation"  : False,
             "card_id"      : 0,		#### GET FROM OLD ENTRY, IF EXISTS !!!
             "genre"        : [],
             "tracks"       : [],
             "track_count"  : 0,
             "error"        : [],
             "cover_images" : {"active" : "dir", "active_pos" : 0, "upload" : [], "dir" : [], "track" : []}
             }
        album_data_error = {
             "uuid"         : album_uuid+"_error",
             "artist"       : "",
             "album"        : "",
             "albumname"    : "",
             "albumpath"    : album_path,
             "albumlength"  : 0,
             "albumsize"    : 0,
             "compilation"  : False,
             "card_id"      : 0,		#### GET FROM OLD ENTRY, IF EXISTS !!!
             "genre"        : [],
             "tracks"       : [],
             "track_count"  : 0,
             "error"        : [],
             "cover_images" : {"active" : "dir", "active_pos" : 0, "upload" : [], "dir" : [], "track" : []}
             }
             
        track_count       = 0
        track_count_error = 0
        
        for track_uuid in track_data:
           if album_path in track_data[track_uuid]["file"]:
              track_info       = track_data[track_uuid]
              
              if "#error" in track_info["artist"]:
                  track_count_error += 1
                  album_data_error["album"]       = track_info["album"] 
                  album_data_error["albumname"]   = track_info["album"] 
                  album_data_error["artist"]      = track_info["artist"]
                  
                  if "error" in track_info: album_data_error["error"].append(track_info["error"])              
                  
                  album_data_error["tracks"].append(track_uuid)
                  album_data_error["track_count"]  = track_count_error
              
              else:
                track_count += 1
                if track_count == 1:
                  album_data["album"]       = track_info["album"] 
                  album_data["albumname"]   = track_info["album"] 
                  album_data["artist"]      = track_info["artist"]
                  
                elif album_data["artist"] != track_info["artist"] and not "#error" in track_info["artist"]:
                  album_data["artist"]      = "Compilation"
                  album_data["compilation"] = True
                  
                elif not "#error" in track_info["artist"] and track_info["album"] == "":
                  album_data["album"]       = track_info["album"] 
                  album_data["albumname"]   = track_info["album"] 
                  album_data["artist"]      = track_info["artist"]
                                  
                album_data["tracks"].append(track_uuid)
                album_data["track_count"]  = track_count
                if "filesize" in track_info: album_data["albumsize"]   += float(track_info["filesize"])
                if "length" in track_info:   album_data["albumlength"] += float(track_info["length"])
                if "error" in track_info:    album_data["error"].append(track_info["error"]+" ("+track_info["file"]+")")              
                if "genre" in track_info and track_info["genre"] not in album_data["genre"]:
                   album_data["genre"].append(track_info["genre"])      
                if "cover_images" in track_info: 
                   if "dir" in track_info["cover_images"]:   album_data["cover_images"]["dir"].extend(track_info["cover_images"]["dir"])
                   if "track" in track_info["cover_images"]: album_data["cover_images"]["track"].extend(track_info["cover_images"]["track"])
                                
        if len(album_data["cover_images"]["dir"]) == 0 and len(album_data["cover_images"]["track"]) > 0:
           album_data["cover_images"]["active"] = "track"
        
        album_info[album_uuid] = album_data
        
        if album_data_error["artist"] != "":
           album_info[album_uuid+"_error"] = album_data_error
           
    for album_uuid in album_info:

       # sort tracks in album by key "sort"
       sorted_tracks = {}
       album_data    = album_info[album_uuid]
       for track_uuid in album_data["tracks"]:
          track = track_data[track_uuid]
          if "sort" not in track:                 track["sort"] = "00000"
          if track["sort"] not in sorted_tracks:  sorted_tracks[track["sort"]] = []
          sorted_tracks[track["sort"]].append(track_uuid)

       # add position of track to track data as "sort_pos"
       track_list_sorted = []
       track_list_pos    = 0
       for key in sorted(sorted_tracks.keys()):
         track_list_pos    += 1
         track_list_sorted.extend(sorted_tracks[key])       
         for track in sorted_tracks[key]:
            track_data[track]["sort_pos"] = track_list_pos

       album_info[album_uuid]["tracks"] = track_list_sorted.copy()
       
    return album_info, track_data


#------------------------------------

def reloadMusic(data, load_all=True, thread=""):
    '''
    load metadata and images from files in music_dir
    '''

    global music_dir, music_cover
    logging.info("reloadMusic: Start reloading music data: " + music_dir + " | all=" + str(load_all))
    
    keys_media  = mbox.databases["music"]
    data_reload = {}    
    for key in keys_media:
      data_reload[key] = {}
      
    media_files_exist  = data["files"].keys()
    media_files_reload = readFiles(music_dir)
    image_files_reload = readFiles(music_cover)

    if not load_all:
       data_reload = reloadMusic_getCurrentWithoutErrors(data_current=data)
       
    # reload files incl. metadata and images -> tracks and files
    files_amount     = len(media_files_reload)
    files_count      = 0
    files_percentage = 0

    logging.info("reloadMusic ... Starting (load_all="+str(load_all)+") - " + str(files_amount) + " files found.")
    
    for path2file in media_files_reload:

      if os.path.isfile(path2file) and checkIfSupported(thread.supported_mpX,path2file) == True:
         file_uuid         = str(uuid.uuid1())
         filename          = path2file.replace(music_dir,"")
         files_count      += 1
         reloadMusic_setProgessInfo(count=files_count, total=len(media_files_reload), thread=thread)
      
         if load_all or filename not in media_files_exist:
            data_reload["files"][filename]                    = readMetadata(music_dir+filename)
            data_reload["tracks"]["t_"+file_uuid]             = data_reload["files"][filename]
            data_reload["tracks"]["t_"+file_uuid]["uuid"]     = "t_"+file_uuid
            data_reload["files"][filename]["uuid"]            = "t_"+file_uuid
            
         else:
            file_data                                         = readMetadata(music_dir+filename)
            if "#error" in file_data["artist"]:
               data_reload["files"][filename]                 = file_data
               data_reload["tracks"]["t_"+file_uuid]          = data_reload["files"][filename]
               data_reload["tracks"]["t_"+file_uuid]["uuid"]  = "t_"+file_uuid
               data_reload["files"][filename]["uuid"]         = "t_"+file_uuid
         
    # ??? check, if file still exists (for load_all=True)

    # recreate album_infos based on tracks
    logging.info("reloadMusic: recreate album_infos based on tracks")
    data_reload["album_info"], data_reload["tracks"] = reloadMusic_createAlbumInfo(track_data=data_reload["tracks"])
    
    # recreate album hierachy based on album info
    logging.info("reloadMusic: recreate album hierachy")
    for album_uuid in data_reload["album_info"]:
       album_data = data_reload["album_info"][album_uuid]
        
       if album_data["artist"] not in data_reload["albums"]:                           data_reload["albums"][album_data["artist"]] = {}
       if album_data["albumname"] not in data_reload["albums"][album_data["artist"]]:  data_reload["albums"][album_data["artist"]][album_data["albumname"]] = {}
       data_reload["albums"][album_data["artist"]][album_data["albumname"]]["uuid"] = album_uuid
        
       for track_uuid in data_reload["album_info"][album_uuid]["tracks"]:
          data_reload["tracks"][track_uuid]["album_uuid"] = album_uuid
        
    # recreate list of artists    
    logging.info("reloadMusic: recreate list of artists")
    for track_uuid in data_reload["tracks"]:
       artist_name = data_reload["tracks"][track_uuid]["artist"]
       if not "#error" in artist_name:
          if not artist_name in data_reload["artists"]:              data_reload["artists"][artist_name] = {}
          if not track_uuid in data_reload["artists"][artist_name]:  data_reload["artists"][artist_name][track_uuid] = data_reload["tracks"][track_uuid]         
        
    # reconnect cards information
    if "cards" in data:
       logging.info("reloadMusic: reconnect cards information")
       cards_temp = data["cards"]
       for album_uuid in data_reload["album_info"]:
          cards_temp, card_id = checkIfCardExists(data_cards=cards_temp, album=data_reload["album_info"][album_uuid]["albumname"], artist=data_reload["album_info"][album_uuid]["artist"], uuid=album_uuid)
          data_reload["album_info"][album_uuid]["card_id"] = card_id          
       data_reload["cards"] = cards_temp

    # reconnect playlist information - albums based on uuid or directory, tracks based on filename and path
    if "playlists" in data:
       logging.info("reloadMusic: reconnect playlist information")
       for playlist_uuid in data["playlists"]:
          position = 0
          for entry_uuid in data["playlists"][playlist_uuid]["tracks"]:
             entry_ref  = data["playlists"][playlist_uuid]["tracks_ref"][position]
             check_uuid = checkIfPlaylistEntryExists(data_reload, entry_uuid=entry_uuid, entry_ref=entry_ref)
             if check_uuid != "NOT FOUND" and check_uuid != entry_uuid:
                data["playlists"][playlist_uuid]["tracks"][position] = check_uuid
             position += 1
       data_reload["playlists"] = data["playlists"]
    
    # delete old cover files, if all entries should be reloaded (and reload was successful)
    if load_all:
       logging.info("reloadMusic: delete old cover files")
       for x in image_files_reload:
         if os.path.isfile(x):
           os.remove(x)

    logging.info("reloadMusic: finished ... " + music_dir + " | all=" + str(all) + " | albums=" + str(len(data["albums"])))
    return data_reload

    
#---------------------------------------
# EOF
