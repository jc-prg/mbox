import modules.config_stage as stage


RASPI = True  # True if Raspberry Pi and RFID reader connected
DEBUG = False  # True if output logging in DEBUG level

api_name = "jc://mbox/server/"
api_name_LED = "jc://mbox/LED/"
api_name_BTN = "jc://mbox/BUTTON/"
api_name_RFID = "jc://mbox/RFID/"
api_version = "v0.9.9"
app_version = "v0.9.9"
app_support = [app_version,
               "v1.0.0"
               ]  # other supported versions

initial_stage = "Prod Stage"
active_device = "music_box"
python_version = "python3"
demo_card = "125,232,21,163"

rfid_ctrl = {
    "CardUID": "",
    "ButtonID": ""
}

disk_usage_output = [-1, -1, -1, -1]
disk_use_cmd = "du -c -d 0 "
disk_free_cmd = "df --output=size "

start_time = 0
start_duration = 0

system_drive = "/"
system_data_drive = ""  # "/mnt/usb"

music_data = stage.data_dir + "/data/"
music_dir = stage.data_dir + "/music/"
music_cover = stage.data_dir + "/cover/"
music_cover_upload = stage.data_dir + "/cover_upload/"

error_msg_dir = "audio/"
error_msg_test = "DE_STARTING.mp3"

log_connection = "/log/internet_connect"
log_autohotspot = "/log/autohotspot.status"

databases = {"radio": ["radio"],
             "music": ["albums", "album_info", "cards", "files", "tracks", "playlists", "artists"],
             "other": ["status"]
             }

error_messages = {
    "200": "OK",
    "201": "Error",
    "202": "Started",
    "203": "See Message ...",

    "300": "Successful loaded.",
    "301": "Successful changed.",
    "302": "Successful added.",
    "303": "Successful deleted.",

    "400": "ID doesn't exist.",
    "401": "ID already exists.",

    "500": "Image added/set successfully.",
    "501": "Could not add/set image.",

    "800": "Your app is up to date.",
    "801": "Update available: " + app_version + ".",
    "802": "Update required: " + app_version + ". Delete your browser cache, please."
}
