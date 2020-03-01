#---------------------------------
# Manage Music Files
#---------------------------------

import modules.config_stage  as stage
import modules.config_mbox   as mbox
import modules.jcJson        as jcJSON
import modules.jcCouchDB     as jcCouch

from modules.config_mbox import *
from modules.runcmd      import *
from mutagen.id3         import ID3
from mutagen.mp3         import MP3
from mutagen.mp4         import MP4, MP4Cover

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

def readMutagen(file,type="mp4"):

    global music_dir

    relevant_tags = {}
    data          = {}

    if type == "mp4":
      relevant_tags = {                  # https://mutagen.readthedocs.io/en/latest/api/mp4.html
	"album"          : "\xa9alb",
	"title"          : "\xa9nam",
	"genre"          : "\xa9gen",
	"artist"         : "\xa9ART",
	"album artist"   : "aART",
	"composer"       : "\xa9wrt",
        "disk_no"        : "disk",
	"track_no"       : "trkn"
	}
      # img = "covr"
      if os.path.getsize(file) > 0:
        try:
          tags = MP4(file).tags
        except Exception as e:
          logging.warn("Not an MP4 file"+file)
          logging.warn(str(e))
          tags          = {}
          data["error"] = str(e)
      else:
        logging.warn("File is empty: "+file)
        tags          = {}
        data["error"] = "File is empty"

    elif type == "mp3":
      relevant_tags = {                  # https://mutagen.readthedocs.io/en/latest/api/id3.html
	"album"          : "TALB",
	"title"          : "TIT2",
	"genre"          : "TCON",
	"artist"         : "TPE1",
	"album artist"   : "TPE2",
	"composer"       : "TCOM",
	"track_no"       : "TRCK"
	}
      # img = "APIC"
      if os.path.getsize(file) > 0:
        try:
          tags = ID3(file) #.tags
        except Exception as e:
          logging.warn("Not an MP3 file"+file)
          logging.warn(str(e))
          tags          = {}
          data["error"] = str(e)
      else:
        logging.warn("File is empty: "+file)
        tags          = {}
        data["error"] = "File is empty"

    for r_tag in relevant_tags:
      for f_tag in tags:
        if relevant_tags[r_tag] in f_tag:
          value = tags[f_tag]
          data[r_tag] = value[0]
#          logging.warn(str(data[r_tag]))
#        else:
#          data[r_tag] = ""
#    logging.warn(str(data))

    if type == "mp4" and "track_no" in data:
      track_no = str(data["track_no"])
      track_no = track_no.replace("(","")
      track_no = track_no.replace(")","")
      data["track_num"]    = track_no.split(",")
      data["length"]       = MP4(file).info.length

    if type == "mp3" and "track_no" in data:
      data["track_num"]    = data["track_no"].split(",")
      data["length"]       = MP3(file).info.length


    data["file"]         = file.replace(music_dir,"")
    data["uuid"]         = "t_"+str(uuid.uuid1())
    data["compliation"]  = 0
    data["filesize"]     = os.path.getsize(file)
    data["cover_images"] = {}
    data["cover_images"]["track"] = []

    ########################## problem bei umstellung auf python3 ###

    if "covr" in tags and len(tags["covr"]) > 0:
      data["cover_images"]["track"]  = [ writeImage(data["uuid"]+"_0",tags["covr"][0]).replace(music_cover,"") ]
      data["cover_images"]["active"] = "track"

    if "APIC" in tags and len(tags["APIC"]) > 0:
      data["cover_images"]["track"]  = [ writeImage(data["uuid"]+"_0",tags["APIC"][0]).replace(music_cover,"") ]
      data["cover_images"]["active"] = "track"

    return data


#------------------------------------

def readID3(file):
    ''' read data from mp3 file, for available tags see https://eyed3.readthedocs.io/en/latest/eyed3.id3.html?highlight=images#eyed3.id3.tag.Tag.images '''
    global music_dir

    logging.debug("Read ID3: "+file)
    found = True

    # load data from audio file
    audiofile  = eyed3.load(file)
    albumdirs  = file.split("/")
    albumdir   = albumdirs[len(albumdirs)-1]
    filesize   = os.path.getsize(file)
    try:
      a = MP3( file.encode('utf-8') )
      filelength = a.info.length
    except:
      filelength = 0

    # read tags from audio file
    tags = {}
    try:
      if audiofile.tag.title is not None:
        tags["artist"]       = audiofile.tag.artist  #.encode('utf-8')
        tags["title"]        = audiofile.tag.title   #.encode('utf-8')
        tags["album"]        = audiofile.tag.album
        tags["album_dir"]    = albumdir
        tags["album_artist"] = audiofile.tag.album_artist
        tags["track_num"]    = audiofile.tag.track_num
        tags["compliation"]  = 0
        tags["filesize"]     = filesize
        tags["length"]       = filelength

        try:
          tags["genre"]        = str(audiofile.tag.genre)
          tags["genre"]        = tags["genre"] #.encode('utf-8')

        except:
          tags["genre"]        = ""
          logging.debug("No Genre")

        tags["file"]         = file.replace(music_dir,"")
        tags["uuid"]         = "t_"+str(uuid.uuid1())
        #tags["duration"]     = audiofile.tag.duration

        # check for images and write to file
        tags["cover_images"]           = {}
        tags["cover_images"]["track"]  = []

        if len(audiofile.tag.images) > 0:
           #tags["cover_image"]  = 1 #audiofile.tag.images
           images               = audiofile.tag.images
           count                = 0
           for IMAGE in images:
             count    += 1
             image_url = writeImage(tags["uuid"]+"_"+str(count),IMAGE.image_data).replace(music_cover,"")
             tags["cover_images"]["track"].append(image_url)
             tags["cover_images"]["active"] = "track"
             tags["cover_image"]            = 1

             logging.warn("################# image ##" + image_url)
        else:
           tags["cover_image"]              = 0

      else:
        found = False

    # if no ID3 tags definied set to "" (required)
    except:
      found = False

    if found == False:
      logging.info("test////" + file)
      tags["artist"]       = ""
      tags["title"]        = file.replace(music_dir,"")
      tags["album"]        = ""
      tags["album_artist"] = ""
      tags["track_num"]    = [0,0]
      tags["file"]         = file.replace(music_dir,"")
      tags["uuid"]         = "t_"+str(uuid.uuid1())
      tags["compliation"]  = 0
      tags["filesize"]     = filesize
      tags["length"]       = filelength

    if filesize == 0:
      tags["error"] = "File is empty (ID3)."

    return tags

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

    for key in data_cards:
      if "," in data_cards[key]:
        if data_cards[key][1] == album and data_cards[key][2] == artist:
          data_cards[key][0] = uuid
          return data_cards, key

    return data_cards, ""


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

def reloadMusic(data,all=True,thread=""):
    '''load metadata and images from files in music_dir'''

    global music_dir, music_cover

    data_album_list = {} # albums
    data_album_info = {} # album infos
    data_tracks     = {} # tracks
    data_files      = {} # files
    data_artists    = {} # files
    data_i          = {} # album infos - collect
    data_h          = {} # temporary dict to add image files to album
    
    a_uuid          = ""
    files_exist     = data["files"]
    
    logging.info("Start reloading music data: " + music_dir + " | all=" + str(all))

    # delete old cover files (as not required after reload)
    if all:                                                 # if all files / db entries should be reloaded (else: add only new entries)
      files = readFiles(music_cover)
      for x in files:
        if os.path.isfile(x):
          os.remove(x)

    # if not all, copy existing entries to vars
    else:
      data_album_list = data["albums"]      # data_a
      data_album_info = data["album_info"]  # data_e
      data_tracks     = data["tracks"]      # data_t
      data_files      = data["files"]       # data_f
      data_artists    = data["artists"]     # data_k

    # read all file names in music dir and start loop to read ID3 tags
    files            = readFiles(music_dir)
    files_amount     = len(files)
    files_count      = 0
    files_percentage = 0

    last_artist      = ""
    last_album       = ""
    last_title       = ""
    last_albumdir    = ""

    logging.info("... renew all: " + str(files_amount) + " files found.")

    for file in files:

      # check if entry for file already exists in db
      m_file            = file.replace(music_dir,"")

      # calculate and show progress
      files_count      += 1
      files_percentage  = float(files_count) / float(files_amount) * 100
      if thread != "":
          thread.reload_progress      = files_percentage
          current_time                = time.time()
          thread.reload_time_required = time.time() - thread.reload_time_start
          thread.reload_time_left     = thread.reload_time_required * (100 - files_percentage) / files_percentage

      logging.debug("Reload progress: "+str(files_percentage)+"%")

      # check if file alread loaded and if all files should be loaded
      if (m_file not in files_exist) or all:
        logging.debug("NOT EXIST_or_ALL: " + str(all))

        # generate album identifier based on path to file
        albumID3  = ""
        albumPath = AlbumByPath(file)
        if (albumPath not in data_h):
          data_h[albumPath] = {}

        #logging.info("XXX" + file)

        # check if image file in folder (and take last one as alternative cover)
        if os.path.isfile(file) and checkIfSupported(thread.supported_img,file) == True:

            data_h[albumPath]["cover_image"] = file.replace(music_dir,"")
            if "cover_images" not in data_h[albumPath]: data_h[albumPath]["cover_images"] = {}
            if "dir" not in data_h[albumPath]["cover_images"]: data_h[albumPath]["cover_images"]["dir"] = []
            data_h[albumPath]["cover_images"]["dir"].append( file.replace(music_dir,"") )


        # check if mp3 and read data from ID3 tags
        if os.path.isfile(file) and checkIfSupported(thread.supported_mpX,file) == True:

          tags     = {}
          tag1     = ""
          tag2     = ""
          tag3     = ""
          tag4     = albumPath
          check    = True

          #if ((".mp4" in file) or (".m4a" in file) or (".M4A" in file) or (".MP4" in file)):
          if checkIfSupported(thread.supported_mp4,file) == True:

             tags     = readMutagen(file,"mp4")
             #logging.info("XXXYYYZZZ" + file)
             #logging.warn(str(tags))

          #elif ((".mp3" in file) or (".MP3" in file)):
          elif checkIfSupported(thread.supported_mp3,file) == True:

             tags     = readID3(file)

             if "artist" not in tags and "album" not in tags:
                tags  = readMutagen(file,"mp3")

             if tags["artist"] == "" and tags["album"] == "":
                tags  = readMutagen(file,"mp3")

          else:
             tag1 = "file format not supported"
             tag2 = "file format not supported"
             tag3 = tags["file"]

          try:      logging.info("----" + str(tags["album"]) + " / " + str(tags["artist"]))
          except:   logging.info("----ERROR")

          if check: #tag1 != "file format not supported":

             if "artist" in tags: tag1     = tags["artist"]
             if "album"  in tags: tag2     = tags["album"]
             if "title"  in tags: tag3     = tags["title"]

             # if no ID3 tags available set to "" // python 3
             if not isinstance( tag1, str ): tag1 = ""
             if not isinstance( tag2, str ): tag2 = ""
             if not isinstance( tag3, str ): tag3 = ""

             # if no data set to unknown
             if tag1 == "":
                tag1 = "Unknown Artist"
                tags["artist"] = tag1

             if tag2 == "":
                tag2 = "Unknown Album"
                tags["album"] = tag2

             if tag3 == "":
                temp1 = file.replace(music_dir,"")
                temp2 = temp1.split("/")
                tag3  = temp2[len(temp2)-1]
                tags["title"] = tag3

             # if German ...
             if tag2 == "Unbekanntes Album": tag2 = "Unknown Album"


          # check if it's a compilation
          tag1_org = tag1
          if (tag1 != last_artist) and (tag4 == last_albumdir) and (tag1 != "file format not supported"):
             logging.debug("ALBUM DIR (COMPILATION): " + tag4)
             tags["compilation"] = 1
             tag1                = "Compilation"

             # correct hierachy
             if last_artist != tag1:
               if tag1 not in data_album_list:              data_album_list[tag1]             = {}      # create category compilations
               if last_album not in data_album_list[tag1]:  data_album_list[tag1][last_album] = {}      # create album in category

               data_album_list[tag1][last_album]            = data_album_list[last_artist][last_album]  # move last entry to group "Compilation"
               del data_album_list[last_artist][last_album]                                             # remove entry with artist name

             # correct other
             if last_artist != tag1:
               lst_albumID3 = last_artist+"_"+tag2
               act_albumID3 = tag1+"_"+tag2

               if lst_albumID3 in data_i: data_i[act_albumID3] = data_i[lst_albumID3]                   # move track list from first song to compilation
               if lst_albumID3 in data_i: data_i[act_albumID3+"_tags"] = data_i[lst_albumID3+"_tags"]   # move track list from first song to compilation
               if lst_albumID3 in data_h: data_h[act_albumID3] = data_h[lst_albumID3]                   # move albumPath from first song to compilation

               if lst_albumID3 in data_h: del data_h[lst_albumID3]                                      # delete albumPath for first song
               if lst_albumID3 in data_i: del data_i[lst_albumID3]                                      # delete list of tracks for first song

          else:
             logging.debug("ALBUM DIR: " + tag4)

          # set last vars to check next file if part of compilation (different artists per album)
          last_artist   = tag1
          last_album    = tag2
          last_title    = tag3
          last_albumdir = tag4

          # get basic album information - artist, album, cover image
          # ----------------------------------------------------
          # generate temporary identifier (to mach image files to albums)
          albumID3         = tag1+"_"+tag2
          data_h[albumID3] = data_h[albumPath]

          ###################################### uebergeben von tags fuer das Album -> MISSING: tags[cover_images];tags[cover_image] ...

          # check if embedded images from audiofiles
          if "cover_images" in tags:

            if not albumID3+"_image" in data_i:
              data_i[albumID3+"_image"]            = {}
              data_i[albumID3+"_image"]            = tags["cover_images"]
              data_i[albumID3+"_image"]["active"]  = "track"

            else:
              for img in tags["cover_images"]["track"]:
                 data_i[albumID3+"_image"]["track"].append(img)

          data_i[albumID3] = [tag1,tag2,tag4] # simplification - assumption files of an album will never be stored in different directories (tag4)

          # create list of tracks
          if albumID3+"_tags" in data_i: # exist
             data_i[albumID3+"_tags"].append(tags["uuid"])
          else:                          # is empty
             data_i[albumID3+"_tags"] = {}
             data_i[albumID3+"_tags"] = [tags["uuid"]]

          # safe title and filename in dict
          data_tracks[tags["uuid"]] = tags
          data_files[tags["file"]]  = tags

          # create hierarchy: artist - track
          if tag1_org not in data_artists:        data_artists[tag1_org]         = {}
          if tag3 not in data_artists[tag1_org]:  data_artists[tag1_org][tag3]   = {}

          data_artists[tag1_org][tag3] = tags

          # create hierarchy: artist - album - track
          if tag1 not in data_album_list:          data_album_list[tag1]         = {}
          if tag2 not in data_album_list[tag1]:    data_album_list[tag1][tag2]   = {}


    # create list of albums by UUID based on track infos -> album_info
    for key in data_i:
       a_uuid = "a_"+str(uuid.uuid1())
       if key+"_tags" in data_i:
         if data_i[key][1] not in data_album_list[data_i[key][0]]: data_album_list[data_i[key][0]][data_i[key][1]] = {}

         data_album_list[data_i[key][0]][data_i[key][1]]["uuid"] = a_uuid  # KeyError 'Unknown Album'
         data_album_info[a_uuid]                  = {}
         data_album_info[a_uuid]["artist"]        = data_i[key][0]
         data_album_info[a_uuid]["album"]         = data_i[key][1]
         data_album_info[a_uuid]["tracks"]        = data_i[key+"_tags"]
         data_album_info[a_uuid]["track_count"]   = len(data_i[key+"_tags"])
         data_album_info[a_uuid]["albumpath"]     = data_i[key][2]
         data_album_info[a_uuid]["albumsize"]     = 0
         data_album_info[a_uuid]["albumlength"]   = 0
         data_album_info[a_uuid]["genres"]        = []
         data_album_info[a_uuid]["error"]         = []

         data_album_info[a_uuid]["cover_images"]          = {}
         data_album_info[a_uuid]["cover_images"]["dir"]   = []
         data_album_info[a_uuid]["cover_images"]["track"] = []

         # consolidate data from tracks
         for t_key in data_album_info[a_uuid]["tracks"]:

           # calculate album size in bytes
           data_album_info[a_uuid]["albumsize"]       = data_album_info[a_uuid]["albumsize"]   + data_tracks[t_key]["filesize"]
           if "length" in data_tracks[t_key]: 
             data_album_info[a_uuid]["albumlength"]   = data_album_info[a_uuid]["albumlength"] + data_tracks[t_key]["length"]

           # collect genre information from tracks
           if "genre" in data_tracks[t_key]:
             if data_tracks[t_key]["genre"] and not data_tracks[t_key]["genre"] in data_album_info[a_uuid]["genres"]:
               data_album_info[a_uuid]["genres"].append(data_tracks[t_key]["genre"])
           data_tracks[t_key]["uuid_album"] = a_uuid

           # error message from tracks
           if "error" in data_tracks[t_key]:
             data_album_info[a_uuid]["error"].append(data_tracks[t_key]["error"] + " ("+data_tracks[t_key]["file"]+")")
           data_tracks[t_key]["uuid_album"] = a_uuid


         # check if already a rfid card is connected
         data["cards"], data_album_info[a_uuid]["card_id"] = checkIfCardExists(data["cards"],data_album_info[a_uuid]["album"],data_album_info[a_uuid]["artist"],a_uuid)

         # set image information for album
         if key+"_image" in data_i:
             data_album_info[a_uuid]["cover_images"]         = data_i[key+"_image"] # images extracted from audio file

         if "cover_images" in data_h[key]:
             data_album_info[a_uuid]["cover_images"]["dir"]  = data_h[key]["cover_images"]["dir"] # images from directory
             if len(data_album_info[a_uuid]["cover_images"]["track"]) == 0: data_album_info[a_uuid]["cover_images"]["active"] = "dir"
         else:
             data_album_info[a_uuid]["cover_images"]["dir"]  = []

         if len(data_album_info[a_uuid]["cover_images"]["track"]) == 0 and len(data_album_info[a_uuid]["cover_images"]["dir"]) == 0:
             data_album_info[a_uuid]["cover_images"]["active"] = "none"


    data["albums"]      = data_album_list
    data["tracks"]      = data_tracks
    data["files"]       = data_files
    data["artists"]     = data_artists

    if all:
      data["album_info"]  = data_album_info        # replace all albums

    else:
      for x in data_album_info:
        data["album_info"][x] = data_album_info[x] # add not existing albums

    if "playlists" not in data:   data["playlists"] = {}
    if "cards" not in data:       data["cards"]     = {}
      
    logging.info("Finished reloading music data: " + music_dir + " | all=" + str(all) + " | albums=" + str(len(data["albums"])))

    return data

#------------------------------------

def writeImage(name,data):
    ''' write image data to file '''
 
    filename = mbox.music_cover + name + ".jpg"
    file = open(filename,"wb")
    file.write(data)
    file.close()
    return filename


def writeImageMP4(uuid, target_file):
    ''' write image data from mp4-file to file '''

    filename = mbox.music_cover + uuid + ".jpg"
    return filename
