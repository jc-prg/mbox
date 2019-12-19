# ---------------------------------
# mbox Configuration
# ---------------------------------

import modules.config_stage as stage

# ---------------------------------

RASPI = True   # True if Raspberry Pi and RFID reader connected
DEBUG = False  # True if output logging in DEBUG level

APIname       = "jc://mbox/server/"
APIname_LED   = "jc://mbox/LED/"
APIname_BTN   = "jc://mbox/button/"
APIname_RFID  = "jc://mbox/RFID/"
APIversion    = "v0.5.7"
APPversion    = "v0.5.5"
APPsupport    = [APPversion, "v0.5.4"]  # other supported versions

# ---------------------------------

initial_stage      = "Prod Stage"
active_device      = "music_box"
python_version     = "python3"
demo_card          = "125,232,21,163"

rfid_ctrl          = {
                     "CardUID"  : "",
                     "ButtonID" : ""
                     }

# ---------------------------------

checkdisk            = [-1,-1,-1,-1]
diskuse              = "du -c -d 0 "
diskfree             = "df --output=size "

start_time           = 0
start_duration       = 0

# ---------------------------------

system_drive         = "/"
system_data_drive    = "" # "/mnt/usb"

music_data           = stage.data_dir+"/data/"
music_dir            = stage.data_dir+"/music/"
music_cover          = stage.data_dir+"/cover/"
music_cover_upload   = stage.data_dir+"/cover_upload/"

errormsg_dir         = "audio/"
errormsg_test        = "DE_STARTING.mp3"

# ---------------------------------

databases  = { "radio" : [ "radio" ], 
               "music" : [ "albums", "album_info", "cards", "files", "tracks", "playlists", "artists" ] 
             }

# ---------------------------------

error_messages = {
          "200" : "OK",
          "201" : "Error",
          "202" : "Started",
          "203" : "See Message ...",

          "300" : "Successful loaded.",
          "301" : "Successful changed.",
          "302" : "Successful added.",
          "303" : "Successful deleted.",

          "400" : "ID doesn't exist.",
          "401" : "ID already exists.",

          "500" : "Image added/set successfully.",
          "501" : "Could not add/set image.",

          "800" : "Your app is up to date.",
          "801" : "Update available: " + APPversion + ".",
          "802" : "Update required: " + APPversion + ". Delete your browser cache, please."
         }



