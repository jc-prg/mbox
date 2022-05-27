import time
import uuid
import urllib.parse
import logging

import modules.music_podcast as music_podcast
import modules.config_stage as stage
import modules.config_mbox as mbox
import modules.jcRunCmd as run_cmd
from modules.jcRunCmd import *
from modules.server_init import *


def error_msg(code, info=""):
    if info != "": info = "(" + info + ")"

    message = mbox.error_messages

    if code in message:
        if int(code) >= 300:
            data = {"Code": code, "Msg": message[code], "Info": message[code] + " " + info}
            return data
        else:
            return message[code]
    else:
        return "UNKNOWN ERROR CODE"


class ServerApi:

    def __init__(self, db, music_ctrl, speak):
        """
        init server API (used via server_api.yml / swagger-file)
        """
        # self.db = db
        # self.speak = speak
        # self.ctrl = music_ctrl

        self.initial_data = {
            "API": {
                "name": "mBox",
                "version": mbox.api_version,
                "stage": mbox.initial_stage,
                "rollout": stage.rollout
                },
            }
        self.logging = logging.getLogger("api")
        self.logging.setLevel = stage.logging_level

    def response_error(self, data, error):
        """
        collect and log errors
        """
        if "error" in data["REQUEST"]:
            data["REQUEST"]["error"] += ", " + error
        else:
            data["REQUEST"]["error"] = error
        self.logging.warning(data["REQUEST"]["c-name"] + " ERROR:" + error)
        return data

    def response_start(self, cName, cmd1, cmd2, param1, param2):
        """
        set initial overarching data for the API response
        """
        self.logging.debug(cName + " START ...")

        data = self.initial_data
        data["REQUEST"] = {}
        data["REQUEST"]["status"] = "success"
        data["REQUEST"]["command"] = "mBox " + cName + ": " + str(cmd1) + ":" + str(cmd2) + " / " + str(param1) + ":" + str(
            param2)
        data["REQUEST"]["c-name"] = cName
        data["REQUEST"]["c-param"] = str(param1) + " " + str(param2)
        data["REQUEST"]["start-time"] = time.time()

        data["STATUS"] = {}
        data["DATA"] = {}
        data["DATA"]["SHORT"] = {}

        data["LOAD"] = {}
        data["LOAD"]["UUID"] = ""
        data["LOAD"]["RFID"] = ""

        if "cardUID" in mbox.rfid_ctrl:
            data["LOAD"]["RFID"] = mbox.rfid_ctrl["cardUID"]
        if "buttonID" in mbox.rfid_ctrl:
            data["LOAD"]["BUTTON"] = mbox.rfid_ctrl["buttonID"]
        if "_" in str(param1):
            data["LOAD"]["UUID"] = param1
        return data

    def response_end(self, data, reduce_data=[]):
        """
        set closing overarching data for the API response, delete unnecessary data
        """
        data["REQUEST"]["load-time"] = time.time() - data["REQUEST"]["start-time"]

        out = run_cmd.check_disk_space()

        data["STATUS"]["active_device"] = mbox.active_device

        if "no-playback" not in reduce_data:
            data["STATUS"]["playback"] = thread_music_ctrl.music_ctrl

        if "no-system" not in reduce_data:
            data["STATUS"]["system"] = {
                "space_usb_used": out[0],
                "space_usb_available": out[1],
                "space_usb_mount": stage.mount_data,
                "space_main_used": out[2],
                "space_main_available": out[3],
                "space_main_mount": stage.mount_system,
                "server_start": mbox.start_time,
                "server_start_duration": mbox.start_duration,
                "server_running": time.time() - mbox.start_time,
                "server_connection": run_cmd.connection_status()
            }
        data["STATUS"]["load_data"] = {
            "reload_new": thread_music_load.reload_new,
            "reload_all": thread_music_load.reload_all,
            "reload_progress": thread_music_load.reload_progress,
            "reload_time_left": thread_music_load.reload_time_left
        }

        #if "no-statistic" not in reduce_data:
        #    data["STATUS"]["statistic"] = {}
        #    for database in thread_couch.database:
        #        temp = thread_couch.read_cache(database)
        #        try:
        #            data["STATUS"]["statistic"][database] = len(temp.keys())
        #        except:
        #            data["STATUS"]["statistic"][database] = "error"

        if "no-request" in reduce_data:
            del data["REQUEST"]
        if "no-load" in reduce_data:
            del data["LOAD"]
        if "no-api" in reduce_data:
            del data["API"]

        self.logging.debug(data["REQUEST"]["c-name"] + " END")
        return data

    def status(self):
        """
        return system and playback status (see server_api.yml)
        """
        data = self.response_start("status", "status", "", "", "")
        data = self.check_active_card(data)
        data = self.response_end(data)
        return data

    def volume(self, param):
        """
        set volume for playback via API call (see server_api.yml)
        """
        data = self.response_start("volume", "volume", "", param, "")

        if param == "mute":
            thread_music_ctrl.mute()
        elif param == "up":
            thread_music_ctrl.volume_up("up")
        elif param == "down":
            thread_music_ctrl.volume_up("down")
        elif param.startswith("set"):
            get_vol = param.split(":")
            thread_music_ctrl.volume_up(int(get_vol[1]))
        else:
            data = self.response_error(data, "Parameter not supported: " + param)
            self.logging.warning("Parameter not supported: " + param)

        data = self.response_end(data, ["no-statistic", "no-system"])
        return data

    def play(self, uuid):
        """
        start playback of track via API call (see server_api.yml)
        """
        global thread_couch, thread_music_ctrl

        uuid = self.test_uuid("album_info", uuid)
        data = self.response_start("play", "play", "", uuid, "")

        mbox.active_device = "music_box"
        if "a_" in uuid:
            database = thread_couch.read_cache("album_info")
        elif "p_" in uuid:
            database = thread_couch.read_cache("playlists")
        elif "t_" in uuid:
            database = thread_couch.read_cache("tracks")
        elif "r_" in uuid:
            database = thread_couch.read_cache("radio")
        else:
            database = {}

        if database != {}:
            if uuid in database:
                if "playlist_uuid" in thread_music_ctrl.music_ctrl:
                    uuid_current = thread_music_ctrl.music_ctrl["playlist_uuid"]
                    if uuid == uuid_current and "Paused" in thread_music_ctrl.music_ctrl["status"]:
                        thread_music_ctrl.player.pause()
                    else:
                        thread_music_ctrl.playlist_load_uuid(uuid)
            else:
                data = self.response_error(data, "UUID not found: " + uuid)
        else:
            data = self.response_error(data, "UUID format not supported: " + uuid)
            self.logging.warning("UUID format not supported: " + uuid)

        data = self.response_end(data, ["no-statistic", "no-system"])
        return data

    def play_position(self, uuid, position):
        """
        jump to track in playlist via API call (see server_api.yml)
        """
        data = self.play(uuid)
        position = int(position) + 1
        thread_music_ctrl.playlist_load_uuid(playlist_uuid=uuid, position=position)
        data = self.response_end(data, ["no-statistic", "no-system"])
        return data

    def pause(self):
        """
        pause playback via API call (see server_api.yml)
        """
        data = self.response_start("pause", "pause", "", "", "")
        thread_music_ctrl.player.pause()
        data = self.response_end(data, ["no-statistic", "no-system"])
        return data

    def stop(self):
        """
        stop playback via API call (see server_api.yml)
        """
        data = self.response_start("stop", "stop", "", "", "")
        thread_music_ctrl.control_data(state="Ended", song={}, playlist={})
        thread_music_ctrl.player.stop()
        data = self.response_end(data, ["no-statistic", "no-system"])
        return data

    def next(self, step):
        """
        jump to last position forward in playlist via API call (see server_api.yml)
        """
        data = self.response_start("next", "next", "", step, "")
        thread_music_ctrl.playlist_next(step=step)
        data = self.response_end(data, ["no-statistic", "no-system"])
        return data

    def last(self, step):
        """
        jump to last position back in playlist via API call (see server_api.yml)
        """
        data = self.response_start("last", "last", "", step, "")
        step = step * -1
        thread_music_ctrl.playlist_next(step=step)
        data = self.response_end(data, ["no-statistic", "no-system"])
        return data

    def jump(self, percentage):
        """
        jump with playback to new position via API call (see server_api.yml)
        """
        data = self.response_start("jump", "jump", "", percentage, "")
        thread_music_ctrl.player.set_position(int(percentage))
        data = self.response_end(data, ["no-statistic", "no-system"])
        return data

    def read_db(self, databases, db_filter=""):
        """
        read data from database
        """
        global thread_couch
        param = databases
        uuid = ""
        data = self.response_start("readDB", "readDB", "", param, "")

        if ">>" in db_filter:
            the_filter = db_filter.split(">>")
        else:
            the_filter = db_filter.split("||")
        if len(the_filter) > 1:
            uuid = the_filter[1]

        if databases == "all":
            db_list = ["files", "tracks", "albums", "album_info", "cards", "playlists", "radio", "artists"]
        elif "--" in databases:
            db_list = databases.split("--")
        elif databases == "artists":
            db_list = ["albums", "album_info", "artists"]
        else:
            db_list = [databases]

        # read complete databases
        for database in db_list:
            if database in thread_couch.database:
                if "main" in thread_couch.database[database]:
                    data["DATA"][database] = thread_couch.read_cache(database)
                else:
                    data = self.response_error(data, "Database empty: " + database)
            else:
                data = self.response_error(data, "Database not found: " + database)

            if uuid != "" and uuid in data["DATA"][database]:
                data["DATA"]["_selected_uuid"] = uuid
                data["DATA"]["_selected_db"] = database
                data["DATA"]["_selected"] = data["DATA"][database][uuid]

        # TEMP ... read podcast ...
        if databases == "radio":
            for stream_uuid in data["DATA"]["radio"]:
                stream_url = data["DATA"]["radio"][stream_uuid]["stream_url"]

                is_podcast = False
                for end in music_podcast.podcast_ending:
                    if stream_url.endswith(end):
                        is_podcast = True

                if is_podcast:
                    podcast = thread_music_ctrl.podcast.get_podcasts(playlist_uuid=stream_uuid)
                    data["DATA"]["radio"][stream_uuid]["podcast"] = podcast
                    if "_selected_uuid" in data and stream_uuid == uuid:
                        data["DATA"]["_selected"]["podcast"] = podcast
                        if "cover_images" in podcast:
                            data["DATA"]["_selected"]["cover_images"] = podcast["cover_images"]

                elif stream_url.endswith(".m3u"):
                    data["DATA"]["radio"][stream_uuid]["stream_url2"] = thread_music_ctrl.player.get_stream_m3u(stream_url)
                    if "_selected_uuid" in data and stream_uuid == uuid:
                        data["DATA"]["_selected"]["stream_url2"] = thread_music_ctrl.player.get_stream_m3u(stream_url)

        # .... check for errors!
        if databases == "artists":
            artists = {}
            for key in data["DATA"]["album_info"]:
                album_info = data["DATA"]["album_info"][key]
                artist = album_info["artist"]
                album = {"album": album_info["albumname"], "uuid": key}

                if "#error" not in artist:
                    if artist not in artists: artists[artist] = []
                    artists[artist].append(album)

            data["DATA"]["artists"] = artists
            del data["DATA"]["album_info"]
            del data["DATA"]["albums"]

        data = self.filter(data, db_filter)
        data = self.response_end(data, ["no-statistic", "no-playback", "no-system"])
        return data

    def read_entry(self, uuid, db_filter=""):
        """
        read a specific entry from the database
        """
        global thread_couch, thread_music_ctrl

        # identify database
        if "a_" in uuid:
            database = "album_info"
        elif "t_" in uuid:
            database = "tracks"
        elif "r_" in uuid:
            database = "radio"
        elif "p_" in uuid:
            database = "playlists"
        elif "/" in uuid:
            database = "files"
        elif "," in uuid:
            database = "cards"
        else:
            database = ""

        param = database
        param2 = uuid
        uuid = self.test_uuid(database, uuid)
        data = self.response_start("readEntry", "readEntry", "", param, param2)

        # read entry from database
        if database in thread_couch.database:
            temp_tracks = thread_couch.read_cache("tracks")
            temp_albums = thread_couch.read_cache("album_info")

            if "main" in thread_couch.database[database]:
                temp = thread_couch.read_cache(database)

                if uuid in temp:
                    data["DATA"]["_selected_uuid"] = uuid
                    data["DATA"]["_selected_db"] = database

                    # check if rfid card (array instead of dict)
                    if not isinstance(temp[uuid], list):
                        data["DATA"]["_selected"] = temp[uuid]
                    else:
                        data["DATA"]["_selected"] = {}
                        data["DATA"]["_selected"]["card_info"] = temp[uuid]

                    if "tracks" not in data["DATA"]["_selected"]:
                        data["DATA"]["_selected"]["tracks"] = {}

                    if "tracks" in temp[uuid]:
                        if "tracks" not in data["DATA"]: data["DATA"]["tracks"] = {}
                        if "album_info" not in data["DATA"]: data["DATA"]["album_info"] = {}
                        self.logging.info("-> " + str(len(temp[uuid]["tracks"])) + " tracks")
                        for key in temp[uuid]["tracks"]:
                            self.logging.debug(key)
                            # if track add track info
                            if key in temp_tracks: data["DATA"]["tracks"][key] = temp_tracks[key]
                            # if album add album info and track information
                            if key in temp_albums:
                                data["DATA"]["album_info"][key] = temp_albums[key]
                                for key_track in temp_albums[key]["tracks"]:
                                    data["DATA"]["tracks"][key_track] = temp_tracks[key_track]

                    if "uuid" not in data["DATA"]["_selected"]:
                        data["DATA"]["_selected"]["uuid"] = uuid

                    # special handling for streams and podcast (read up-to-date data)
                    if uuid.startswith("r_"):
                        temp[uuid]["podcast"] = thread_music_ctrl.podcast.get_podcasts(playlist_uuid=uuid)
                        if "cover_images" in temp[uuid]["podcast"]:
                            data["DATA"]["_selected"]["cover_images"] = temp[uuid]["podcast"]["cover_images"]
                        if data["DATA"]["_selected"]["stream_url"].endswith(".m3u"):
                            data["DATA"]["_selected"]["stream_url2"] = thread_music_ctrl.player.get_stream_m3u(
                                data["DATA"]["_selected"]["stream_url"])

                else:
                    data = self.response_error(data, "Entry not in database: " + uuid)
            else:
                data = self.response_error(data, "Database empty: " + database)
        else:
            data = self.response_error(data, "Database not found: " + database)

        data = self.filter(data, db_filter)
        data = self.response_end(data, ["no-statistic", "no-playback", "no-system"])
        return data

    def edit(self, uuid, entry_data):
        global thread_couch
        database = ""
        databases = ["files", "tracks", "albums", "album_info", "cards", "playlists", "radio", "artists"]
        db_entries = {}
        data = self.response_start("edit", "edit", "", uuid, "")

        # read all data from DB
        for name in databases:
            db_entries[name] = thread_couch.read(name)

        # identify database
        if "a_" in uuid:
            database = "album_info"
        elif "t_" in uuid:
            database = "tracks"
        elif "r_" in uuid:
            database = "radio"
        elif "p_" in uuid:
            database = "playlists"
        else:
            data = self.response_error(data, "UUID format not supported: " + uuid)

        # edit specific values in selected entry
        if uuid in db_entries[database]:
            entry = db_entries[database][uuid]
            for key in entry_data:
                if key in entry:
                    entry[key] = entry_data[key]
            db_entries[database][uuid] = entry

        else:
            data = self.response_error(data, "UUID not found: " + uuid + "/" + database)

        # write change data to DB
        for name in databases:
            thread_couch.write(name, db_entries[name])

        data = self.response_end(data, ["no-statistic", "no-playback", "no-system"])
        return data

    def delete(self, uuid):
        global couch
        database = ""
        databases = ["files", "tracks", "albums", "album_info", "cards", "playlists", "radio", "artists"]
        databases_changed = []
        db_entries = {}
        data = self.response_start("delete", "delete", "", uuid, "")

        # read all data from DB
        for name in databases:
            db_entries[name] = thread_couch.read_cache(name)

        # delete album, tracks, files, link to card
        if "a_" in uuid:
            database = "album_info"
            if uuid in db_entries[database]:
                entry = db_entries[database][uuid]

                if "card_id" in entry:
                    card = entry["card_id"]
                    if card in db_entries["cards"] and db_entries["cards"][card][0]:
                        if db_entries["cards"][card][0] == uuid:
                            if card in db_entries["cards"]: del db_entries["cards"][card]

                for track in entry["tracks"]:
                    file = db_entries["tracks"][track]["file"]
                    if track in db_entries["tracks"]:
                        del db_entries["tracks"][track]
                    if file in db_entries["files"]:
                        del db_entries["files"][file]

                if entry["artist"] in db_entries["albums"] and entry["album"] in db_entries["albums"][entry["artist"]]:
                    del db_entries["albums"][entry["artist"]][entry["album"]]

                del db_entries["album_info"][uuid]

            else:
                data = self.response_error(data, "Entry not found in DB: " + uuid + "/" + database)

        # delete track
        elif "t_" in uuid:
            database = "tracks"
            if uuid in db_entries[database]:
                entry = db_entries[database][uuid]
                file = entry["file"]
                if file in db_entries["file"]: del db_entries["files"][file]
                del db_entries[database][uuid]
            else:
                data = self.response_error(data, "Entry not found in DB: " + uuid + "/" + database)

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
                data = self.response_error(data, "Entry not found in DB: " + uuid + "/" + database)

        # delete playlist
        elif "p_" in uuid:
            database = "playlists"
            if uuid in db_entries[database]:
                entry = db_entries[database][uuid]

                if "card_id" in entry:
                    card = entry["card_id"]
                    if card in db_entries["cards"] and db_entries["cards"][card][0]:
                        if db_entries["cards"][card][0] == uuid:
                            del db_entries["cards"][card]

                del db_entries[database][uuid]
            else:
                data = self.response_error(data, "Entry not found in DB: " + uuid + "/" + database)

        # delete card and unlink linked element
        elif "," in uuid or "test" in uuid:
            self.logging.info("Delete card " + uuid)
            database = "cards"
            if uuid in db_entries[database]:
                entry_id = db_entries[database][uuid][0]
                del db_entries[database][uuid]
                for name in databases:
                    if entry_id in db_entries[name] and "card_id" in db_entries[name][entry_id]:
                        del db_entries[name][entry_id]["card_id"]
            else:
                data = self.response_error(data, "Entry not found in DB: " + uuid + "/" + database)

        else:
            data = self.response_error(data, "UUID format not supported: " + uuid)

            # write change data to DB
        for name in databases:
            thread_couch.write(name, db_entries[name])

        data = self.response_end(data, ["no-statistic", "no-playback", "no-system"])
        return data

    def add(self, database, param):
        """
        add playlist or podcast
        """
        global thread_couch
        db_entries = {}
        databases = ["playlists", "radio"]
        data = self.response_start("add", "add", database, param, "")
        param = urllib.parse.unquote(param)

        # read all data from DB
        for name in databases:
            db_entries[name] = thread_couch.read(name)

        if database == "playlists":
            uuid_p = "p_" + str(uuid.uuid1())
            parameter = param.split("||")

            # create playlist
            playlist = {
                "uuid": uuid_p,
                "title": parameter[0],
                "tracks": [],
                "tracks_ref": [],
                "cover_images": {
                    "active": "none",
                    "upload": [],
                    "url": []
                }
            }
            if len(parameter) > 0:
                playlist["description"] = parameter[1]

            # write playlist
            if not database in db_entries:  db_entries[database] = {}
            db_entries[database][uuid_p] = playlist
            data["LOAD"]["UUID"] = uuid_p

        elif database == "radio":
            uuid_r = "r_" + str(uuid.uuid1())
            parameter = param.split("||")

            # create radio
            playlist = {}
            playlist["uuid"] = uuid_r
            playlist["title"] = parameter[0]
            if len(parameter) > 0:
                playlist["description"] = parameter[1]
            if len(parameter) > 1:
                playlist["stream_info"] = parameter[2]
            if len(parameter) > 2:
                playlist["stream_url"] = parameter[3]
            playlist["stream_url2"] = ""
            playlist["cover_images"] = {}
            playlist["cover_images"]["active"] = "none"
            playlist["cover_images"]["upload"] = []
            playlist["cover_images"]["url"] = [parameter[4]]

            # write radio
            if database not in db_entries:  db_entries[database] = {}
            db_entries[database][uuid_r] = playlist
            data["LOAD"]["UUID"] = uuid_r

        else:
            data = self.response_error(data, "Command not supported: " + database)

        # write change data to DB
        for name in db_entries:
            thread_couch.write(name, db_entries[name])

        data = self.response_end(data, ["no-statistic", "no-playback", "no-system"])
        return data

    def images(self, cmd, uuid, param):
        global thread_couch
        data = self.response_start("images", "images", cmd, uuid, param)

        # identify UUID type
        if "p_" in uuid:
            key = "playlists"
        elif "a_" in uuid:
            key = "album_info"
        elif "r_" in uuid:
            key = "radio"
        else:
            data = self.response_error(data, "UUID type not supported: " + uuid)
            data = self.response_end(data)
            return data

        # read data from DB
        db_entries = {key: thread_couch.read(key)}

        # add image from download
        if cmd == "upload" and len(key) > 0:

            playlist = db_entries[key][uuid]
            if param == "-":
                playlist["cover_images"]["active"] = "none"
                playlist["cover_images"]["upload"] = []
            else:
                playlist["cover_images"]["active"] = "upload"
                playlist["cover_images"]["upload"] = [param]

        # set active image
        elif cmd == "set_active" and len(key) > 0:

            playlist = db_entries[key][uuid]
            allowed = ["upload", "dir", "track", "url"]

            if param in allowed:
                playlist["cover_images"]["active"] = param
            else:
                data = self.response_error(data, "Image type not supported: " + param)

        # command not implemented
        else:
            data = self.response_error(data, "Command or UUID is not valid: " + uuid + "/" + param)
            self.logging.warning("Command or UUID is not valid: " + uuid + "/" + param)

        # write change data to DB
        thread_couch.write(key, db_entries[key])

        data = self.response_end(data, ["no-statistic", "no-playback", "no-system"])
        return data

    def playlist_items(self, cmd, uuid, param):
        global thread_couch
        db_entries = {}
        databases = ["playlists", "tracks", "album_info"]
        data = self.response_start("playlist_items", "playlist_items", cmd, uuid, param)

        # read all data from DB
        for name in databases:
            db_entries[name] = thread_couch.read(name)

        if cmd == "add":
            if uuid in db_entries["playlists"]:
                playlist = db_entries["playlists"][uuid]
                if "tracks" not in playlist: playlist["tracks"] = []
                if "tracks_ref" not in playlist: playlist["tracks_ref"] = []

                # add track to playlist
                if param in db_entries["tracks"]:
                    if param not in playlist["tracks"]:
                        playlist["tracks"].append(param)
                        playlist["tracks_ref"].append(db_entries["tracks"][param]["file"])
                    else:
                        data = self.response_error(data, "Track/album already part of playlist: " + uuid + "/" + param)

                        # add album to playlist
                elif param in db_entries["album_info"]:
                    if param not in playlist["tracks"]:
                        playlist["tracks"].append(param)
                        playlist["tracks_ref"].append(db_entries["album_info"][param]["albumpath"])
                    else:
                        data = self.response_error(data, "Track/album already part of playlist: " + uuid + "/" + param)
                        # uuid not found
                else:
                    data = self.response_error(data, "Track/album to add not found: " + uuid + "/" + param)
                db_entries["playlists"][uuid] = playlist
            else:
                data = self.response_error(data, "Playlist not found: " + uuid + "/" + param)

        elif cmd == "delete":
            if uuid in db_entries["playlists"]:
                playlist = db_entries["playlists"][uuid]
                if param in playlist["tracks"]:
                    x = playlist["tracks"].index(param)
                    playlist["tracks"][x:x + 1] = []
                    playlist["tracks_ref"][x:x + 1] = []
                else:
                    data = self.response_error(data, "Track/album not found: " + uuid + "/" + param)

                db_entries["playlists"][uuid] = playlist
            else:
                data = self.response_error(data, "Playlist not found: " + uuid + "/" + param)

        # write change data to DB
        for name in databases:
            thread_couch.write(name, db_entries[name])

        data = self.response_end(data, ["no-statistic", "no-playback", "no-system"])
        return data

    def cards(self, uuid, param):
        global thread_couch
        db_entries = {}
        data = self.response_start("cards", "cards", "", uuid, param)
        databases = ["cards", "album_info", "playlists", "radio"]
        update_time = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

        # read all data from DB
        for name in databases:
            db_entries[name] = thread_couch.read(name)

        # check if card already used for different album
        if param in db_entries["cards"]:
            if db_entries["cards"][param][0] is not param and db_entries["cards"][param][0] != "":
                data = self.response_error(data, "Card already in use for other entry: " + uuid + "/" + param)
                self.logging.warning(
                    "Card alread in use for other entry (old: " + db_entries["cards"][param][
                        0] + "/ new: " + uuid + ")")

        # if uuid of album
        if "a_" in uuid:
            if uuid in db_entries["album_info"]:
                db_entries["album_info"][uuid]["card_id"] = param
                db_entries["cards"][param] = [uuid, db_entries["album_info"][uuid]["album"],
                                              db_entries["album_info"][uuid]["artist"], update_time]
            else:
                data = self.response_error(data, "Album to connect not found: " + uuid + "/" + param)
                self.logging.warning("Album to connect not found (" + uuid + ")")

        # if uuid of playlist
        elif "p_" in uuid:
            if uuid in db_entries["playlists"]:
                db_entries["playlists"][uuid]["card_id"] = param
                db_entries["cards"][param] = [uuid, db_entries["playlists"][uuid]["title"], "", update_time]
            else:
                data = self.response_error(data, "Playlist to connect not found: " + uuid + "/" + param)
                self.logging.warning("Playlist to connect not found (" + uuid + ")")

        # if uuid of radio channel
        elif "r_" in uuid:
            if uuid in db_entries["radio"]:
                db_entries["radio"][uuid]["card_id"] = param
                db_entries["cards"][param] = [uuid, db_entries["radio"][uuid]["title"], "", update_time]
            else:
                data = self.response_error(data, "Stream to connect not found: " + uuid + "/" + param)
                self.logging.warning("Stream to connect not found (" + uuid + ")")

        # write change data to DB
        for name in databases:
            thread_couch.write(name, db_entries[name])

        data = self.response_end(data, ["no-statistic", "no-playback", "no-system"])
        return data

    def card_info(self, filter):
        global thead_couch
        db_entries = {}
        data = self.response_start("cards", "cards", "", "", "")
        databases = ["cards", "album_info", "playlists", "radio"]

        # read all data from DB
        for name in databases:
            db_entries[name] = thread_couch.read_cache(name)
            data["DATA"][name] = {}

        data["DATA"]["cards"] = db_entries["cards"]

        for card in db_entries["cards"]:
            id = db_entries["cards"][card][0]

            if "r_" in id and id in db_entries["radio"]:
                data["DATA"]["radio"][id] = db_entries["radio"][id]
            if "a_" in id and id in db_entries["album_info"]:
                data["DATA"]["album_info"][id] = db_entries["album_info"][id]
            if "p_" in id and id in db_entries["playlists"]:
                data["DATA"]["playlists"][id] = db_entries["playlists"][id]

        for name in databases:
            if filter in db_entries[name]: data["DATA"][name][filter] = db_entries[name][filter]

        if "," in filter:
            data["DATA"]["_selected_uuid"] = filter
        elif not "_" in filter:
            data["DATA"]["_selected_filter"] = filter

        data = self.response_end(data, ["no-statistic", "no-playback", "no-system"])
        return data

    def card_set(self, cardUID):
        """
        set card UID by microservice to central var
        """
        param = cardUID
        data = self.response_start("setCard", "setCard", "", param, "")

        if param == "no_card" or param == "-":
            mbox.rfid_ctrl["cardUID"] = ""
        else:
            mbox.rfid_ctrl["cardUID"] = param

        data = self.response_end(data)
        return data

    def speak(self, message):
        """
        set card UID by microservice to central var
        """
        global thread_speak
        data = self.response_start("speak", "speak", "", message, "")
        thread_speak.speak_message(message)
        data = self.response_end(data)
        return data

    def set_button(self, buttonID):
        """
        set button ID by microservice to central var
        """
        param = buttonID
        data = self.response_start("setButton", "setButton", "", param, "")

        if param == "no_button":
            mbox.rfid_ctrl["buttonID"] = ""
        else:
            mbox.rfid_ctrl["buttonID"] = param

        if mbox.active_device == "music_box" and param == "next":
            thread_music_ctrl.playlist_next(1)
        elif mbox.active_device == "music_box" and param == "back":
            thread_music_ctrl.playlist_next(-1)
        elif mbox.active_device == "music_box" and param == "pause":
            thread_music_ctrl.player.pause()

        data = self.response_end(data)
        return data

    def backup(self, param):
        """
        create or restore backup for couchDB
        """
        global thread_couch
        data = self.response_start("backup", "backup", "", param, "")

        if param == "json2db":
            thread_couch.restore_from_json()
        elif param == "db2json":
            thread_couch.backup_to_json()
        else:
            data = self.response_error(data, "Parameter is not supported.")

        data = self.response_end(data)
        return data

    def load(self, param):
        """
        reload metadata from music files or images
        """
        global thread_couch
        data = self.response_start("load", "load", "", param, "")

        if param == "new":
            thread_music_load.reload_new = True
        elif param == "all":
            thread_music_load.reload_all = True
        elif param == "images":
            thread_music_load.reload_img = True
        else:
            data = self.response_error(data, "Parameter is not supported.")

        data = self.response_end(data)
        return data

    def check_version(self, APPversion):
        """
        check if APP version is supported by server
        """
        global thread_couch
        param = mbox.app_version
        data = self.response_start("checkVersion", "checkVersion", "", param, "")

        if (APPversion == mbox.app_version):
            result = error_msg("800")
        elif (APPversion in mbox.app_support):
            result = error_msg("801")
        else:
            result = error_msg("802")

        data["STATUS"]["check-version"] = result
        data = self.response_end(data, ["no-statistic", "no-playback", "no-system"])
        return data

    def template_read(self, param):
        data = self.response_start("template_read", "template_read", "", param, "")
        data = self.response_end(data, ["no-statistic", "no-playback", "no-system"])
        return data

    def template_edit(self, database, param):
        global thread_couch
        db_entries = {}
        data = self.response_start("template_edit", "template_edit", "", param, "")

        # read all data from DB
        for name in databases:
            db_entries[name] = thread_couch.read(name)
        # write change data to DB
        for name in databases:
            thread_couch.write(name, db_entries[name])

        data = self.response_end(data, ["no-statistic", "no-playback", "no-system"])
        return data

    @staticmethod
    def test_uuid(database, uuid):
        """
        if uuid is "test", get uuid from first dataset in database
        """
        global thread_couch
        if "test" in uuid:
            temp = thread_couch.read_cache(database)
            for key in temp:
                uuid = key
                break
        return uuid

    @staticmethod
    def check_active_card(data):
        """
        check if card already is connected, otherwise return signal and list of available items ...
        """
        if data["LOAD"]["RFID"] == "":
            return data
        card = data["LOAD"]["RFID"]
        cards = thread_couch.read_cache("cards")
        if card not in cards:
            data["LOAD"]["CARD"] = "unknown"
            db_list = ["album_info", "playlists", "radio"]
            for db in db_list:
                temp_db = thread_couch.read_cache(db)
                data["DATA"]["SHORT"][db] = {}
                for entry in temp_db:
                    if "title" in temp_db[entry]:
                        data["DATA"]["SHORT"][db][entry] = temp_db[entry]["title"]
                    elif "album" in temp_db[entry]:
                        data["DATA"]["SHORT"][db][entry] = temp_db[entry]["album"] + " (" + temp_db[entry]["artist"] + ")"
        else:
            data["LOAD"]["CARD"] = "known"
        return data

    @staticmethod
    def filter(data, db_filter=""):
        if "db_filter" in data["REQUEST"] and db_filter:
            data["REQUEST"]["db_filter"] += "||" + db_filter
        elif db_filter:
            data["REQUEST"]["db_filter"] = db_filter
        return data


api_calls = ServerApi(thread_couch, thread_music_ctrl, thread_speak)
