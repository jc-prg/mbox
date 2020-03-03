#---------------------------------
# Get Metadata from Music Files
#---------------------------------

from modules.config_mbox import *
from mutagen.id3         import ID3
from mutagen.mp3         import MP3
from mutagen.mp4         import MP4, MP4Cover

import modules.config_mbox  as mbox

import eyed3
import os
import uuid
import logging

#------------------------------------

def readMetadata(path_to_file):
    '''
    get metadata from music file, return as standardized dict
    '''
    
    tags     = {}
    temp     = path_to_file.split("/")
    filename = temp[len(temp)-1]

    if   ".mp3" in filename.lower():  
       tags = readID3(path_to_file)
       if "artist" not in tags and "album" not in tags:   tags  = readMutagen(path_to_file,"mp3")
       if tags["artist"] == "" and tags["album"] == "":   tags  = readMutagen(path_to_file,"mp3")       
       
    elif ".m4a" in filename.lower():
      tags = readMutagen(path_to_file,"mp4")
      
    elif ".mp4" in filename.lower():
      tags = readMutagen(path_to_file,"mp4")
      
    else:
      tags["artist"] = "file format not supported"
      tags["album"]  = "file format not supported"
      tags["title"]  = filename

    if not "artist" in tags or tags["artist"] == "":  tags["artist"] = "Unknown Artist"
    if not "album"  in tags or tags["album"] == "":   tags["album"]  = "Unknown Album"
    if not "title"  in tags or tags["title"] == "":   tags["title"]  = filename
    
    if tags["album"] == "Unbekanntes Album":          tags["album"] = "Unknown Album"
    if tags["artist"] == "Unbekannte Künstler":       tags["album"] = "Unknown Artist"
    
    return tags, str(tags["artist"]), str(tags["album"]), str(tags["title"])
    

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
    
#------------------------------------
# EOF
