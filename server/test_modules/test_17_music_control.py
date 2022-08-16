import time
import os
import logging
import shutil
from unittest import TestCase

import modules.music_control as music_ctrl
import modules.config_mbox as mbox
import modules.config_stage as stage
import modules.server_init as server_init
import modules.server_cmd as server_cmd
import modules.run_cmd as run_cmd
import modules.json_db as json_db


stage.log_filename_data = "/tmp/load_metadata.log"
mbox.log_connection = "/tmp/log_connection.log"
backup_dir = "../test_data/couchdb_backup/"


class TestMusicControlThread(TestCase):
    def start_threads(self):
        # init all required threads
        server_init.start_modules(speak_msg=False)
        self.vlc = server_init.thread_vlc
        self.player = server_init.thread_player
        self.couch = server_init.thread_couch
        self.speak = server_init.thread_speak
        self.podcast = server_init.thread_podcast
        self.music_load = server_init.thread_music_load
        self.music_control = music_ctrl.MusicControlThread("music_box", self.couch, self.player, self.speak,
                                                           self.podcast, "time_since_start")
        self.music_control.wait_for_other_services = False
        self.mbox_music_dir = mbox.music_dir
        self.mbox_music_cover = mbox.music_cover
        self.mbox_music_cover_upload = mbox.music_cover_upload
        self.mbox_log_connection = mbox.log_connection

        # set test specific vars
        working_dir = os.getcwd()
        stage.data_backup = os.path.join(os.getcwd(), backup_dir)
        stage.data_dir = os.path.join(os.getcwd(), "../test_data")
        mbox.music_dir = os.path.join(working_dir, "../test_data/music")
        mbox.music_cover = os.path.join(working_dir, "../test_data/cover")
        mbox.music_cover_upload = os.path.join(working_dir, "../test_data/cover_upload")
        mbox.log_connection = "/tmp/check_log_connection"

    def end_threads(self):
        # close threads
        self.music_control.wait_for_other_services = False
        self.music_control.stop()
        self.api_calls = None
        server_init.end_modules(raise_error=False)

        # reset vars
        mbox.music_dir = self.mbox_music_dir
        mbox.music_cover = self.mbox_music_cover
        mbox.music_cover_upload = self.mbox_music_cover_upload
        mbox.log_connection = self.mbox_log_connection

    def load_data(self):
        self.api_calls = server_cmd.ServerApi(self.couch, self.podcast, self.music_control, self.music_load, self.speak)
        self.api_calls.load("all")
        time.sleep(0.5)
        while self.api_calls.music_load.reload_all:
            print(".")
            time.sleep(1)
        print("-> albums: " + str(len(self.couch.read("albums"))))
        print("-> tracks: " + str(len(self.couch.read("tracks"))))
        print("-> files: " + str(len(self.couch.read("files"))))

    def test_run(self):
        self.start_threads()
        self.music_control_test = music_ctrl.MusicControlThread("music_box", self.couch, self.player, self.speak,
                                                                self.podcast, "time_since_start")
        self.assertEqual(self.music_control_test.running, None)
        self.music_control_test.start()
        self.assertEqual(self.music_control_test.running, True)
        self.assertEqual(self.music_control_test.music_plays, -1)
        self.music_control_test.wait_for_other_services = False
        time.sleep(2)
        self.assertTrue(self.music_control_test.music_plays != -1)
        self.music_control_test.stop()
        self.end_threads()

    def test_stop(self):
        self.start_threads()
        self.music_control_test = music_ctrl.MusicControlThread("music_box", self.couch, self.player, self.speak,
                                                                self.podcast, "time_since_start")
        self.assertEqual(self.music_control_test.running, None)
        self.music_control_test.start()
        time.sleep(2)
        self.assertEqual(self.music_control_test.running, True)
        self.music_control_test.wait_for_other_services = False
        self.music_control_test.stop()
        time.sleep(1)
        self.assertEqual(self.music_control_test.running, False)
        self.assertEqual(self.music_control_test.player.running, False)
        self.end_threads()

    def test_volume(self):
        self.start_threads()
        self.music_control.volume(40)
        self.assertEqual(self.music_control.music_ctrl["volume"], 40)
        self.assertEqual(self.vlc.player.audio_get_volume(), (self.vlc.volume_factor * 40))
        self.music_control.volume(0.5)
        self.assertEqual(self.music_control.music_ctrl["volume"], 0.5)
        self.assertEqual(self.vlc.player.audio_get_volume(), (self.vlc.volume_factor * 50))
        self.music_control.volume(120)
        self.assertEqual(self.music_control.music_ctrl["volume"], 120)
        self.assertEqual(self.vlc.player.audio_get_volume(), (self.vlc.volume_factor * 100))
        self.end_threads()

    def test_volume_up(self):
        self.start_threads()
        self.music_control.volume(40)
        self.assertEqual(self.music_control.music_ctrl["volume"], 40)
        self.assertEqual(self.vlc.player.audio_get_volume(), (self.vlc.volume_factor * 40))
        self.music_control.volume_up("up")
        self.assertEqual(self.music_control.music_ctrl["volume"], 45)
        self.assertEqual(self.vlc.player.audio_get_volume(), (self.vlc.volume_factor * 45))
        self.music_control.volume_up("up")
        self.assertEqual(self.music_control.music_ctrl["volume"], 50)
        self.assertEqual(self.vlc.player.audio_get_volume(), (self.vlc.volume_factor * 50))
        self.music_control.volume_up("down")
        self.assertEqual(self.music_control.music_ctrl["volume"], 45)
        self.assertEqual(self.vlc.player.audio_get_volume(), (self.vlc.volume_factor * 45))

        self.music_control.volume(100)
        self.assertEqual(self.music_control.music_ctrl["volume"], 100)
        self.assertEqual(self.vlc.player.audio_get_volume(), (self.vlc.volume_factor * 100))
        self.music_control.volume_up("up")
        self.assertEqual(self.music_control.music_ctrl["volume"], 100)
        self.assertEqual(self.vlc.player.audio_get_volume(), (self.vlc.volume_factor * 100))

        self.music_control.volume(0)
        self.assertEqual(self.music_control.music_ctrl["volume"], 0)
        self.assertEqual(self.vlc.player.audio_get_volume(), (self.vlc.volume_factor * 0))
        self.music_control.volume_up("down")
        self.assertEqual(self.music_control.music_ctrl["volume"], 0)
        self.assertEqual(self.vlc.player.audio_get_volume(), (self.vlc.volume_factor * 0))
        self.end_threads()

    def test_volume_mute(self):
        self.start_threads()
        self.music_control.volume(40)
        self.assertEqual(self.music_control.music_ctrl["volume"], 40)
        self.assertEqual(self.music_control.music_ctrl["mute"], False)
        self.assertEqual(self.vlc.player.audio_get_volume(), (self.vlc.volume_factor * 40))

        self.music_control.volume_mute()
        self.assertEqual(self.music_control.music_ctrl["volume"], 40)
        self.assertEqual(self.music_control.music_ctrl["mute"], True)

        self.music_control.volume_mute()
        self.assertEqual(self.music_control.music_ctrl["volume"], 40)
        self.assertEqual(self.music_control.music_ctrl["mute"], False)

        self.music_control.volume_mute()
        self.assertEqual(self.music_control.music_ctrl["volume"], 40)
        self.assertEqual(self.music_control.music_ctrl["mute"], True)

        self.music_control.volume_mute(True)
        self.assertEqual(self.music_control.music_ctrl["volume"], 40)
        self.assertEqual(self.music_control.music_ctrl["mute"], True)

        self.end_threads()

    def test_playlist_info(self):
        self.start_threads()
        self.load_data()

        # restart after loading data
        self.music_control.stop()
        self.music_control.wait_for_other_services = False
        self.music_control.start()

        # start playback and check if saved
        album_key = ""
        data = self.couch.read("album_info")
        data_files = self.couch.read("files")
        for key in data:
            album_key = key
        self.music_control.playlist_load_uuid(album_key)
        time.sleep(3)
        self.assertEqual(self.music_control.music_ctrl["playing"], 1)
        self.assertEqual(self.music_control.music_ctrl["playlist_pos"], 1)

        data_info = self.music_control.playlist_info()
        self.assertEqual(data_info["length"], len(data[album_key]["tracks"]))
        self.assertEqual(data_info["position"], 1)
        for file in data_info["list"]:
            if "info" in file:
                del file["info"]
            self.assertEqual(file, data_files[file["file"]])
            self.assertTrue(file["uuid"] in data[album_key]["tracks"])

        self.end_threads()

    def test_playlist_load_uuid(self):
        self.start_threads()
        self.load_data()

        # restart after loading data
        self.music_control.stop()
        self.music_control.wait_for_other_services = False
        self.music_control.start()

        # start playback and check if saved
        album_key = ""
        data = self.couch.read("album_info")
        for key in data:
            album_key = key
        self.music_control.playlist_load_uuid(album_key)
        time.sleep(3)
        if data[album_key]["tracks"]:
            self.assertEqual(self.music_control.music_device, "music_box")
            self.assertEqual(self.music_control.music_list_p, 1)
            # self.assertTrue(len(self.music_control.music_list) > 0)
            self.assertEqual(self.music_control.music_ctrl["playing"], 1)
            self.assertEqual(self.music_control.music_ctrl["playlist_pos"], 1)
        else:
            self.assertTrue(len(self.music_control.music_list) == 0)

        self.music_control.stop()
        self.end_threads()

    def test_playlist_load_rfid(self):
        self.start_threads()
        self.load_data()

        # restart after loading data
        self.music_control.stop()
        self.music_control.wait_for_other_services = False
        self.music_control.start()

        # start playback and check if saved
        album_key = ""
        count = 0
        data = self.couch.read("album_info")
        data_cards = self.couch.read("cards")
        for key in data:
            count += 1
            album_card = "1,2,3," + str(count)
            data[key]["card_id"] = album_card
            data_cards[album_card] = [key, "", "", ""]
            print(key + " " + album_card)
        self.couch.write("album_info", data)
        self.couch.write("cards", data_cards)
        print(self.couch.read_cache("cards"))

        self.music_control.music_ctrl["LastCard"] = ""
        for card_id in data_cards:
            print(card_id)
            mbox.rfid_ctrl["cardUID"] = card_id
            # the command is called in the loop of "def run(self)" once a second
            # self.music_control.playlist_load_rfid()
            time.sleep(2)
            card_uuid = data_cards[card_id][0]
            self.assertEqual(self.music_control.music_ctrl["LastCard"], card_uuid)
            if data[card_uuid]["tracks"]:
                print(self.music_control.music_ctrl)
                self.assertEqual(self.music_control.music_ctrl["playing"], 1)
                self.assertEqual(self.music_control.music_ctrl["playlist_pos"], 1)
                self.assertEqual(self.music_control.music_ctrl["LastCard"], data_cards[card_id][0])
                time.sleep(3)

        self.music_control.stop()
        self.end_threads()

    def test_playlist_next(self):
        self.start_threads()
        self.load_data()

        # restart after loading data
        self.music_control.stop()
        self.music_control.wait_for_other_services = False
        self.music_control.start()

        # start playback and check if saved
        album_key = ""
        data = self.couch.read("album_info")
        for key in data:
            if "error" not in key:
                album_key = key
        self.music_control.playlist_load_uuid(album_key)
        time.sleep(1)
        print(data[album_key])
        if data[album_key]["tracks"]:
            self.assertEqual(self.music_control.music_device, "music_box")
            self.assertEqual(self.music_control.music_list_p, 1)
            # self.assertTrue(len(self.music_control.music_list) > 0)
            self.assertEqual(self.music_control.music_ctrl["playing"], 1)
            self.assertEqual(self.music_control.music_ctrl["playlist_pos"], 1)
        else:
            self.assertTrue(len(self.music_control.music_list) == 0)

        # go step forward or backward
        self.music_control.playlist_next(step=1)
        time.sleep(2)
        self.assertEqual(self.music_control.music_ctrl["playing"], 1)
        self.assertEqual(self.music_control.music_ctrl["playlist_pos"], 2)

        self.music_control.playlist_next(step=-1)
        time.sleep(1)
        self.assertEqual(self.music_control.music_ctrl["playing"], 1)
        self.assertEqual(self.music_control.music_ctrl["playlist_pos"], 1)

        self.music_control.stop()
        self.end_threads()

    def test_playlist_by_uuid(self):
        self.start_threads()
        self.load_data()

        # restart after loading data
        self.music_control.stop()
        self.music_control.wait_for_other_services = False
        self.music_control.start()

        # check album_info
        data = self.couch.read("album_info")
        for key in data:
            album_key = key
            album_tracks = data[album_key]["tracks"]
            self.assertEqual(self.music_control.playlist_by_uuid(album_key), album_tracks)

        self.assertEqual(self.music_control.playlist_by_uuid("a_does-not-exist"), [])
        self.assertEqual(self.music_control.playlist_by_uuid("f_does-not-exist"), [])

        self.end_threads()

    def test_metadata_by_filename(self):
        self.start_threads()
        self.load_data()

        # restart after loading data
        self.music_control.stop()
        self.music_control.wait_for_other_services = False
        self.music_control.start()

        # data
        data = self.couch.read("files")
        for key in data:
            self.assertEqual(data[key], self.music_control.metadata_by_filename(key))
        data = self.couch.read("radio")
        for key in data:
            self.assertEqual({}, self.music_control.metadata_by_filename(key))

        self.end_threads()

    def test_metadata_by_uuid(self):
        self.start_threads()
        self.load_data()

        # restart after loading data
        self.music_control.stop()
        self.music_control.wait_for_other_services = False
        self.music_control.start()

        # data
        data = self.couch.read("tracks")
        for key in data:
            self.assertEqual(data[key], self.music_control.metadata_by_uuid(key))
        data = self.couch.read("radio")
        for key in data:
            self.assertEqual({}, self.music_control.metadata_by_uuid(key))

        self.end_threads()

    def test_control_data_update(self):
        self.start_threads()
        self.load_data()

        # restart after loading data
        self.music_control.stop()
        self.music_control.wait_for_other_services = False
        self.music_control.start()

        # start playback and check if saved
        album_key = ""
        data = self.couch.read("album_info")
        for key in data:
            album_key = key
        self.music_control.playlist_load_uuid(album_key)
        time.sleep(3)

        data = self.music_control.control_data_update()
        data["position"] = -1
        data_compare = self.music_control.music_ctrl
        data_compare["position"] = -1
        self.assertEqual(data["playing"], 1)
        self.assertEqual(data["mute"], False)
        self.assertEqual(data, data_compare)

        self.end_threads()

    def test_control_data_create(self):
        self.start_threads()
        self.load_data()

        # restart after loading data
        self.music_control.stop()
        self.music_control.wait_for_other_services = False
        self.music_control.start()
        music_ctrl_keys = ["device", "mute", "status", "connected", "file", "song", "stream",
                           "playlist", "playlist_pos", "playlist_len", "playlist_files", "playlist_uuid",
                           "volume", "position", "length", "playing", "player_status", "state", "type",
                           "LastCard"]

        data = self.music_control.control_data_create(state="Started")
        for key in music_ctrl_keys:
            self.assertTrue(key in data)
        self.assertEqual(data["state"], "Started")
        self.assertEqual(data["song"], {})
        self.assertEqual(data["playing"], -1)

        self.end_threads()

    def test_playback_status_save(self):
        self.start_threads()
        self.load_data()

        self.music_control.stop()
        self.music_control.wait_for_other_services = False
        self.music_control.start()

        # clean up from last start
        data = self.couch.read("status")
        data["_test-active"] = True
        data["_saved"] = 0
        self.couch.write("status", data)
        time.sleep(2)

        # check if another instance is running
        data = self.couch.read("status")
        time_saved = ""
        time_saved_2 = ""
        if "_saved" in data:
            time_saved = data["_saved"]
        time.sleep(4)
        data = self.couch.read("status")
        if "_saved" in data:
            time_saved_2 = data["_saved"]
        if time_saved != time_saved_2:
            print("!!! Test failed due to in parallel running instance !!!")
            print(str(time_saved) + "-" + str(time_saved_2))
            self.assertEqual(time_saved, time_saved_2)

        # initial save status
        self.music_control.volume(50)
        self.assertEqual(self.music_control.music_ctrl["volume"], 50)
        self.assertEqual(self.music_control.player.volume, 50)
        self.music_control.playback_status_save(test=True)
        data = self.couch.read("status")
        self.assertTrue("_saved" in data)
        self.assertEqual(data["music"]["volume"], 50)
        time.sleep(3)

        # update save status
        self.music_control.volume(60)
        self.assertEqual(self.music_control.music_ctrl["volume"], 60)
        self.assertEqual(self.music_control.player.volume, 60)
        self.music_control.playback_status_save(test=True)
        data = self.couch.read("status")
        self.assertTrue("_saved" in data)
        self.assertEqual(data["music"]["volume"], 60)
        time.sleep(1)

        # update save status < 3 sek
        self.music_control.volume(70)
        self.assertEqual(self.music_control.music_ctrl["volume"], 70)
        self.assertEqual(self.music_control.player.volume, 70)
        self.music_control.playback_status_save(test=True)
        data = self.couch.read("status")
        self.assertTrue("_saved" in data)
        self.assertEqual(data["music"]["volume"], 60)

        # update save status > 3 s
        time.sleep(3)
        self.music_control.playback_status_save(test=True)
        data = self.couch.read("status")
        self.assertTrue("_saved" in data)
        self.assertEqual(data["music"]["volume"], 70)

        # start playback and check if saved
        album_key = ""
        data = self.couch.read("album_info")
        for key in data:
            if "error" not in key and len(data[key]["tracks"]) > 0:
                album_key = key
        print(album_key)

        self.music_control.playlist_load_uuid(album_key)
        time.sleep(4)
        self.music_control.playback_status_save(test=True)
        data = self.couch.read("status")
        self.assertTrue("_saved" in data)

        self.assertEqual(data["music"]["playing"], 1)
        self.assertEqual(data["music"]["song"]["album_uuid"], album_key)

        data = self.couch.read("status")
        data["_test-active"] = False
        data["_saved"] = ""
        self.couch.write("status", data)

        self.music_control.stop()
        self.end_threads()

    def test_playback_status_logging(self):
        pass
