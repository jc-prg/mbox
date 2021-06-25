import logging
import uuid
import urllib.parse
from os import path

import modules.config_stage   as stage
import modules.config_mbox    as mbox
import modules.jcJson         as jcJSON
import modules.jcCouchDB      as jcCouch
import modules.music_load     as music_load
import modules.music_control  as music_ctrl
import modules.stream_control as radio_ctrl
import modules.speakmsg       as speak

from modules.runcmd           import *
from modules.music_podcast    import *
from modules_api.server_init  import *

#-------------------------------------------------

if stage.test:
    if mbox.DEBUG: logging.basicConfig(level=logging.DEBUG)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    else:          logging.basicConfig(level=logging.INFO)   # DEBUG, INFO, WARNING, ERROR, CRITICAL
else:              logging.basicConfig(level=logging.WARN)   # DEBUG, INFO, WARNING, ERROR, CRITICAL

#-------------------------------------------------

def diskSpace(init=False):

    out = mbox.checkdisk

    if stage.mount_data != "" and stage.mount_system != stage.mount_data:

        out[0], err = runCmd(mbox.diskuse  + stage.mount_data)
        try:                   out[0] = float(out[0].split("\t")[0])
        except Exception as e: logging.warn("Error in reading disk spaces (data drive) ..." + str(e))

        out[1], err = runCmd(mbox.diskfree + stage.mount_data)
        try:                   out[1] = float(out[1].split("\n")[1])
        except Exception as e: logging.warn("Error in reading disk spaces (data drive) ..." + str(e))
  

    if stage.mount_system != "":

        if init: 
            out[2], err = runCmd(mbox.diskuse  + stage.mount_system)
            try:                   out[2] = float(out[2].split("\t")[0])
            except Exception as e: logging.warn("Error in reading disk spaces (system drive) ..." + str(e))

        out[3], err = runCmd(mbox.diskfree + stage.mount_system)
        try:                   out[3] = float(out[3].split("\n")[1])
        except Exception as e: logging.warn("Error in reading disk spaces (system drive) ..." + str(e))

    if init: 
        mbox.checkdisk = out

    return out

#-------------------------------------------------

def connectionStatus():
    '''
    read log files with connection status
    '''
    
    try:
      with open(mbox.log_connection) as f:
              content1 = f.readlines()
    except:   content1 = [ "Connection not checked yet" ]

    try:
      with open(mbox.log_autohotspot) as f:
              content2 = f.readlines()
    except:   content2 = [ "Autohotspot not activated" ]
      
    return { "CONNECT" : content1[0], "TYPE" : content2[0] }

#-------------------------------------------------
# NEXT GEN: generic class start and end
#-------------------------------------------------

def mboxAPI_error(data,error):
    if "error" in data["REQUEST"]:   data["REQUEST"]["error"] += ", "+error
    else:                            data["REQUEST"]["error"] = error
    logging.info("mBox " + data["REQUEST"]["c-name"] + " ERROR:" + error)
    return data

# ---

def mboxAPI_filter(data,db_filter=""):
    if "db_filter" in data["REQUEST"] and db_filter:   data["REQUEST"]["db_filter"] += "||"+db_filter
    elif db_filter:	                               data["REQUEST"]["db_filter"] = db_filter
    return data

#-------------------------------------------------
# NEXT GEN: generic class start and end
#-------------------------------------------------

def mboxAPI_start(cName, cmd1, cmd2, param1, param2):

    logging.debug("mBox " + cName + " START ...")
    checkDevice()

    data                            = {}
    data                            = dataInit()
    data["REQUEST"]                 = {}
    data["REQUEST"]["status"]       = "success"
    data["REQUEST"]["command"]      = "mBox " + cName + ": " + str(cmd1) + ":"  + str(cmd2) + " / " + str(param1) + ":" + str(param2)
    data["REQUEST"]["c-name"]       = cName
    data["REQUEST"]["c-param"]      = str(param1) + " " + str(param2)
    data["REQUEST"]["start-time"]   = time.time()

    data["STATUS"]                  = {}
    data["DATA"]                    = {}
    data["DATA"]["SHORT"]           = {}

    data["LOAD"]                    = {}
    data["LOAD"]["UUID"]            = ""
    data["LOAD"]["RFID"]            = ""
    
    if "cardUID"  in mbox.rfid_ctrl: data["LOAD"]["RFID"]    = mbox.rfid_ctrl["cardUID"]
    if "buttonID" in mbox.rfid_ctrl: data["LOAD"]["BUTTON"]  = mbox.rfid_ctrl["buttonID"]
    if "_" in str(param1):           data["LOAD"]["UUID"]    = param1

    return data

# ---

def mboxAPI_end(data,reduce_data=[]):

    data["REQUEST"]["load-time"] = time.time() - data["REQUEST"]["start-time"]

    out = diskSpace()

    data["STATUS"]["active_device"] = mbox.active_device

    if not "no-playback" in reduce_data:
      data["STATUS"]["playback"]    = deviceStatus()
    
    if not "no-system" in reduce_data:
      data["STATUS"]["system"]        = {
        "space_usb_used"        :  out[0],
        "space_usb_available"   :  out[1],
        "space_usb_mount"       :  stage.mount_data,
        "space_main_used"       :  out[2],
        "space_main_available"  :  out[3],
        "space_main_mount"      :  stage.mount_system,
        "server_start"          :  mbox.start_time,
        "server_start_duration" :  mbox.start_duration,
        "server_running"        :  time.time() - mbox.start_time,
        "server_connection"     :  connectionStatus()
        }
    data["STATUS"]["load_data"]     = {
        "reload_new"            : thread_music_load.reload_new,
        "reload_all"            : thread_music_load.reload_all,
        "reload_progress"       : thread_music_load.reload_progress,
        "reload_time_left"      : thread_music_load.reload_time_left
        }

    if not "no-statistic" in reduce_data:
      data["STATUS"]["statistic"] = {}       
      for database in couch.database:
        temp = couch.read_cache(database)
        try:
          data["STATUS"]["statistic"][database] = len(temp.keys())
        except:
          data["STATUS"]["statistic"][database] = "error"
          
    if "no-request" in reduce_data: del data["REQUEST"]
    if "no-load"    in reduce_data: del data["LOAD"]
    if "no-api"     in reduce_data: del data["API"]

    logging.debug("mBox " + data["REQUEST"]["c-name"]  + " END")

    return data

#-------------------------------------------------
# NEXT GEN: DATA functions
#-------------------------------------------------

def mboxDATA_checkActiveCard(data):
       '''
       check if card already is connected, otherwise return signal and list of available items ...
       '''
       
       if data["LOAD"]["RFID"] == "": return data
       else:                          card = data["LOAD"]["RFID"]
       
       cards   = couch.read_cache("cards")
       if card not in cards:
          data["LOAD"]["CARD"] = "unknown"
          db_list = ["album_info","playlists","radio"]
          for db in db_list:
             temp_db = couch.read_cache(db)
             data["DATA"]["SHORT"][db] = {}
             for entry in temp_db:
                if "title" in temp_db[entry]:   data["DATA"]["SHORT"][db][entry] = temp_db[entry]["title"]
                elif "album" in temp_db[entry]: data["DATA"]["SHORT"][db][entry] = temp_db[entry]["album"] + " (" + temp_db[entry]["artist"] +")"
       else:
          data["LOAD"]["CARD"] = "known"
       
       return data
          
          
#-------------------------------------------------
# NEXT GEN: Maintain server / database
#-------------------------------------------------

def mboxAPI_testUUID(database,uuid):
       '''if uuid is "test", get uuid from first dataset in database'''
       
       global couch
       if ("test" in uuid):
          temp = couch.read_cache(database)
          for key in temp:
            uuid = key
            break
       return (uuid)

# ---

def mboxAPI_status():
       '''return system and playback status'''

       data = mboxAPI_start("status","status","","","")
       data = mboxDATA_checkActiveCard(data)
       data = mboxAPI_end(data)
       return (data)

# ---

def mboxAPI_setCard(cardUID):
       '''set card UID by microservice to central var'''

       param = cardUID
       data  = mboxAPI_start("setCard","setCard","",param,"")

       if param == "no_card" or param == "-": mbox.rfid_ctrl["cardUID"] = ""
       else:                                  mbox.rfid_ctrl["cardUID"] = param

       data = mboxAPI_end(data)
       return(data)

# ---

def mboxAPI_speak(message):
       '''set card UID by microservice to central var'''

       data  = mboxAPI_start("speak","speak","",message,"")

       thread_speak.speak_message(message)

       data = mboxAPI_end(data)
       return(data)
       
# ---

def mboxAPI_setButton(buttonID):
       '''set button ID by microservice to central var'''

       param = buttonID
       data  = mboxAPI_start("setButton","setButton","",param,"")

       if param == "no_button": mbox.rfid_ctrl["buttonID"] = ""
       else:                    mbox.rfid_ctrl["buttonID"] = param

       if   mbox.active_device == "music_box" and param == "next":    thread_playlist_ctrl.playlist_next(1)
       elif mbox.active_device == "music_box" and param == "back":    thread_playlist_ctrl.playlist_next(-1)
       elif mbox.active_device == "music_box" and param == "pause":   thread_playlist_ctrl.player.pause()

       data = mboxAPI_end(data)
       return(data)

# ---

def mboxAPI_backup(param):
       '''create or restore backup for couchDB'''
       
       global couch
       data = mboxAPI_start("backup","backup","",param,"")

       if param == "json2db":    couch.restoreFromJson()
       elif param == "db2json":  couch.backupToJson()
       else:                     data = mboxAPI_error(data,"Parameter is not supported.")

       data = mboxAPI_end(data)
       return(data)

# ---

def mboxAPI_load(param):
       '''reload metadata from music files or images'''
       
       global couch
       data = mboxAPI_start("load","load","",param,"")

       if   param == "new":     thread_music_load.reload_new = True
       elif param == "all":     thread_music_load.reload_all = True
       elif param == "images":  thread_music_load.reload_img = True
       else:                    data = mboxAPI_error(data,"Parameter is not supported.")

       data = mboxAPI_end(data)
       return(data)

# ---

def mboxAPI_checkVersion(APPversion):
       '''check if APP version is supported by server'''
       
       global couch
       param = mbox.APPversion
       data  = mboxAPI_start("checkVersion","checkVersion","",param,"")

       if (APPversion == mbox.APPversion):    result    = ErrorMsg("800")
       elif (APPversion in mbox.APPsupport):  result    = ErrorMsg("801")
       else:                                  result    = ErrorMsg("802")

       data["STATUS"]["check-version"] = result

       data = mboxAPI_end(data,["no-statistic","no-playback","no-system"])
       return(data)


#-------------------------------------------------
# NEXT GEN: Read data from database
#-------------------------------------------------

def mboxAPI_readDB(databases,db_filter=""):

       global couch
       param     = databases

       if ">>" in db_filter:  thefilter = db_filter.split(">>")
       else:                  thefilter = db_filter.split("||")

       try:
         uuid = thefilter[1]
       except:
         uuid = ""

       if databases == "all":       db_list = ["files","tracks","albums","album_info","cards","playlists","radio","artists"]
       elif "--" in databases:      db_list = databases.split("--")
       elif databases == "artists": db_list = ["albums","album_info","artists"]
       else:                        db_list = [databases]

       data    = mboxAPI_start("readDB","readDB","",param,"")

       # read complete databases
       for database in db_list:
         if database in couch.database:
           if "main" in couch.database[database]: data["DATA"][database] = couch.read_cache(database)
           else:                                  data = mboxAPI_error(data, "Database empty: "+database)
         else:
           data = mboxAPI_error(data, "Database not found: "+database)

         if uuid != "" and uuid in data["DATA"][database]:
             data["DATA"]["_selected_uuid"]        = uuid
             data["DATA"]["_selected_db"]          = database
             data["DATA"]["_selected"]             = data["DATA"][database][uuid]
             
       # TEMP ... read podcast ...       
       if databases == "radio":
          for stream_uuid in data["DATA"]["radio"]:
             stream_url = data["DATA"]["radio"][stream_uuid]["stream_url"]
             if stream_url.endswith(".rss") or stream_url.endswith(".xml") or stream_url.endswith(".podcast"):   
                podcast = thread_podcast.get_podcasts(playlist_uuid=stream_uuid)
                data["DATA"]["radio"][stream_uuid]["podcast"]        = podcast
                           
       
       # create combined requests - ARTISTS
       
       #.... check for errors!
       if databases == "artists":
          artists = {}
          for key in data["DATA"]["album_info"]:
             album_info     = data["DATA"]["album_info"][key]
             artist         = album_info["artist"] 
             album          = {}
             album["album"] = album_info["albumname"] 
             album["uuid"]  = key 
            
             if not "#error" in artist:
               if not artist in artists: artists[artist] = []
               artists[artist].append( album )
            
          data["DATA"]["artists"] = artists
          del data["DATA"]["album_info"]
          del data["DATA"]["albums"]

       data = mboxAPI_filter(data,db_filter)
       data = mboxAPI_end(data,["no-statistic","no-playback","no-system"])
       return(data)

# ---

def mboxAPI_readEntry(uuid,db_filter=""):

       global couch

       # identify database
       if   "a_" in uuid: database = "album_info"
       elif "t_" in uuid: database = "tracks"
       elif "r_" in uuid: database = "radio"
       elif "p_" in uuid: database = "playlists"
       elif "/"  in uuid: database = "files"
       elif ","  in uuid: database = "cards"
       else:              database = ""

       param  = database
       param2 = uuid
       uuid   = mboxAPI_testUUID(database,uuid)
       data   = mboxAPI_start("readEntry","readEntry","",param,param2)
       

       # read entry from database
       if database in couch.database:
           temp_tracks = couch.read_cache("tracks")
           temp_albums = couch.read_cache("album_info")

           if "main" in couch.database[database]:
               temp = couch.read_cache(database)

               if uuid in temp:
                   if uuid.startswith("r_"): 
                      temp[uuid]["podcast"] = thread_podcast.get_podcasts(playlist_uuid=uuid)
                   
                   data["DATA"]["_selected_uuid"]            = uuid
                   data["DATA"]["_selected_db"]              = database
                   
                   # check if rfid card (array instead of dict)
                   if not isinstance(temp[uuid],list):
                      data["DATA"]["_selected"]              = temp[uuid]
                   else:
                      data["DATA"]["_selected"]              = {}
                      data["DATA"]["_selected"]["card_info"] = temp[uuid]
                   
                   if not "tracks" in data["DATA"]["_selected"]:
                      data["DATA"]["_selected"]["tracks"]   = {}

                   if "tracks" in temp[uuid]:
                      if not "tracks"     in data["DATA"]: data["DATA"]["tracks"]     = {}
                      if not "album_info" in data["DATA"]: data["DATA"]["album_info"] = {}
                      for key in temp[uuid]["tracks"]:
                          logging.info(key)
                          # if track add track info
                          if key in temp_tracks: data["DATA"]["tracks"][key]     = temp_tracks[key]
                          # if album add album info and track infos
                          if key in temp_albums: 
                             data["DATA"]["album_info"][key] = temp_albums[key]
                             for key_track in temp_albums[key]["tracks"]:
                                data["DATA"]["tracks"][key_track]  = temp_tracks[key_track]

                   if not "uuid" in data["DATA"]["_selected"]:
                      data["DATA"]["_selected"]["uuid"] = uuid
               else:
                   data = mboxAPI_error(data, "Entry not in database: " + uuid)
           else:
               data = mboxAPI_error(data, "Database empty: "+database)
       else:
           data = mboxAPI_error(data, "Database not found: "+database)

       data = mboxAPI_filter(data,db_filter)
       data = mboxAPI_end(data,["no-statistic","no-playback","no-system"])
       return(data)


#-------------------------------------------------
# NEXT GEN: class to edit data using CouchDB
#-------------------------------------------------

def mboxAPI_edit(uuid,entry_data):

       global couch
       database   = ""
       databases  = ["files","tracks","albums","album_info","cards","playlists","radio","artists"]
       db_entries = {}
       data       = mboxAPI_start("edit","edit","",uuid,"")

       # read all data from DB
       for name in databases: db_entries[name] = couch.read(name)

       # identify database
       if   "a_" in uuid: database = "album_info"
       elif "t_" in uuid: database = "tracks"
       elif "r_" in uuid: database = "radio"
       elif "p_" in uuid: database = "playlists"
       else: data = mboxAPI_error(data, "UUID format not supported: "+uuid)

       # edit specific values in selected entry
       if uuid in db_entries[database]:
         entry = db_entries[database][uuid]
         for key in entry_data:
           if key in entry:
             entry[key] = entry_data[key]
         db_entries[database][uuid] = entry

       else:
         data = mboxAPI_error(data, "UUID not found: "+uuid +"/"+database)

       # write change data to DB
       for name in databases: couch.write(name, db_entries[name])

       data = mboxAPI_end(data,["no-statistic","no-playback","no-system"])
       return(data)

# ---

def mboxAPI_delete(uuid):

       global couch
       database          = ""
       databases         = ["files","tracks","albums","album_info","cards","playlists","radio","artists"]
       databases_changed = []
       db_entries        = {}
       data              = mboxAPI_start("delete","delete","",uuid,"")

       # read all data from DB
       for name in databases: db_entries[name] = couch.read_cache(name)

       # delete album, tracks, files, link to card
       if "a_" in uuid:
           database          = "album_info"
           if uuid in db_entries[database]:
               entry = db_entries[database][uuid]

               if "card_id" in entry:
                   card = entry["card_id"]
                   if card in db_entries["cards"] and db_entries["cards"][card][0]:
                       if db_entries["cards"][card][0] == uuid:
                           if card in db_entries["cards"]: del db_entries["cards"][card]

               for track in entry["tracks"]:
                   file = db_entries["tracks"][track]["file"]
                   if track in db_entries["tracks"]: del db_entries["tracks"][track]
                   if file in db_entries["files"]:   del db_entries["files"][file]

               if entry["artist"] in db_entries["albums"] and entry["album"] in db_entries["albums"][entry["artist"]]:
                   del db_entries["albums"][entry["artist"]][entry["album"]]

               del db_entries["album_info"][uuid]

           else:
               data = mboxAPI_error(data, "Entry not found in DB: "+uuid+"/"+database)

       # delete track
       elif "t_" in uuid:
           database = "tracks"
           if uuid in db_entries[database]:
               entry = db_entries[database][uuid]
               file  = entry["file"]
               if file in db_entries["file"]: del db_entries["files"][file]
               del db_entries[database][uuid]
           else:
               data = mboxAPI_error(data, "Entry not found in DB: "+uuid+"/"+database)

       # delete stream
       elif "r_" in uuid:
           database = "radio"
           if uuid in db_entries[database]:
               entry = db_entries[database][uuid]

               if "card_id" in entry:
                   card = entry["card_id"]
                   if card in db_entries["cards"] and db_entries["cards"][card][0]:
                       if db_entries["cards"][card][0] == uuid:
                           del db_entries["cards"][card]

               del db_entries[database][uuid]
           else:
               data = mboxAPI_error(data, "Entry not found in DB: "+uuid+"/"+database)

       # delete playlist
       elif "p_" in uuid:
           database = "playlists"
           if uuid in db_entries[database]:
               entry  = db_entries[database][uuid]

               if "card_id" in entry:
                   card = entry["card_id"]
                   if card in db_entries["cards"] and db_entries["cards"][card][0]:
                       if db_entries["cards"][card][0] == uuid:
                           del db_entries["cards"][card]

               del db_entries[database][uuid]
           else:
               data = mboxAPI_error(data, "Entry not found in DB: "+uuid+"/"+database)

       # delete card and unlink linked element
       elif ","  in uuid:
           logging.info("Delete card "+uuid)
           database = "cards"
           if uuid in db_entries[database]:
               entry_id = db_entries[database][uuid][0]
               del db_entries[database][uuid]
               for name in databases:
                 if entry_id in db_entries[name] and "card_id" in db_entries[name][entry_id]:
                   del db_entries[name][entry_id]["card_id"]
           else:
               data = mboxAPI_error(data, "Entry not found in DB: "+uuid+"/"+database)

       else:
           data = mboxAPI_error(data, "UUID format not supported: "+uuid)           

       # write change data to DB
       for name in databases: couch.write(name, db_entries[name])

       data = mboxAPI_end(data,["no-statistic","no-playback","no-system"])
       return(data)

# ---

def mboxAPI_add(database,param):

       global couch
       db_entries = {}
       databases  = ["playlists","radio"]
       data       = mboxAPI_start("add","add",database,param,"")
       param      = urllib.parse.unquote(param)

       # read all data from DB
       for name in databases: db_entries[name] = couch.read(name)

       if database == "playlists":
           uuid_p       = "p_"+str(uuid.uuid1())
           parameter  = param.split("||")

           # create playlist
           playlist                           = {}
           playlist["uuid"]                   = uuid_p
           playlist["title"]                  = parameter[0]
           if len(parameter) > 0:
               playlist["description"]        = parameter[1]
           playlist["tracks"]                 = []
           playlist["tracks_ref"]             = []
           playlist["cover_images"]           = {}
           playlist["cover_images"]["active"] = "none"
           playlist["cover_images"]["upload"] = []
           playlist["cover_images"]["web"]    = []

           # write playlist
           if not database in db_entries:  db_entries[database] = {}
           db_entries[database][uuid_p] = playlist
           data["LOAD"]["UUID"] = uuid_p

       elif database == "radio":
           uuid_r = "r_"+str(uuid.uuid1())
           parameter = param.split("||")

           # create radio
           playlist                           = {}
           playlist["uuid"]                   = uuid_r
           playlist["title"]                  = parameter[0]
           if len(parameter) > 0:
               playlist["description"]        = parameter[1]
           if len(parameter) > 1:
               playlist["stream_info"]        = parameter[2]
           if len(parameter) > 2:
               playlist["stream_url"]         = parameter[3]
           playlist["stream_url2"]            = ""
           playlist["cover_images"]           = {}
           playlist["cover_images"]["active"] = "none"
           playlist["cover_images"]["upload"] = []
           playlist["cover_images"]["web"]    = [parameter[4]]

           # write radio
           if not database in db_entries:  db_entries[database] = {}
           db_entries[database][uuid_r] = playlist
           data["LOAD"]["UUID"] = uuid_r

       else:
           data = mboxAPI_error(data, "Command not supported: "+database)
       
       
       # write change data to DB
       for name in db_entries: couch.write(name, db_entries[name])

       data = mboxAPI_end(data,["no-statistic","no-playback","no-system"])
       return(data)

# ---

def mboxAPI_images(cmd,uuid,param):

       global couch
       data       = mboxAPI_start("images","images",cmd,uuid,param)

       # identify UUID type
       if   "p_" in uuid: key = "playlists"
       elif "a_" in uuid: key = "album_info"
       elif "r_" in uuid: key = "radio"
       else:
           data = mboxAPI_error(data, "UUID type not supported: "+uuid)
           data = mboxAPI_end(data)
           return(data)

       # read data from DB
       db_entries = {}
       db_entries[key] = couch.read(key)

       # add image from download
       if (cmd == "upload" and len(key) > 0):

           playlist = db_entries[key][uuid]
           if param == "-":
               playlist["cover_images"]["active"] = "none"
               playlist["cover_images"]["upload"] = []
           else:
               playlist["cover_images"]["active"] = "upload"
               playlist["cover_images"]["upload"] = [param]

       # set active image
       elif (cmd == "set_active" and len(key) > 0):

           playlist = db_entries[key][uuid]
           allowed  = ["upload","dir","track","web"]
           
           if param in allowed: playlist["cover_images"]["active"] = param
           else:                data = mboxAPI_error(data, "Image type not supported: "+param)

       # command not implemented           
       else:
           data = mboxAPI_error(data, "Command or UUID is not valid: "+uuid+"/"+param)
           logging.warn("Command or UUID is not valid: "+uuid+"/"+param)

       # write change data to DB
       couch.write(key, db_entries[key])

       data = mboxAPI_end(data,["no-statistic","no-playback","no-system"])
       return(data)

# ---

def mboxAPI_playlist_items(cmd,uuid,param):

       global couch
       db_entries = {}
       databases  = ["playlists","tracks","album_info"]
       data       = mboxAPI_start("playlist_items","playlist_items",cmd,uuid,param)

       # read all data from DB
       for name in databases: db_entries[name] = couch.read(name)

       #####
       
       if cmd == "add":
       
           if uuid in db_entries["playlists"]:
               playlist = db_entries["playlists"][uuid]
               if "tracks"     not in playlist: playlist["tracks"]     = []
               if "tracks_ref" not in playlist: playlist["tracks_ref"] = []
                                  
               # add track to playlist
               if param in db_entries["tracks"]:
                   if param not in playlist["tracks"]:
                       playlist["tracks"].append(param)
                       playlist["tracks_ref"].append(db_entries["tracks"][param]["file"])
                   else:
                       data = mboxAPI_error(data, "Track/album already part of playlist: "+uuid+"/"+param)                   
                       
               # add album to playlist
               elif param in db_entries["album_info"]:
                   if param not in playlist["tracks"]:
                       playlist["tracks"].append(param)
                       playlist["tracks_ref"].append(db_entries["album_info"][param]["albumpath"])
                   else:
                       data = mboxAPI_error(data, "Track/album already part of playlist: "+uuid+"/"+param)                   
               
               # uuid not found
               else:
                   data = mboxAPI_error(data, "Track/album to add not found: "+uuid+"/"+param)
                   
               db_entries["playlists"][uuid] = playlist
           else:
               data = mboxAPI_error(data, "Playlist not found: "+uuid+"/"+param)


       elif cmd == "delete":

           if uuid in db_entries["playlists"]:
           
               playlist = db_entries["playlists"][uuid]                   
               if param in playlist["tracks"]:
                  x=playlist["tracks"].index(param)
                  playlist["tracks"][x:x+1]     = []
                  playlist["tracks_ref"][x:x+1] = []
                                 
               else:
                  data = mboxAPI_error(data, "Track/album not found: "+uuid+"/"+param)
                  
               db_entries["playlists"][uuid] = playlist                  
           else:
               data = mboxAPI_error(data, "Playlist not found: "+uuid+"/"+param)
           
       # write change data to DB
       for name in databases: couch.write(name, db_entries[name])

       data = mboxAPI_end(data,["no-statistic","no-playback","no-system"])
       return(data)

# ---

def mboxAPI_cardInfos(filter):

       global couch
       db_entries = {}
       data       = mboxAPI_start("cards","cards","","","")
       databases  = ["cards","album_info","playlists","radio"]

       # read all data from DB
       for name in databases:
           db_entries[name]   = couch.read_cache(name)
           data["DATA"][name] = {}

       data["DATA"]["cards"]      = db_entries["cards"]

       for card in db_entries["cards"]:
           id = db_entries["cards"][card][0]

           if "r_" in id and id in db_entries["radio"]:      data["DATA"]["radio"][id]      = db_entries["radio"][id]
           if "a_" in id and id in db_entries["album_info"]: data["DATA"]["album_info"][id] = db_entries["album_info"][id]
           if "p_" in id and id in db_entries["playlists"]:  data["DATA"]["playlists"][id]  = db_entries["playlists"][id]

       for name in databases:
           if filter in db_entries[name]: data["DATA"][name][filter] = db_entries[name][filter]
           
       if "," in filter:        data["DATA"]["_selected_uuid"]   = filter
       elif not "_" in filter:  data["DATA"]["_selected_filter"] = filter
          
       data = mboxAPI_end(data,["no-statistic","no-playback","no-system"])
       return(data)


# ---

def mboxAPI_cards(uuid,param):

       global couch
       db_entries  = {}
       data        = mboxAPI_start("cards","cards","",uuid,param)
       databases   = ["cards","album_info","playlists","radio"]
       update_time = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

       # read all data from DB
       for name in databases: db_entries[name] = couch.read(name)

       # check if card already used for different album
       if param in db_entries["cards"]:
           if db_entries["cards"][param][0] is not param and db_entries["cards"][param][0] != "":
               data = mboxAPI_error(data, "Card already in use for other entry: "+uuid+"/"+param)
               logging.warn("Card alread in use for other entry (old: " + db_entries["cards"][param][0] + "/ new: " + uuid + ")")

       # if uuid of album
       if "a_" in uuid:
           if uuid in db_entries["album_info"]:
               db_entries["album_info"][uuid]["card_id"]   = param
               db_entries["cards"][param]                  = [uuid,db_entries["album_info"][uuid]["album"],db_entries["album_info"][uuid]["artist"],update_time]                   
           else:
               data = mboxAPI_error(data, "Album to connect not found: "+uuid+"/"+param)
               logging.warn("Album to connect not found (" + uuid + ")")

       # if uuid of playlist
       elif "p_" in uuid:
           if uuid in db_entries["playlists"]:
               db_entries["playlists"][uuid]["card_id"]    = param
               db_entries["cards"][param]                  = [uuid,db_entries["playlists"][uuid]["title"],"",update_time]
           else:
               data = mboxAPI_error(data, "Playlist to connect not found: "+uuid+"/"+param)
               logging.warn("Playlist to connect not found (" + uuid + ")")

       # if uuid of radio channel
       elif "r_" in uuid:
           if uuid in db_entries["radio"]:
               db_entries["radio"][uuid]["card_id"]        = param
               db_entries["cards"][param]                  = [uuid,db_entries["radio"][uuid]["title"],"",update_time]
               #logging.warn("TEST - "+uuid+"|"+param+" ... ")
           else:
               data = mboxAPI_error(data, "Stream to connect not found: "+uuid+"/"+param)
               logging.warn("Stream to connect not found (" + uuid + ")")
               
       # write change data to DB
       for name in databases: couch.write(name, db_entries[name])

       data = mboxAPI_end(data,["no-statistic","no-playback","no-system"])
       return(data)


#-------------------------------------------------
# NEXT GEN: Control playback and volume
#-------------------------------------------------

def mboxAPI_volume(param):

       global couch
       db_entries = {}
       data       = mboxAPI_start("volume","volume","",param,"")
       
       if param == "mute":     thread_playlist_ctrl.player.mute()
       elif param == "up":     thread_playlist_ctrl.volume_up("up")
       elif param == "down":   thread_playlist_ctrl.volume_up("down")
       elif param.startswith("set"):
            getvol = param.split(":")
            thread_playlist_ctrl.volume_up(int(getvol[1]))
       else:
            data = mboxAPI_error(data, "Parameter not supported: "+param)
            logging.warn("Parameter not supported: " + param)   
            
       data = mboxAPI_end(data,["no-statistic","no-system"])
       return(data)

# ---

def mboxAPI_play_position(uuid, position):

       data = mboxAPI_play(uuid)      

       position = int(position)+1
       thread_playlist_ctrl.playlist_load_uuid(playlist_uuid=uuid, position=position)
       
       data = mboxAPI_end(data,["no-statistic","no-system"])
       return(data)

# ---

def mboxAPI_play(uuid):

       global couch
       db_entries = {}
       uuid       = mboxAPI_testUUID("album_info",uuid)
       data       = mboxAPI_start("play","play","",uuid,"")
       database   = {}
       
       mbox.active_device = "music_box"   
       if "a_" in uuid:   database  = couch.read_cache("album_info")
       elif "p_" in uuid: database  = couch.read_cache("playlists")
       elif "t_" in uuid: database  = couch.read_cache("tracks")
       elif "r_" in uuid: database  = couch.read_cache("radio")
                      
       if database != {}:
         if uuid in database:
           uuid_current = ""

           if "playlist_uuid" in thread_playlist_ctrl.music_ctrl:
             uuid_current = thread_playlist_ctrl.music_ctrl["playlist_uuid"]
             if uuid == uuid_current and "Paused" in thread_playlist_ctrl.music_ctrl["status"]:
               thread_playlist_ctrl.player.pause()
             else:
               thread_playlist_ctrl.playlist_load_uuid(uuid)

         else:
           data = mboxAPI_error(data, "UUID not found: "+uuid)

       else:
         data = mboxAPI_error(data, "UUID format not supported: "+uuid)
         logging.warn("UUID format not supported: " + uuid)
       
       data = mboxAPI_end(data,["no-statistic","no-system"])
       return(data)

# ---

def mboxAPI_next(step):

       global couch
       db_entries = {}
       data       = mboxAPI_start("next","next","",step,"")
       
       position      = thread_playlist_ctrl.music_list_p + int(step)
       playlist_uuid = thread_playlist_ctrl.music_ctrl["playlist_uuid"]       
       thread_playlist_ctrl.playlist_load_uuid(playlist_uuid=playlist_uuid, position=position)
                   
       data = mboxAPI_end(data,["no-statistic","no-system"])
       return(data)

# ---

def mboxAPI_last(step):

       global couch
       db_entries = {}
       data       = mboxAPI_start("last","last","",step,"")
       
       position      = thread_playlist_ctrl.music_list_p - int(step)
       playlist_uuid = thread_playlist_ctrl.music_ctrl["playlist_uuid"]       
       thread_playlist_ctrl.playlist_load_uuid(playlist_uuid=playlist_uuid, position=position)
            
       data = mboxAPI_end(data,["no-statistic","no-system"])
       return(data)

# ---

def mboxAPI_jump(percentage):

       global couch
       db_entries = {}
       data       = mboxAPI_start("jump","jump","",percentage,"")

       thread_playlist_ctrl.player.set_position(int(percentage))
                   
       data = mboxAPI_end(data,["no-statistic","no-system"])
       return(data)

# ---

def mboxAPI_pause():

       global couch
       db_entries = {}
       data       = mboxAPI_start("pause","pause","","","")

       thread_playlist_ctrl.player.pause()
       
       data = mboxAPI_end(data,["no-statistic","no-system"])
       return(data)

# ---

def mboxAPI_stop():

       global couch
       db_entries = {}
       data       = mboxAPI_start("stop","stop","","","")
       
       thread_playlist_ctrl.control_data(state="Ended",song={},playlist={})
       thread_playlist_ctrl.player.stop()
       
       data = mboxAPI_end(data,["no-statistic","no-system"])
       return(data)

#-------------------------------------------------
# NEXT GEN: templates
#-------------------------------------------------

def mboxAPI_template_read(param):

       global couch
       db_entries = {}
       data       = mboxAPI_start("template_read","template_read","",param,"")

       data = mboxAPI_end(data,["no-statistic","no-playback","no-system"])
       return(data)

# --- 

def mboxAPI_template_edit(database,param):

       global couch
       db_entries = {}
       data       = mboxAPI_start("template_edit","template_edit","",param,"")

       # read all data from DB
       for name in databases: db_entries[name] = couch.read(name)

       # write change data to DB
       for name in databases: couch.write(name, db_entries[name])

       data = mboxAPI_end(data,["no-statistic","no-playback","no-system"])
       return(data)



#-------------------------------------------------
# EOF

