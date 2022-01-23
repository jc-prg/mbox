#---------------------------------
# Manage Music Files
#---------------------------------

import modules.config_stage   as stage
import modules.config_mbox    as mbox
import modules.jcJson         as jcJSON
import modules.jcCouchDB      as jcCouch
import modules.jcRunCmd       as jcRunCmd
import modules.music_metadata as music_metadata

from modules.jcRunCmd import *

import os
import uuid
import logging
import threading
import time

#---------------------------------

load_logging = logging.getLogger("load")
load_logging.setLevel(stage.logging_level_data)

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

      self.logging = logging.getLogger("load")
      self.logging.setLevel(stage.logging_level)

   #------

   def run(self):
      '''control reload of music data'''

      self.logging.info( "Starting " + self.name )
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
            self.logging.info( "Starting Reload ALL" )

            self.store_data        = self.music_database.readGroup("music")
            self.store_data        = reloadMusic(self.store_data, True,  self)
            for key in self.store_data:
               self.music_database.write(key,self.store_data[key])

        # check if new files and load data for new files
        elif self.reload_new:
            self.logging.info( "Starting Reload NEW" )

            self.store_data      = self.music_database.readGroup("music")
            self.store_data      = reloadMusic(self.store_data, False,  self)
            for key in self.store_data:
               self.music_database.write(key,self.store_data[key])

        # check if new images in directories available
        elif self.reload_img:
            self.logging.info( "Starting Reload IMAGES" )

            self.store_data      = self.music_database.read("album_info")
            self.store_data      = reloadCoverImages(self.store_data, self)

            for key in self.store_data:
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

      self.logging.info( "Exiting " + self.name )


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
    load_logging.info("Read files: " + command)
    file_logging("----------------------------------------------")
    file_logging("Read files: " + command)
      
    list,error=jcRunCmd.runCmd(command)
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

    load_logging.info("Dont scan directories: "+str(noscan))
    file_logging("Dont scan directories: "+str(noscan))
    
    return files_return

#------------------------------------

def AlbumByPath(file):
    '''separate infos from path'''

    album     = ""
    localpath = file.replace(mbox.music_dir,"")
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

    load_logging.debug("checkIfPlaylistEntryExists : "+entry_uuid+" -> "+check_uuid)
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

    files            = readFiles(mbox.music_dir)
    files_amount     = len(files)
    files_count      = 0
    files_img_found  = 0
    files_percentage = 0
    
    load_logging.info("reloadCoverImages: Start to scan for new cover images ...")

    file_logging_init()
    file_logging(     "----------------------------------------------")
    file_logging(     "reloadCoverImages: Start to scan for new cover images ...")

    # remove old entries
    for key in data:
        data[key]["cover_images"]["dir"] = []

    # check list of files
    for filename in files:

       files_count      += 1
       if not os.path.isfile(filename):
          reloadMusic_setProgessInfo(count=files_count, total=files_amount, thread=thread, show=True)
          load_logging.debug("Check Images: "+filename.replace(stage.data_dir,""))
          file_logging(      "Check Images: "+filename.replace(stage.data_dir,""))

       # check if image file in folder (and take last one as alternative cover)
       if os.path.isfile(filename) and checkIfSupported(thread.supported_img,filename) == True:
       
          reloadMusic_setProgessInfo(count=files_count, total=files_amount, thread=thread, show=False)
          file_e = filename.replace("/","_")
          for key in data:
              #load_logging.debug(key+": "+data[key]["albumpath"])
              if data[key]["albumpath"] in file_e or data[key]["albumpath"] in filename:

                  files_img_found += 1
                  file_e2 = filename.replace(mbox.music_dir,"")
                  load_logging.debug(" . Found: "+filename.replace(mbox.music_dir,""))
                  file_logging(      " . Found: "+filename.replace(mbox.music_dir,""))
                  load_logging.debug(" . Found: "+key+" | "+data[key]["album"])
                  file_logging(      " . Found: "+key+" | "+data[key]["album"])
                  data[key]["cover_images"]["dir"].append(file_e2)
                  data[key]["cover_images"]["active"] = "dir"
    
    load_logging.info("reloadCoverImages: found "+str(files_img_found)+" files ("+str(files_count)+")")
    file_logging(     "reloadCoverImages: found "+str(files_img_found)+" files ("+str(files_count)+")")
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
    
    load_logging.info("Remove entries with errors for reload ...")
    file_logging(     "Remove entries with errors for reload ...")
    
    for key in data_keys:
       data_reload[key] = {}
    
    for x in data_current["albums"]:
       if "#error" in x:  logging_msg.append("albums: "+x)
       else:              data_reload["albums"][x] = data_current["albums"][x]
       
    for x in data_current["artists"]:
       if "#error" in x:  logging_msg.append("artists: "+x)
       else:              data_reload["artists"][x] = data_current["artists"][x]
       
    for x in data_current["files"]:
      if data_current["files"][x]["artist"] != None:
        if "#error" in data_current["files"][x]["artist"]:       logging_msg.append(" - files:      "+x)
        else:                                                    data_reload["files"][x] = data_current["files"][x]
       
    for x in data_current["tracks"]:
      if data_current["tracks"][x]["artist"] != None:
        if "#error" in data_current["tracks"][x]["artist"]:      logging_msg.append(" - tracks:     "+x)
        else:                                                    data_reload["tracks"][x] = data_current["tracks"][x]
       
    for x in data_current["album_info"]:
      if data_current["album_info"][x]["artist"] != None:
        if "#error" in data_current["album_info"][x]["artist"]:  logging_msg.append(" - album_info: "+x)
        else:                                                    data_reload["album_info"][x] = data_current["album_info"][x]
       
    for x in logging_msg:
       load_logging.debug(x)
       file_logging(x)
       
    return data_reload

#------------------------------------

def reloadMusic_setProgessInfo(count, total, thread, show=True):
    '''
    reload ... progress information
    '''
    if count == 0:
       return

    files_percentage  = float(count) / float(total) * 100
    if thread != "":
       thread.reload_progress      = files_percentage
       current_time                = time.time()
       thread.reload_time_required = time.time() - thread.reload_time_start
       thread.reload_time_left     = thread.reload_time_required * (100 - files_percentage) / files_percentage
       if files_percentage == 100: thread.reload_time_left = 0

    if show:
       load_logging.debug("Reload progress: "+str(files_percentage)+"%")
    
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

    load_logging.info("reloadMusic: Start reloading music data: " + mbox.music_dir + " | all=" + str(load_all))
    
    file_logging_init()
    file_logging(     "----------------------------------------------")
    file_logging(     "reloadMusic: Start reloading music data: " + mbox.music_dir + " | all=" + str(load_all))
    
    keys_media  = mbox.databases["music"]
    data_reload = {}    
    for key in keys_media:
      data_reload[key] = {}
      
    media_files_exist  = data["files"].keys()
    media_files_reload = readFiles(mbox.music_dir)
    image_files_reload = readFiles(mbox.music_cover)

    if not load_all:
       data_reload = reloadMusic_getCurrentWithoutErrors(data_current=data)
       
    # reload files incl. metadata and images -> tracks and files
    files_amount     = len(media_files_reload)
    files_count      = 0
    files_percentage = 0
    files_loaded     = 0
    
    load_logging.info("reloadMusic: Starting (load_all="+str(load_all)+") - " + str(files_amount) + " files found.")
    file_logging(     "reloadMusic: Starting (load_all="+str(load_all)+") - " + str(files_amount) + " files found.")
        
    for path2file in media_files_reload:
    
      if not os.path.isfile(path2file):
         load_logging.info("Read: "+path2file)
         file_logging(     "Read: "+path2file)
         reloadMusic_setProgessInfo(count=files_count, total=len(media_files_reload), thread=thread, show=True)

      elif os.path.isfile(path2file) and checkIfSupported(thread.supported_mpX,path2file) == True:
         file_uuid         = str(uuid.uuid1())
         filename          = path2file.replace(mbox.music_dir,"")
         files_count      += 1
         reloadMusic_setProgessInfo(count=files_count, total=len(media_files_reload), thread=thread, show=False)
         
         file_exist = (filename in media_files_exist)
         file_read  = (load_all or (not load_all and not file_exist))

         load_logging.debug(" . Check: read=" + str(file_read) + " | " + filename)
         file_logging(      " . Check: read=" + str(file_read) + " | " + filename)
      
         if file_read:
            files_loaded += 1
            
            data_reload["files"][filename]                    = music_metadata.readMetadata(mbox.music_dir+filename)
            data_reload["tracks"]["t_"+file_uuid]             = data_reload["files"][filename]
            data_reload["tracks"]["t_"+file_uuid]["uuid"]     = "t_"+file_uuid
            data_reload["files"][filename]["uuid"]            = "t_"+file_uuid
                     
    load_logging.info("reloadMusic: loaded data from "+str(files_loaded)+" files ("+str(len(media_files_reload))+")")
    file_logging(     "reloadMusic: loaded data from "+str(files_loaded)+" files ("+str(len(media_files_reload))+")")
    
    # recreate album_infos based on tracks
    load_logging.info("reloadMusic: recreate album_infos based on tracks")
    data_reload["album_info"], data_reload["tracks"] = reloadMusic_createAlbumInfo(track_data=data_reload["tracks"])
    
    # recreate album hierachy based on album info
    load_logging.info("reloadMusic: recreate album hierachy")
    for album_uuid in data_reload["album_info"]:
       album_data = data_reload["album_info"][album_uuid]
        
       if album_data["artist"] not in data_reload["albums"]:                           data_reload["albums"][album_data["artist"]] = {}
       if album_data["albumname"] not in data_reload["albums"][album_data["artist"]]:  data_reload["albums"][album_data["artist"]][album_data["albumname"]] = {}
       data_reload["albums"][album_data["artist"]][album_data["albumname"]]["uuid"] = album_uuid
        
       for track_uuid in data_reload["album_info"][album_uuid]["tracks"]:
          data_reload["tracks"][track_uuid]["album_uuid"] = album_uuid
        
    # recreate list of artists    
    load_logging.info("reloadMusic: recreate list of artists")
    for track_uuid in data_reload["tracks"]:
       artist_name = data_reload["tracks"][track_uuid]["artist"]
       if not "#error" in artist_name:
          if not artist_name in data_reload["artists"]:              data_reload["artists"][artist_name] = {}
          if not track_uuid in data_reload["artists"][artist_name]:  data_reload["artists"][artist_name][track_uuid] = data_reload["tracks"][track_uuid]         
        
    # reconnect cards information
    if "cards" in data:
       load_logging.info("reloadMusic: reconnect cards information")
       cards_temp = data["cards"]
       for album_uuid in data_reload["album_info"]:
          cards_temp, card_id = checkIfCardExists(data_cards=cards_temp, album=data_reload["album_info"][album_uuid]["albumname"], artist=data_reload["album_info"][album_uuid]["artist"], uuid=album_uuid)
          data_reload["album_info"][album_uuid]["card_id"] = card_id          
       data_reload["cards"] = cards_temp

    # reconnect playlist information - albums based on uuid or directory, tracks based on filename and path
    if "playlists" in data:
       load_logging.info("reloadMusic: reconnect playlist information")
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
       load_logging.info("reloadMusic: delete old cover files")
       for x in image_files_reload:
         if os.path.isfile(x):
           os.remove(x)

    load_logging.info("reloadMusic: finished ... " + mbox.music_dir + " | all=" + str(all) + " | albums=" + str(len(data["albums"])))
    file_logging(     "reloadMusic: finished ... " + mbox.music_dir + " | all=" + str(all) + " | albums=" + str(len(data["albums"])))
    return data_reload

    
#---------------------------------------
# EOF
