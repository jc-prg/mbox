import logging
import os
import threading
import time
import uuid

import modules.config_mbox as mbox
import modules.config_stage as stage
import modules.run_cmd as run_cmd
import modules.music_metadata as music_metadata


class MusicLoadMetadata:

    def __init__(self):
        self.album_data_structure = {
            "uuid": "",
            "artist": "",
            "album": "",
            "albumname": "",
            "albumpath": "",
            "albumlength": 0,
            "albumsize": 0,
            "compilation": False,
            "card_id": 0,
            "genre": [],
            "tracks": [],
            "track_count": 0,
            "error": [],
            "cover_images": {}
        }
        self.album_image_structure = {"active": "dir", "active_pos": 0, "upload": [], "dir": [], "track": []}

        self.data_keys = ["albums", "album_info", "artists", "files", "tracks"]

        self.logging = logging.getLogger("load-md")
        self.logging.setLevel(stage.logging_level)

    def reload_music(self, data, load_all=True, thread=""):
        """
        load metadata and images from files in music_dir
        """
        self.logging.info("reloadMusic: Start reloading music data: " + mbox.music_dir + " | all=" + str(load_all))
        run_cmd.file_logging_init()
        run_cmd.file_logging("----------------------------------------------")
        run_cmd.file_logging("reloadMusic: Start reloading music data: " + mbox.music_dir + " | all=" + str(load_all))

        keys_media = mbox.databases["music"]
        data_reload = {}
        for key in keys_media:
            data_reload[key] = {}

        # reload files incl. metadata and images -> tracks and files
        media_files_exist = data["files"].keys()
        media_files_reload = self.get_files_in_directory(mbox.music_dir)
        image_files_reload = self.get_files_in_directory(mbox.music_cover)

        files_amount = len(media_files_reload)
        files_count = 0
        files_loaded = 0
        files_error = {}

        message = "Starting reload (all=" + str(load_all) + ") - " + str(files_amount) + " files found."
        self.logging.info(message)
        run_cmd.file_logging(message)

        if not load_all:
            data_reload = self.get_current_without_errors(data_current=data)
            media_files_exist = data_reload["files"].keys()
            run_cmd.file_logging("- Removed files with errors from list of existing files (" + str(len(media_files_exist)) + ")")

        for path2file in media_files_reload:

            if not os.path.isfile(path2file):
                self.logging.info("- Read: " + path2file)
                run_cmd.file_logging("- Read: " + path2file)
                self.set_progress_information(count=files_count, total=len(media_files_reload), thread=thread, show=True)

            elif os.path.isfile(path2file) and self.check_if_format_supported(thread.supported_mpX, path2file) is True:
                file_uuid = str(uuid.uuid1())
                filename = path2file.replace(mbox.music_dir, "")
                files_count += 1
                self.set_progress_information(count=files_count, total=len(media_files_reload), thread=thread, show=False)

                file_exist = (filename in media_files_exist)
                file_read = (load_all or (not load_all and not file_exist))

                self.logging.debug(" . Check: read=" + str(file_read) + " | " + filename)
                run_cmd.file_logging(" . Check: read=" + str(file_read) + " | " + filename)

                if file_read:
                    files_loaded += 1

                    data_reload["files"][filename] = music_metadata.read_metadata(mbox.music_dir + filename)
                    data_reload["tracks"]["t_" + file_uuid] = data_reload["files"][filename]
                    data_reload["tracks"]["t_" + file_uuid]["uuid"] = "t_" + file_uuid
                    data_reload["files"][filename]["uuid"] = "t_" + file_uuid

                    if "#error" in data_reload["files"][filename]["artist"]:
                        files_error[filename] = data_reload["files"][filename]["artist"]

        self.logging.info("reloadMusic: loaded data from " + str(files_loaded) + " files (" + str(len(media_files_reload)) + ")")
        run_cmd.file_logging("reloadMusic: loaded data from " + str(files_loaded) + " files (" + str(len(media_files_reload)) + ")")

        # recreate album_infos based on tracks
        self.logging.info("reloadMusic: recreate album_infos based on tracks")
        data_reload["album_info"], data_reload["tracks"] = self.create_album_information(track_data=data_reload["tracks"])

        # recreate album hierarchy based on album info
        self.logging.info("reloadMusic: recreate album hierarchy")
        for album_uuid in data_reload["album_info"]:
            album_data = data_reload["album_info"][album_uuid]

            if album_data["artist"] not in data_reload["albums"]:
                data_reload["albums"][album_data["artist"]] = {}
            if album_data["albumname"] not in data_reload["albums"][album_data["artist"]]:
                data_reload["albums"][album_data["artist"]][album_data["albumname"]] = {}
                data_reload["albums"][album_data["artist"]][album_data["albumname"]]["uuid"] = album_uuid

            for track_uuid in data_reload["album_info"][album_uuid]["tracks"]:
                data_reload["tracks"][track_uuid]["album_uuid"] = album_uuid

        # recreate list of artists
        self.logging.info("reloadMusic: recreate list of artists")
        for track_uuid in data_reload["tracks"]:
            artist_name = data_reload["tracks"][track_uuid]["artist"]
            if "#error" not in artist_name:
                if artist_name not in data_reload["artists"]:
                    data_reload["artists"][artist_name] = {}
                if track_uuid not in data_reload["artists"][artist_name]:
                    data_reload["artists"][artist_name][track_uuid] = data_reload["tracks"][track_uuid]

        # reconnect cards information
        if "cards" in data:
            self.logging.info("reloadMusic: reconnect cards information")
            cards_temp = data["cards"]
            for album_uuid in data_reload["album_info"]:
                cards_temp, card_id = self.check_if_card_exists(data_cards=cards_temp,
                                                        album=data_reload["album_info"][album_uuid]["albumname"],
                                                        artist=data_reload["album_info"][album_uuid]["artist"],
                                                        uuid=album_uuid)
                data_reload["album_info"][album_uuid]["card_id"] = card_id
            data_reload["cards"] = cards_temp

        # reconnect playlist information - albums based on uuid or directory, tracks based on filename and path
        if "playlists" in data:
            self.logging.info("reloadMusic: reconnect playlist information")
            for playlist_uuid in data["playlists"]:
                position = 0
                for entry_uuid in data["playlists"][playlist_uuid]["tracks"]:
                    entry_ref = data["playlists"][playlist_uuid]["tracks_ref"][position]
                    check_uuid = self.check_if_entry_in_playlist(data_reload, entry_uuid=entry_uuid, entry_ref=entry_ref)
                    if check_uuid != "NOT FOUND" and check_uuid != entry_uuid:
                        data["playlists"][playlist_uuid]["tracks"][position] = check_uuid
                    position += 1
            data_reload["playlists"] = data["playlists"]

        # delete old cover files, if all entries should be reloaded (and reload was successful)
        if load_all:
            self.logging.info("reloadMusic: delete old cover files")
            for x in image_files_reload:
                if os.path.isfile(x):
                    os.remove(x)

        if files_error != {}:
            run_cmd.file_logging("reloadMusic: found files with errors:")
            for filename in files_error:
                run_cmd.file_logging(" - " + filename + " | " + files_error[filename])

        message = "Reload finished: " + mbox.music_dir + " | all=" + str(all) + " | albums=" + str(len(data["albums"]))
        self.logging.info(message)
        run_cmd.file_logging(message)
        return data_reload

    def reload_covers(self, data, thread=""):
        """
        Check for JPG files in the folder again without reloading the music
        """
        files = self.get_files_in_directory(mbox.music_dir)
        files_amount = len(files)
        files_count = 0
        files_img_found = 0
        files_percentage = 0

        self.logging.info("reload_covers: Start to scan for new cover images ...")
        run_cmd.file_logging_init()
        run_cmd.file_logging("----------------------------------------------")
        run_cmd.file_logging("reload_covers: Start to scan for new cover images ...")

        # remove old entries
        for key in data:
            data[key]["cover_images"]["dir"] = []

        # check list of files
        for filename in files:

            files_count += 1
            if not os.path.isfile(filename):
                self.set_progress_information(count=files_count, total=files_amount, thread=thread, show=True)
                self.logging.debug("Check Images: " + filename.replace(stage.data_dir, ""))
                run_cmd.file_logging("Check Images: " + filename.replace(stage.data_dir, ""))

            # check if image file in folder (and take last one as alternative cover)
            if os.path.isfile(filename) and self.check_if_format_supported(thread.supported_img, filename) is True:

                self.set_progress_information(count=files_count, total=files_amount, thread=thread, show=False)
                file_e = filename.replace("/", "_")
                for key in data:
                    # load_logging.debug(key+": "+data[key]["albumpath"])
                    if data[key]["albumpath"] in file_e or data[key]["albumpath"] in filename:
                        files_img_found += 1
                        file_e2 = filename.replace(mbox.music_dir, "")
                        self.logging.debug(" . Found: " + filename.replace(mbox.music_dir, ""))
                        run_cmd.file_logging(" . Found: " + filename.replace(mbox.music_dir, ""))
                        self.logging.debug(" . Found: " + key + " | " + data[key]["album"])
                        run_cmd.file_logging(" . Found: " + key + " | " + data[key]["album"])
                        data[key]["cover_images"]["dir"].append(file_e2)
                        data[key]["cover_images"]["active"] = "dir"

        self.logging.info("reloadCoverImages: found " + str(files_img_found) + " files (" + str(files_count) + ")")
        run_cmd.file_logging("reloadCoverImages: found " + str(files_img_found) + " files (" + str(files_count) + ")")
        return data

    def get_files_in_directory(self, data_directory):
        """
        get all files from directory
        don't return files, if a file ".dont-scan" exists in directory
        """
        command = "find -L " + data_directory + " -maxdepth 4"

        run_cmd.file_logging("----------------------------------------------")
        run_cmd.file_logging("Read files: " + command)
        self.logging.info("Read files: " + command)

        file_list, error = run_cmd.runCmd(command)
        files = file_list.splitlines()

        no_scan = []
        files_return = []
        if len(files) > 1:
            for directory in files:
                if ".dont-scan" in directory:
                    dir_parts = directory.split("/")
                    dir_parts = dir_parts[:-1]
                    no_scan.append("/".join(dir_parts))

            for filename in files:
                scan = True
                for entry in no_scan:
                    if entry in filename:
                        scan = False
                if scan is True:
                    files_return.append(filename)

        if len(no_scan) > 0:
            self.logging.info("Don't scan sub-directories: " + str(no_scan))
            run_cmd.file_logging("Don't scan sub-directories: " + str(no_scan))
        return files_return

    def get_album_from_path(self, file):
        """
        separate information from path
        """
        album = ""
        local_path = file.replace(mbox.music_dir, "")
        path_list = local_path.split("/")
        path_list.pop(len(path_list) - 1)
        for x in path_list:
            album = album + "_" + x
        self.logging.debug("Album from path: " + file + " -> " + album)
        return album

    def get_current_without_errors(self, data_current):
        """
        if only new files shall be loaded, the current data have to be prepare as base
        therefor all db entries with errors will be deleted as they will be detected again (if they still exist)
        """
        self.logging.info("Remove entries with errors for reload ...")
        run_cmd.file_logging("Remove entries with errors for reload ...")

        data_reload = {}
        logging_msg = []

        for key in self.data_keys:
            data_reload[key] = {}

        for x in data_current["albums"]:
            if "#error" in x:
                logging_msg.append("albums: " + x)
            else:
                data_reload["albums"][x] = data_current["albums"][x]

        for x in data_current["artists"]:
            if "#error" in x:
                logging_msg.append("artists: " + x)
            else:
                data_reload["artists"][x] = data_current["artists"][x]

        for x in data_current["files"]:
            if data_current["files"][x]["artist"] is not None:
                if "#error" in data_current["files"][x]["artist"]:
                    logging_msg.append(" - files:      " + x)
                else:
                    data_reload["files"][x] = data_current["files"][x]

        for x in data_current["tracks"]:
            if data_current["tracks"][x]["artist"] is not None:
                if "#error" in data_current["tracks"][x]["artist"]:
                    logging_msg.append(" - tracks:     " + x)
                else:
                    data_reload["tracks"][x] = data_current["tracks"][x]

        for x in data_current["album_info"]:
            if data_current["album_info"][x]["artist"] is not None:
                if "#error" in data_current["album_info"][x]["artist"]:
                    logging_msg.append(" - album_info: " + x)
                else:
                    data_reload["album_info"][x] = data_current["album_info"][x]

        for x in logging_msg:
            self.logging.debug(x)
            run_cmd.file_logging(x)

        return data_reload

    def set_progress_information(self, count, total, thread, show=True):
        """
        reload ... progress information
        """
        if count == 0:
            return
        files_percentage = float(count) / float(total) * 100
        if thread != "":
            thread.reload_progress = files_percentage
            thread.reload_time_required = time.time() - thread.reload_time_start
            thread.reload_time_left = thread.reload_time_required * (100 - files_percentage) / files_percentage
            if files_percentage == 100: thread.reload_time_left = 0
        if show:
            self.logging.debug("Reload progress: " + str(files_percentage) + "%")

    def create_album_information(self, track_data):
        """
        create album info from track data
        """
        album_info = {}
        album_dir = {}

        # recreate album_infos based on tracks: (1) get all paths from tracks
        for track in track_data:
            file_path = track_data[track]["file"]
            temp = file_path.split("/")
            file_name = temp[len(temp) - 1]
            file_path = file_path.replace(file_name, "")
            if "album_uuid" in track_data[track]:
                album_dir[file_path] = track_data[track]["album_uuid"]
            else:
                album_dir[file_path] = "NEW_ENTRY"

        # recreate album_infos based on tracks:
        #   (2) get album information from tracks and check if it's a compilation (more than 1 artist)
        for album_path in album_dir:
            self.logging.info("- Create album for "+album_path)

            album_uuid = album_dir[album_path]
            if album_uuid == "NEW_ENTRY":
                album_uuid = "a_" + str(uuid.uuid1())

            album_data = self.album_data_structure.copy()
            album_data["cover_images"] = self.album_image_structure.copy()
            album_data["tracks"] = []
            album_data["uuid"] = album_uuid
            album_data["albumpath"] = album_path

            album_data_error = self.album_data_structure.copy()
            album_data_error["cover_images"] = self.album_image_structure.copy()
            album_data_error["tracks"] = []
            album_data_error["uuid"] = album_uuid + "_error"
            album_data_error["albumpath"] = album_path

            track_count = 0
            track_count_error = 0

            for track_uuid in track_data:
                if album_path in track_data[track_uuid]["file"]:
                    track_info = track_data[track_uuid]

                    if "#error" in track_info["artist"]:
                        track_count_error += 1
                        album_data_error["album"] = track_info["album"]
                        album_data_error["albumname"] = track_info["album"]
                        album_data_error["artist"] = track_info["artist"]

                        if "error" in track_info: album_data_error["error"].append(track_info["error"])

                        album_data_error["tracks"].append(track_uuid)
                        album_data_error["track_count"] = track_count_error

                    else:
                        track_count += 1
                        if track_count == 1:
                            album_data["album"] = track_info["album"]
                            album_data["albumname"] = track_info["album"]
                            album_data["artist"] = track_info["artist"]

                        elif album_data["artist"] != track_info["artist"] and "#error" not in track_info["artist"]:
                            album_data["artist"] = "Compilation"
                            album_data["compilation"] = True

                        elif "#error" not in track_info["artist"] and track_info["album"] == "":
                            album_data["album"] = track_info["album"]
                            album_data["albumname"] = track_info["album"]
                            album_data["artist"] = track_info["artist"]

                        album_data["tracks"].append(track_uuid)
                        album_data["track_count"] = track_count
                        if "filesize" in track_info:
                            album_data["albumsize"] += float(track_info["filesize"])
                        if "length" in track_info:
                            album_data["albumlength"] += float(track_info["length"])
                        if "error" in track_info:
                            album_data["error"].append(track_info["error"] + " (" + track_info["file"] + ")")
                        if "genre" in track_info and track_info["genre"] not in album_data["genre"]:
                            album_data["genre"].append(track_info["genre"])
                        if "cover_images" in track_info:
                            if "dir" in track_info["cover_images"]:   album_data["cover_images"]["dir"].extend(
                                track_info["cover_images"]["dir"])
                            if "track" in track_info["cover_images"]: album_data["cover_images"]["track"].extend(
                                track_info["cover_images"]["track"])

            if len(album_data["cover_images"]["dir"]) == 0 and len(album_data["cover_images"]["track"]) > 0:
                album_data["cover_images"]["active"] = "track"

            album_info[album_uuid] = album_data

            if album_data_error["artist"] != "":
                album_info[album_uuid + "_error"] = album_data_error

        for album_uuid in album_info:

            # sort tracks in album by key "sort"
            sorted_tracks = {}
            album_data = album_info[album_uuid]
            for track_uuid in album_data["tracks"]:
                if track_uuid in track_data:
                    track = track_data[track_uuid]
                    if "sort" not in track:
                        track["sort"] = "00000"
                    if track["sort"] not in sorted_tracks:
                        sorted_tracks[track["sort"]] = []
                    sorted_tracks[track["sort"]].append(track_uuid)

            # add position of track to track data as "sort_pos"
            track_list_sorted = []
            track_list_pos = 0
            for key in sorted(sorted_tracks.keys()):
                track_list_pos += 1
                track_list_sorted.extend(sorted_tracks[key])
                for track in sorted_tracks[key]:
                    track_data[track]["sort_pos"] = track_list_pos

            album_info[album_uuid]["tracks"] = track_list_sorted.copy()

        return album_info.copy(), track_data.copy()

    def check_if_entry_in_playlist(self, data, entry_uuid, entry_ref):
        """
        check album and track list, if track or file exists
        """
        check_uuid = "NOT FOUND"
        check_ref = "NOT FOUND"

        if entry_uuid.startswith("a_"):
            if entry_uuid in data["album_info"]:
                check_uuid = entry_uuid
            else:
                for album_uuid in data["album_info"]:
                    if data["album_info"][album_uuid]["albumpath"] == entry_ref:
                        check_uuid = album_uuid
                        check_ref = data["album_info"][album_uuid]["albumpath"]

        elif entry_uuid.startswith("t_"):
            if entry_uuid in data["tracks"]:
                check_uuid = entry_uuid
            else:
                for track_uuid in data["tracks"]:
                    if data["tracks"][track_uuid]["file"] == entry_ref:
                        check_uuid = track_uuid
                        check_ref = data["tracks"][track_uuid]["file"]

        self.logging.debug("checkIfPlaylistEntryExists : " + entry_uuid + " -> " + check_uuid + "/" + check_ref)
        return check_uuid

    @staticmethod
    def check_if_card_exists(data_cards, album, artist, uuid):
        """
        Check for JPG files in the folder again without reloading the music
        """
        update_time = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
        for card_id in data_cards:
            # check if card
            if "," in card_id:
                # if data error
                if len(data_cards[card_id]) < 3: return data_cards, ""
                # check if album and artist exist
                if data_cards[card_id][1] == album and data_cards[card_id][2] == artist:
                    # replace old UUID by current UUID
                    data_cards[card_id][0] = uuid
                    if len(data_cards[card_id]) > 3:
                        # add date when replaced UUID last time
                        data_cards[card_id][3] = update_time
                    else:
                        data_cards[card_id].append(update_time)
                    # return data and card_id
                    return data_cards, card_id
        return data_cards, ""

    @staticmethod
    def check_if_format_supported(supported_formats, file_name):
        """
        check if file extension is one of the supported formats
        """
        supported = False
        for file_extension in supported_formats:
            if file_extension in file_name:
                supported = True
        return supported


class MusicLoadingThread(threading.Thread):

    def __init__(self, database, start_time):
        """
        set initial values to vars and start pygame.mixer
        """

        threading.Thread.__init__(self)
        self.stopProcess = False
        self.start_time = start_time

        self.reload_all = False
        self.reload_new = False
        self.reload_img = False
        self.reload_progress = 0
        self.reload_time_start = 0
        self.reload_time_left = 0
        self.music_database = database

        self.supported_img = [".jpg", ".jpeg", ".JPG", ".png", ".PNG"]
        self.supported_mp3 = [".mp3", ".MP3"]
        self.supported_mp4 = [".mp4", ".m4a", ".MP4",
                              ".M4A"]  # .M4P metadata can be read but music is DRM protected -> convert to use this file format
        self.supported_mpX = [".mp3", ".MP3", ".mp4", ".m4a", ".MP4", ".M4A"]

        self.load = MusicLoadMetadata()

        self.store_data = None
        self.logging = logging.getLogger("load")
        self.logging.setLevel(stage.logging_level)

    def run(self):
        """
        control reload of music data
        """
        self.logging.info("Start Music-Load ... " + self.start_time)
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
                self.logging.info("Starting Reload ALL")

                self.store_data = self.music_database.read_group("music")
                self.store_data = self.load.reload_music(self.store_data, True, self)
                for key in self.store_data:
                    self.music_database.write(key, self.store_data[key])

            # check if new files and load data for new files
            elif self.reload_new:
                self.logging.info("Starting Reload NEW")

                self.store_data = self.music_database.read_group("music")
                self.store_data = self.load.reload_music(self.store_data, False, self)
                for key in self.store_data:
                    self.music_database.write(key, self.store_data[key])

            # check if new images in directories available
            elif self.reload_img:
                self.logging.info("Starting Reload IMAGES")

                self.store_data = self.music_database.read("album_info")
                self.store_data = self.load.reload_covers(self.store_data, self)

                for key in self.store_data:
                    self.music_database.write("album_info", self.store_data)

            # clean progress and reload request
            if self.reload_all or self.reload_new or self.reload_img:
                self.music_database.fill_cache()
                self.music_database.changed_data = False

                self.reload_progress = 0
                self.reload_time_start = 0

                self.reload_all = False
                self.reload_new = False
                self.reload_img = False

            time.sleep(2)

        self.logging.info("Stopped Music-Load.")

    def stop(self):
        """
        Stop thread to reload music data
        """
        self.stopProcess = True
