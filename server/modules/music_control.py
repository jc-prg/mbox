import threading
import time
import logging
import modules.config_stage as stage
import modules.config_mbox as mbox
import modules.music_podcast as music_podcast


class MusicControlThread(threading.Thread):

    def __init__(self, device, thread_database, thread_player, thread_speak, thread_podcast, start_time):
        """
        set initial values to vars and start VLC
        """
        threading.Thread.__init__(self)
        self.speak = thread_speak
        self.player = thread_player
        self.podcast = thread_podcast
        self.start_time = start_time
        self.running = True

        self.music_list = []
        self.music_list_p = 1
        self.music_list_uuid = ""
        self.music_database = thread_database
        self.music_loaded = -1
        self.music_plays = -1
        self.music_dir = mbox.music_dir
        self.music_device = device
        self.music_load_new = False
        self.music_load_new_p = False
        self.music_ctrl = {}
        self.music_ctrl = self.control_data(state="Started")
        self.music_type = ""

        time.sleep(2)

        self.last_card_identified = ""
        self.relevant_db = self.music_database.databases["music"]

        self.logging = logging.getLogger("control")
        self.logging.setLevel = stage.logging_level

    def run(self):
        """
        loop: check if track in playlist, stream ... and play status
        """
        self.logging.info("Start Music Control ..." + self.start_time)

        current_stream = {}
        wait_time = 0.1
        last_load = False
        last_run = self.music_database.read("status")

        if "music" not in last_run:
            last_run["music"] = {"playing": 0, "playlist_uuid": "no_uuid"}

        last_music = last_run["music"]

        if last_run["music"]["playing"] != 1 and "playlist_uuid" in last_music:
            self.logging.info(" - Don't load playlist and song from last run (" + last_music["playlist_uuid"] + ")...")

        elif last_run["music"]["playing"] != 1:
            self.logging.info(" - Don't load playlist and song from last run ...")

        elif last_run["music"]["playing"] == 1:
            self.music_ctrl = last_music
            self.music_ctrl["LastCard"] = ""
            self.music_loaded = 1
            self.podcast.check_playing_podcast(playing=1, playing_data=self.music_ctrl)

            if "playlist_files" in last_music:
                self.music_list = last_music["playlist_files"]
                self.music_list_p = last_music["playlist_pos"]
                self.music_load_new = True
                last_load = True

                self.logging.info("Load playlist and song from last run ...")
                self.logging.info("... " + last_music["playlist_uuid"])

        time.sleep(5)
        count = 0
        while self.running:

            time.sleep(wait_time)
            count += 1
            if count == 150:
                self.playback_status()
                count = 0

            self.music_plays = self.player.playing()
            self.podcast.check_playing_podcast(playing=self.music_plays, playing_data=self.music_ctrl)

            # if new data to be loaded
            self.logging.debug("Active playlist: " + str(self.music_load_new) + "; List: " + str(
                len(self.music_list)) + "; Position: " + str(self.music_list_p))
            if self.music_load_new and len(self.music_list) > 0 and int(self.music_list_p) <= len(self.music_list):

                self.music_load_new = False
                current_path = self.music_list[int(self.music_list_p) - 1]
                current_list = self.playlist_info()

                # if playlist or album
                if not self.music_list_uuid.startswith("r_"):
                    current_info = self.metadata_by_filename(current_path)
                    current_info["info"] = "Title loaded"
                    current_stream = ""

                # if stream or podcast
                else:
                    database = self.music_database.read_cache("radio")

                    # if stream exists
                    if self.music_list_uuid in database:
                        current_stream = database[self.music_list_uuid]
                        current_stream["podcast"] = self.podcast.get_podcasts(self.music_list_uuid,
                                                                              current_stream["stream_url"])

                        if current_stream["podcast"] != {}:
                            current_info = current_stream["podcast"]
                            current_list["list"] = []
                            for filename in current_list["files"]:
                                track_uuid = current_info["track_url"][filename]
                                track_info = current_info["tracks"][track_uuid]
                                current_list["list"].append(track_info)
                            current_uuid = current_info["track_url"][current_path]
                            current_info = current_info["tracks"][current_uuid]
                            current_info["uuid"] = current_uuid
                            current_info["info"] = "Title loaded"
                        else:
                            current_info = {"file": current_path, "stream": current_stream}
                            current_info["stream"]["uuid"] = self.music_list_uuid

                            # if stream_uuid not found
                    else:
                        current_info = {"file": current_path, "stream": current_stream}
                        current_info["stream"]["uuid"] = self.music_list_uuid

                # start playback
                if current_path.startswith("http"):
                    self.player.stop()
                    p = self.music_ctrl["position"]
                    self.music_ctrl = self.control_data(state="play", song=current_info, playlist=current_list)
                    self.music_ctrl["length"] = 0
                    self.music_ctrl["position"] = 0

                    if self.music_list_p == 1 and "title" in current_stream and "title" in current_info:
                        self.speak.speak_text(current_stream["title"] + ": 1. : " + current_info["title"] + ".")
                    elif "title" in current_info:
                        self.speak.speak_text(str(self.music_list_p) + ". : " + current_info["title"] + ".")
                    elif "title" in current_stream:
                        self.speak.speak_text(current_stream["title"] + ".")

                    self.player.play_stream(current_path)
                    self.music_ctrl["length"] = self.player.get_length()
                    self.music_ctrl["position"] = p

                else:
                    self.player.stop()
                    self.player.play_file(mbox.music_dir + current_path)

                # set playback metadata
                if not last_load:
                    if self.player.play_status == 1:
                        self.music_ctrl = self.control_data(state="play", song=current_info, playlist=current_list)
                    else:
                        self.music_ctrl = self.control_data(state="error", song={}, playlist=current_list)

                # if stopped device while playing, load last music
                if last_load:
                    self.logging.debug("Jump to position in song from last run ...")
                    if self.music_ctrl["length"] != 0:
                        position = (self.music_ctrl["position"] / self.music_ctrl["length"]) * 100
                    else:
                        position = 0
                    self.player.set_position(position)
                    last_load = False

                self.volume(self.music_ctrl["volume"])

            # if no new data, check if ended
            if not self.music_load_new:
                if self.player.player_status == "State.Ended":

                    if self.music_list_p < len(self.music_list):
                        self.music_load_new = True
                        self.music_list_p = int(self.music_list_p) + 1
                        self.logging.info(
                            "Next song in list, position: " + str(self.music_list_p) + "/" + str(len(self.music_list)))

                    else:
                        self.music_load_new = True
                        self.music_list = []
                        self.music_list_p = 1
                        self.music_type = ""
                        self.control_data(state="Ended", song={}, playlist={})
                        self.logging.info("Playlist empty, stop playing.")

                if self.player.play_status == 1:
                    self.music_ctrl["length"] = float(self.player.get_length()) / 1000
                    self.music_ctrl["position"] = float(self.player.get_position()) / 1000

            # check if rfid card and save status
            self.playlist_load_rfid()
            self.playback_save_status()

        self.logging.info("Stopped music control.")

    def stop(self):
        """
        Stop music control
        """
        self.player.stop()
        self.player.running = False
        self.running = False

    def volume(self, vol):
        """
        player volume
        """
        self.player.set_volume(vol)
        self.music_ctrl["volume"] = self.player.volume

    def mute(self, value=""):
        """
        player mute
        """
        self.player.mute(value)
        self.music_ctrl["mute"] = self.player.volume_mute
        self.logging.debug("Mute: " + str(self.music_ctrl["mute"]))

    def volume_up(self, up):
        """
        player volume
        """
        self.player.volume_up(up)
        self.music_ctrl["volume"] = self.player.volume

    def playlist_info(self):
        """
        prepare playlist info based on loaded playlist
        """
        current_list = {
            "uuid": "",
            "position": self.music_list_p,
            "length": len(self.music_list),
            "files": self.music_list,
            "list": []
        }
        for filename in self.music_list:
            if not filename.startswith("http"):
                file_info = self.metadata_by_filename(filename)
                current_list["list"].append(file_info)
        return current_list

    def playlist_load_uuid(self, playlist_uuid, position=1):
        """
        load list from album, playlist or stream -> put to playlist array
        """
        self.logging.info("Load Playlist " + playlist_uuid + "/" + str(position) + " ...")

        if playlist_uuid == self.music_list_uuid:
            self.music_list_p = int(position)
            self.music_load_new = True
            self.music_load_new_p = True
            return
        else:
            self.music_list_p = int(position)
            self.music_load_new = True
            self.music_list = []
            self.music_list_uuid = playlist_uuid

        if playlist_uuid.startswith("a_"):
            self.music_type = "Album"
        elif playlist_uuid.startswith("p_"):
            self.music_type = "Playlist"
        elif playlist_uuid.startswith("t_"):
            self.music_type = "Track"
        elif playlist_uuid.startswith("r_"):
            self.music_type = "Stream"
        else:
            self.music_type = ""

        if self.music_type == "Stream":
            self.music_device = "radio"
        else:
            self.music_device = "music_box"

        if self.music_device == "music_box":
            track_list = self.playlist_by_uuid(playlist_uuid)
            track_db = self.music_database.read_cache("tracks")

        else:
            podcast = self.podcast.get_podcasts(playlist_uuid)
            if "track_list" in podcast:
                track_list = podcast["track_list"]
                track_db = podcast["tracks"]
                if len(track_list) > 0:
                    self.music_type = "Podcast"
            else:
                track_list = self.playlist_by_uuid(playlist_uuid)
                track_db = {}

        for track in track_list:
            if track in track_db and "file" in track_db[track]:
                self.music_list.append(track_db[track]["file"])
            if track.startswith("http"):
                self.music_list.append(track)

    def playlist_load_rfid(self):
        """
        check rfid card value and load connected playlist -> put to playlist array
        """
        if "cardUID" in mbox.rfid_ctrl:

            self.logging.debug("Load UUID from RFID-Card: " + mbox.rfid_ctrl["cardUID"])
            database = self.music_database.read_cache("cards")

            if mbox.rfid_ctrl["cardUID"] != "":

                self.logging.info("CardUID: " + mbox.rfid_ctrl["cardUID"])
                if mbox.rfid_ctrl["cardUID"] in database:

                    if "LastCard" in self.music_ctrl and self.music_ctrl["LastCard"] == \
                            database[mbox.rfid_ctrl["cardUID"]][0]:
                        self.logging.info("Card already started (" + self.music_ctrl["LastCard"] + "/" +
                                          database[mbox.rfid_ctrl["cardUID"]][0] + ")...")

                    else:
                        self.logging.info(
                            "Start Playlist: " + database[mbox.rfid_ctrl["cardUID"]][0] + " / " + self.music_ctrl[
                                "LastCard"])
                        self.playlist_load_uuid(database[mbox.rfid_ctrl["cardUID"]][0])
                        self.music_ctrl["LastCard"] = database[mbox.rfid_ctrl["cardUID"]][0]

                else:
                    self.player.stop()
                    self.music_ctrl["LastCard"] = ""
                    self.control_data(state="error")

                    if mbox.rfid_ctrl["cardUID"] != self.last_card_identified:
                        self.logging.info("No Entry connected.")
                        self.last_card_identified = mbox.rfid_ctrl["cardUID"]

                        if mbox.rfid_ctrl["cardUID"] not in database:
                            self.speak.speak_message("NO-MUSIC-CONNECTED-TO-CARD")

    def playlist_next(self, step):
        """
        jump within the playlist
        """
        self.logging.debug(
            "Next song: " + str(step) + "+" + str(self.music_list_p) + " (" + str(len(self.music_list)) + ")")

        # back // if position > 0
        if step < 0 and self.music_list_p + step > 0:
            self.player.stop()
            self.music_list_p = self.music_list_p + step  # set new position in playlist
            self.music_load_new = True
            return "done"

        # forward // if position < length of list
        elif step > 0 and self.music_list_p + step <= len(self.music_list):
            self.player.stop()
            self.music_list_p = self.music_list_p + step  # set new position in playlist
            self.music_load_new = True
            return "done"

        # stop playing if beginning or end ...
        else:
            self.music_load_new = False
        #        self.player.stop()
        #        self.music_list_p        = 0                              # set new position in playlist

        return "not found"

    def playback_save_status(self):
        """
        write current playlist, track and position to config
        """
        data = self.music_database.read("status")

        if "_saved" not in data or data["_saved"] + 3 < time.time():
            if "file" in data["music"]["song"]:
                old_state = data["music"]["state"] + " " + str(data["music"]["song"]["file"])
            else:
                old_state = data["music"]["state"] + " " + str(data["music"]["song"])

            data["music"] = self.music_ctrl
            if "album_uuid" in data["music"]["song"] and data["music"]["song"]["album_uuid"].startswith("r_"):
                podcast_uuid = data["music"]["song"]["album_uuid"]
                data["music"]["podcast"] = self.podcast.get_podcasts(playlist_uuid=podcast_uuid)

            data["_saved"] = time.time()
            self.music_database.write("status", data)
            if "file" in data["music"]["song"]:
                new_state = data["music"]["state"] + " " + str(data["music"]["song"]["file"])
            else:
                new_state = data["music"]["state"] + " " + str(data["music"]["song"])
            if old_state != new_state:
                self.logging.info("Save playing status: ")
                self.logging.info(" - " + new_state)

    def metadata_by_filename(self, filename):
        """
        return metadata from db by filename
        """
        database = self.music_database.read_cache("files")
        filename = filename.replace(mbox.music_dir, "")
        if filename not in database:
            self.logging.error("Filename not in DB (" + filename + ").")
            return {}
        else:
            return database[filename]

    def metadata_by_uuid(self, get_uuid):
        """
        return metadata from db by filename
        """
        database = self.music_database.read_cache("tracks")
        if not get_uuid.startswith("t_"):
            self.logging.error("It's not a track.")
            return {}
        elif get_uuid not in database:
            self.logging.error("Track not found in DB.")
            return {}
        else:
            return database[get_uuid]

    def playlist_by_uuid(self, get_uuid):
        """
        return tracks from db by uuid
        """
        track_list = []
        if get_uuid.startswith("t_"):
            track_list = [get_uuid]

        elif get_uuid.startswith("a_"):
            database = self.music_database.read_cache("album_info")
            if get_uuid in database:
                track_list = database[get_uuid]["tracks"]
            else:
                self.logging.error("Album not found: " + get_uuid)
                track_list = []

        elif get_uuid.startswith("p_"):
            database_p = self.music_database.read_cache("playlists")
            database_a = self.music_database.read_cache("album_info")
            if get_uuid in database_p:
                tracks = database_p[get_uuid]["tracks"]
                track_list = []
                for track in tracks:
                    if track.startswith("t_"):
                        track_list.append(track)
                    elif track.startswith("a_") and track in database_a:
                        track_list.extend(database_a[track]["tracks"])
            else:
                self.logging.error("Album / track not found: " + get_uuid)
                track_list = []

        elif get_uuid.startswith("r_"):
            database = self.music_database.read_cache("radio")
            if get_uuid in database:
                stream_url = database[get_uuid]["stream_url"]

                if stream_url.endswith(".m3u"):
                    track_list = [stream_url]
                elif stream_url.endswith(".mp3"):
                    track_list = [stream_url]
                else:
                    is_podcast = False
                    for end in music_podcast.podcast_ending:
                        if stream_url.endswith(end):
                            is_podcast = True

                    if is_podcast:
                        self.podcast.get_tracks_rss(rss_url=stream_url, playlist_uuid=get_uuid)
                        self.logging.warning("RSS Feed / Podcast-List not implemented yet!")
                        track_list = []
                    else:
                        self.logging.warning("Unknown URL format. Try out ...")
                        track_list = [stream_url]

        else:
            self.logging.error("Unknown ID Type!")

        return track_list

    def control_data(self, state, song=None, playlist=None):
        """
        set and return control data
        """
        if song is None:
            song = {}
        if playlist is None:
            playlist = {}
        if state != "Started" and playlist != {}:
            if "LastCard" in self.music_ctrl:
                last_card = self.music_ctrl["LastCard"]
            else:
                last_card = ""

            if "stream" in song:
                stream = song["stream"]
                song = {}
            else:
                stream = {}

            #        if song != "":
            #           thread.music_ctrl["position"]         = float(thread.player.get_time()) / 1000
            self.music_ctrl = {
                "device": self.music_device,
                "type": self.music_type,
                "mute": self.player.volume_mute,
                "status": self.player.player_status,
                "connected": self.player.connected,
                "file": self.player.play_url,
                "song": song,
                "stream": stream,
                "playlist": playlist["list"],
                "playlist_pos": playlist["position"],
                "playlist_len": playlist["length"],
                "playlist_files": playlist["files"],
                "playlist_uuid": self.music_list_uuid,
                "volume": self.player.volume,
                "position": self.player.get_position(),
                "length": self.player.get_length(),
                "playing": self.player.playing(),
                "state": state,
                "LastCard": last_card
            }
        else:
            self.music_ctrl = {
                "device": self.music_device,
                "mute": False,
                "status": "",
                "connected": False,
                "file": "",
                "song": {},
                "stream": {},
                "playlist": [],
                "playlist_pos": -1,
                "playlist_len": -1,
                "playlist_files": [],
                "playlist_uuid": "",
                "volume": 0.4,
                "position": -1,
                "length": -1,
                "playing": -1,
                "state": state,
                "type": "",
                "LastCard": ""
            }
        return self.music_ctrl

    def playback_status(self):
        """
        check which device is active (as rfid can change this in the background)
        """
        play_status = str(self.music_plays)
        play_type = self.music_ctrl["type"]
        play_position = str(self.music_list_p) + "/" + str(len(self.music_list))
        play_volume = str(self.music_ctrl["volume"])
        play_mute = str(self.music_ctrl["mute"])

        self.logging.info(
            "Playback Status: Play=" + play_status + " / Type=" + play_type + " / Pos=" + play_position +
            " / Vol=" + play_volume + " / Mute=" + play_mute)
