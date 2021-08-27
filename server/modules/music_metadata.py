#---------------------------------
# Get Metadata from Music Files
#---------------------------------

import os
import uuid
import logging
import hashlib

import eyed3
from mutagen.id3         import ID3
from mutagen.mp3         import MP3
from mutagen.mp4         import MP4, MP4Cover

import modules.config_mbox  as mbox

#------------------------------------

def fileHashMD5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

#------------------------------------

def setMetadataError(error, filename, error_msg="", decoder=""):
    '''
    create tags if an error occurred during file detection and metadata extraction
    '''
    temp      = filename.split("/")
    directory = filename.replace(temp[len(temp)-1], "")
    directory = directory.replace(mbox.music_dir, "")
    filename  = temp[len(temp)-1]
    
    tags = {}
    tags["uuid"]      = "t_"+str(uuid.uuid1())
    tags["file"]      = directory + filename
    tags["filesize"]  = 0
    tags["artist"]    = "#error: "+directory
    tags["album"]     = error
    tags["albumsize"] = 0
    tags["title"]     = filename + " (error: " + error + ")"
    tags["error"]     = error
    tags["sort"]      = "00000"+filename
    
    logging.warning(error + ": " + filename)
    if decoder != "":
       logging.warning("..."+decoder)
       tags["decoder"] = decoder
    if error_msg != "":
       logging.warning("..."+error_msg)
       tags["error"]  = error_msg
    return tags

#------------------------------------

def readMetadata(path_to_file):
    '''
    get metadata from music file, return as standardized dict
    '''

    tags     = {}
    temp     = path_to_file.split("/")
    filename = temp[len(temp)-1]

    # check if file is empty
    file_stats = os.stat(path_to_file)
    if file_stats.st_size == 0:
       tags = setMetadataError(error="empty file", filename=path_to_file)
       return tags

   # check file type and read metadata
    if   ".mp3" in filename.lower():  
       tags = readID3(path_to_file)
       if tags["filesize"] == 0:
          return tags
         
       #logging.info(tags)
       if "artist" not in tags and "album" not in tags:     tags  = readMutagen(path_to_file,"mp3")
       elif tags["artist"] == "" and tags["album"] == "":   tags  = readMutagen(path_to_file,"mp3")       

    elif ".m4a" in filename.lower():
      tags = readMutagen(path_to_file,"mp4")

    elif ".mp4" in filename.lower():
      tags = readMutagen(path_to_file,"mp4")

    else:
       tags = setMetadataError(error="file format not supported", filename=path_to_file)
       return tags

    if not "artist" in tags or tags["artist"] == "":  tags["artist"] = "Unknown Artist"
    if not "album"  in tags or tags["album"] == "":   tags["album"]  = "Unknown Album"
    if not "title"  in tags or tags["title"] == "":   tags["title"]  = filename

    if tags["album"] == "Unbekanntes Album":          tags["album"] = "Unknown Album"
    if tags["artist"] == "Unbekannte Künstler":       tags["album"] = "Unknown Artist"

    tags["MD5"] = fileHashMD5(path_to_file)

    if "track_no" in tags: del tags["track_no"]
    if "disc_no"  in tags: del tags["disc_no"]
    
    logging.debug(path_to_file + " MD5: " + tags["MD5"])   
    return tags


#------------------------------------

def readMutagen(filename,ftype="mp4"):

    relevant_tags = {}
    data          = {}

    if ftype == "mp4":
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
      if os.path.getsize(filename) > 0:
        try:
          tags = MP4(filename).tags
        except Exception as e:
          tags = setMetadataError(error="Not a correct MP4 file: ", filename=filename, error_msg=str(e), decoder="mutagen::"+ftype)
          return tags

      else:
        tags   = setMetadataError(error="empty file", filename=filename, decoder="mutagen::"+ftype)
        return tags
#
    elif ftype == "mp3":	         # https://en.wikipedia.org/wiki/ID3
      relevant_tags = {                  # https://mutagen.readthedocs.io/en/latest/api/id3.html
	"album"          : "TALB",
	"title"          : "TIT2",
	"genre"          : "TCON",
	"artist"         : "TPE1",
	"album artist"   : "TPE2",
	"composer"       : "TCOM",
	"length"         : "TLEN",
	"track_no"       : "TRCK",
	"disc_no"        : "TPOS",
	"album_no"       : "TSOA"
	}
      # img = "APIC"
      if os.path.getsize(filename) > 0:
        try:
          tags = ID3(filename) #.tags
        except Exception as e:
          tags = setMetadataError(error="Not a correct MP3 file", filename=filename, error_msg=str(e), decoder="mutagen::"+ftype)
          return tags
      else:
         tags  = setMetadataError(error="empty file", filename=filename, decoder="mutagen::"+ftype)
         return tags

    for r_tag in relevant_tags:
      for f_tag in tags:
        if relevant_tags[r_tag] in f_tag:
          value = tags[f_tag]
          data[r_tag] = value[0]

    if ftype == "mp3":
      try:
         data["length"]     = MP3(filename).info.length               
      except Exception as e:
         data               = setMetadataError(error="can't get file length", filename=filename, error_msg=str(e), decoder="mutagen::"+ftype)
         return data
      
    elif ftype == "mp4":
      try:
         data["length"]     = MP4(filename).info.length      
      except Exception as e:
         data               = setMetadataError(error="can't get file length", filename=filename, error_msg=str(e), decoder="mutagen::"+ftype)
         return data
      
    if ftype == "mp4" and "track_no" in data:
      track_no             = str(data["track_no"])
      track_no             = track_no.replace("(","")
      track_no             = track_no.replace(")","")
      data["track_num"]    = track_no.split(",")

    if ftype == "mp3" and "track_no" in data:
        if "/" in data["track_no"]:                      data["track_num"]    = data["track_no"].split("/")
        elif "," in data["track_no"]:                    data["track_num"]    = data["track_no"].split(",")
        else:                                            data["track_num"]    = [ data["track_no"] ]
        if "disc_no" in data and "/" in data["disc_no"]: data["disc_num"]     = data["disc_no"].split("/")[0]
        elif "disc_no" in data:                          data["disc_num"]     = data["disc_no"]

    data["file"]         = filename.replace(mbox.music_dir,"")
    data["uuid"]         = "t_"+str(uuid.uuid1())
    data["compliation"]  = 0
    data["filesize"]     = os.path.getsize(filename)
    data["cover_images"] = {}
    data["cover_images"]["track"] = []

    data["sort"] = 0
    if "track_num" in data and int(data["track_num"][0]) > 0: data["sort"] += int(data["track_num"][0])
    if "disc_num" in data and int(data["disc_num"]) > 0:      data["sort"] += int(data["disc_num"])*1000
    data["sort"] = str(data["sort"]).zfill(5)+data["file"]

    for tag in tags:    
      if "covr" in tag:
         data["cover_images"]["track"]  = [ writeImage(data["uuid"]+"_0",tags[tag]).replace(mbox.music_cover,"") ]
         data["cover_images"]["active"] = "track"

      if "APIC" in tag:
         data["cover_images"]["track"]  = [ writeImage(data["uuid"]+"_0",tags[tag]).replace(mbox.music_cover,"") ]
         data["cover_images"]["active"] = "track"

    data["decoder"] = "mutagen::"+ftype
    return data


#------------------------------------

def readID3(filename ,album_id="", album_nr=""):
    '''
    read data from mp3 file, for available tags see https://eyed3.readthedocs.io/en/latest/eyed3.id3.html?highlight=images#eyed3.id3.tag.Tag.images
    '''
    logging.debug("Read ID3: "+filename)
    found = True

    # load data from audio file
    audiofile  = eyed3.load(filename)
    albumdirs  = filename.split("/")
    albumdir   = albumdirs[len(albumdirs)-1]
    filesize   = os.path.getsize(filename)
    try:
      a = MP3( filename.encode('utf-8') )
      filelength = a.info.length
    except Exception as e:
      tags = setMetadataError(error="Not a correct MP3 file", filename=filename, error_msg=str(e), decoder="eyed3::mp3")
      return tags

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
        tags["track_total"]  = audiofile.tag.track_total
        tags["compliation"]  = 0
        tags["filesize"]     = filesize
        tags["length"]       = filelength

        try:
          tags["disc_num"]     = audiofile.tag.disc	     # disc number
          tabs["disc_total"]   = audiofile.tag.disc_total  # the total number of discs
          
        except Exception as e:
           logging.debug("No Disc Info: "+str(e))
        
        try:
          tags["genre"]        = str(audiofile.tag.genre)
          tags["genre"]        = tags["genre"] #.encode('utf-8')

        except Exception as e:
          tags["genre"]        = ""
          logging.debug("No Genre: "+str(e))

        tags["file"]         = filename.replace(mbox.music_dir,"")
        tags["uuid"]         = "t_"+str(uuid.uuid1())
        #tags["duration"]     = audiofile.tag.duration

        tags["sort"] = 0
        if "track_num" in tags and int(tags["track_num"]) > 0: tags["sort"] += int(tags["track_num"])
        if "disc_num" in tags and int(tags["disc_num"]) > 0:   tags["sort"] += int(tags["disc_num"])*1000
        tags["sort"] = str(tags["sort"]).zfill(5)+tags["file"]

        # check for images and write to file
        tags["cover_images"]           = {}
        tags["cover_images"]["track"]  = []

        if len(audiofile.tag.images) > 0:
           #tags["cover_image"]  = 1 #audiofile.tag.images
           images               = audiofile.tag.images
           count                = 0
           for IMAGE in images:
             count    += 1
             image_url = writeImage(tags["uuid"]+"_"+str(count),IMAGE.image_data).replace(mbox.music_cover,"")
             tags["cover_images"]["track"].append(image_url)
             tags["cover_images"]["active"] = "track"
             tags["cover_image"]            = 1

             logging.debug("## image ##" + image_url)
        else:
           tags["cover_image"]              = 0

      else:
        found = False

    # if no ID3 tags definied set to "" (required)
    except  Exception as e:
      logging.warning("Error reading ID3 tags: "+str(e))
      found = False

    if found == False:
      logging.info("test////" + filename)
      tags["artist"]       = ""
      tags["title"]        = filename.replace(mbox.music_dir,"")
      tags["album"]        = ""
      tags["album_artist"] = ""
      tags["track_num"]    = [0,0]
      tags["file"]         = filename.replace(mbox.music_dir,"")
      tags["uuid"]         = "t_"+str(uuid.uuid1())
      tags["compliation"]  = 0
      tags["filesize"]     = filesize
      tags["length"]       = filelength

    tags["decoder"] = "eyed3"
    return tags

#------------------------------------

def writeImage(name,idata):
    ''' write image data to file '''
    
    dtype = type(idata)
    if "id3.APIC" in str(dtype):      # <class 'mutagen.id3.APIC'>
      data = idata.data
    else:                             # byte object in array
      data = idata[0]

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
