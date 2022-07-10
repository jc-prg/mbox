import time
import os
import logging
from unittest import TestCase

import modules.config_mbox as mbox
import modules.config_stage as stage
import modules.server_init as server_init
import modules.server_cmd as server_cmd
import modules.run_cmd as run_cmd

working_dir = os.getcwd()
podcast_test_url = "https://raw.githubusercontent.com/jc-prg/mbox/dev/test_data/test_podcast/test_podcast.xml"
podcast_test_uuid = "r_1234-abcd"
podcast_test_data = {podcast_test_uuid: {
            "title": "test-radio",
            "stream_url": podcast_test_url,
            "stream_url2": "",
            "description": "test radio description"
        }}


class TestServerApi(TestCase):
    def start_threads(self):
        server_init.start_modules(speak_msg=False)
        self.api_calls = server_cmd.ServerApi(server_init.thread_couch, server_init.thread_podcast,
                                              server_init.thread_music_ctrl, server_init.thread_music_load,
                                              server_init.thread_speak)
        self.api_calls.music_ctrl.wait_for_other_services = False
        self.api_calls.music_ctrl.music_list = []
        self.vlc = server_init.thread_vlc
        self.player = server_init.thread_player
        self.couch = server_init.thread_couch
        self.music_ctrl = server_init.music_ctrl
        self.music_load = server_init.music_load

        self.mbox_music_dir = mbox.music_dir
        self.mbox_music_cover = mbox.music_cover
        self.mbox_music_cover_upload = mbox.music_cover_upload
        self.mbox_log_connection = mbox.log_connection

        mbox.music_dir = os.path.join(working_dir, "../test_data/music")
        mbox.music_cover = os.path.join(working_dir, "../test_data/cover")
        mbox.music_cover_upload = os.path.join(working_dir, "../test_data/cover_upload")
        mbox.log_connection = "/tmp/check_log_connection"

    def end_threads(self):
        self.api_calls = None
        server_init.end_modules(raise_error=False)

        mbox.music_dir = self.mbox_music_dir
        mbox.music_cover = self.mbox_music_cover
        mbox.music_cover_upload = self.mbox_music_cover_upload
        mbox.log_connection = self.mbox_log_connection

    def clean_db(self):
        self.couch.write("album_info", {})
        self.couch.write("albums", {})
        self.couch.write("tracks", {})
        self.couch.write("files", {})
        self.couch.write("artists", {})
        self.couch.write("radio", {})
        self.couch.write("playlists", {})
        self.couch.write("cards", {})

    def load_data(self):
        print("Load Album Data")
        self.clean_db()
        self.api_calls.load("all")
        time.sleep(0.5)
        while self.api_calls.music_load.reload_all:
            print(".")
            time.sleep(1)
        print("-> albums: " + str(len(self.couch.read("albums"))))
        print("Create Test Podcast")
        self.couch.write("radio", podcast_test_data)
        print("-> radio: " + str(len(self.couch.read("radio"))))

    def test_response_error(self):
        self.fail()

    def test_response_start(self):
        self.fail()

    def test_response_end(self):
        self.fail()

    def test_status(self):
        self.start_threads()
        data = self.api_calls.status()

        self.assertTrue("API" in data and "REQUEST" in data and "STATUS" in data)
        self.assertTrue("error" not in data["REQUEST"])
        self.assertTrue("load_data" in data["STATUS"])
        self.assertTrue("playback" in data["STATUS"])
        self.assertTrue("statistic" in data["STATUS"])
        self.assertTrue("system" in data["STATUS"])
        self.assertTrue("error" not in data["REQUEST"])
        self.assertEqual(data["REQUEST"]["c-name"], "status")
        self.assertEqual(data["REQUEST"]["status"], "success")
        self.assertNotEqual(data["STATUS"]["playback"]["playing"], 1)
        self.assertEqual(data["STATUS"]["playback"]["volume"], self.player.volume/100)

        self.end_threads()

    def test_volume(self):
        self.start_threads()
        volume = self.player.volume
        if volume < 1:
            volume = volume * 100
        print(str(volume))
        data = self.api_calls.volume("up")
        self.assertEqual(data["STATUS"]["playback"]["volume"], (volume + 5)/100)
        data = self.api_calls.volume("down")
        self.assertEqual(data["STATUS"]["playback"]["volume"], volume/100)
        data = self.api_calls.volume("set:50")
        self.assertEqual(data["STATUS"]["playback"]["volume"], 0.5)
        data = self.api_calls.volume("set:60")
        self.assertEqual(data["STATUS"]["playback"]["volume"], 0.6)
        self.end_threads()

    def test_play(self):
        self.start_threads()
        self.load_data()
        data = self.couch.read("album_info")
        test_key = ""
        for key in data:
            if "Unknown" not in data[key]["artist"] and "error" not in key:
                test_key = key
        test_uuid = test_key
        test_uuid_track = data[test_key]["tracks"][0]

        print("Test album: "+str(test_key))
        self.api_calls.play(uuid=test_uuid)
        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playing"], 1)
        self.assertEqual(data["STATUS"]["playback"]["song"]["album_uuid"], test_uuid)
        time.sleep(2)

        print("Test track: "+str(test_uuid_track))
        self.api_calls.play(uuid=test_uuid_track)
        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playing"], 1)
        self.assertEqual(data["STATUS"]["playback"]["song"]["uuid"], test_uuid_track)
        time.sleep(2)

        self.end_threads()

    def test_play_position(self):
        self.fail()

    def test_pause(self):
        self.start_threads()
        self.load_data()
        data = self.couch.read("album_info")
        test_key = ""
        for key in data:
            if "Unknown" not in data[key]["artist"] and "error" not in key:
                test_key = key
        test_uuid = test_key
        test_uuid_track = data[test_key]["tracks"][0]

        print("Test album: "+str(test_key))
        self.api_calls.play(uuid=test_uuid)
        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playing"], 1)
        self.assertEqual(data["STATUS"]["playback"]["song"]["album_uuid"], test_uuid)

        self.api_calls.pause()
        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playing"], 0)
        self.assertEqual(data["STATUS"]["playback"]["song"]["album_uuid"], test_uuid)

        self.api_calls.pause()
        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playing"], 1)
        self.assertEqual(data["STATUS"]["playback"]["song"]["album_uuid"], test_uuid)
        self.end_threads()

    def test_stop(self):
        self.start_threads()
        self.load_data()
        data = self.couch.read("album_info")
        test_key = ""
        for key in data:
            if "Unknown" not in data[key]["artist"] and "error" not in key:
                test_key = key
        test_uuid = test_key
        test_uuid_track = data[test_key]["tracks"][0]

        print("Test album: "+str(test_key))
        self.api_calls.play(uuid=test_uuid)
        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playing"], 1)
        self.assertEqual(data["STATUS"]["playback"]["song"]["album_uuid"], test_uuid)

        self.api_calls.stop()
        time.sleep(2)
        data = self.api_calls.status()
        print(data["STATUS"]["playback"])
        self.assertEqual(data["STATUS"]["playback"]["playing"], 0)
        self.assertTrue(data["STATUS"]["playback"]["status"] == "State.Ended" or
                        data["STATUS"]["playback"]["status"] == "")
        self.assertEqual(data["STATUS"]["playback"]["song"], {})

        self.end_threads()

    def test_next(self):
        self.fail()

    def test_last(self):
        self.fail()

    def test_jump(self):
        self.fail()

    def test_read_db(self):
        self.fail()

    def test_read_entry(self):
        self.fail()

    def test_edit(self):
        self.fail()

    def test_delete(self):
        self.fail()

    def test_add(self):
        self.fail()

    def test_images(self):
        self.fail()

    def test_playlist_items(self):
        self.fail()

    def test_cards(self):
        self.fail()

    def test_card_info(self):
        self.fail()

    def test_card_set(self):
        self.fail()

    def test_speak_message(self):
        self.start_threads()
        data = self.api_calls.speak_message("STARTING")
        self.assertTrue("error" not in data["REQUEST"])
        self.assertTrue("STARTING" in data["REQUEST"]["command"])
        data = self.api_calls.speak_message("STARTING-XX")
        self.assertTrue("error" in data["REQUEST"])
        self.assertTrue("STARTING-XX" in data["REQUEST"]["command"])
        self.end_threads()

    def test_set_button(self):
        self.fail()

    def test_button_error(self):
        self.fail()

    def test_backup(self):
        self.fail()

    def test_load(self):
        """
        in progress
        ??? Maybe move check if data are correct to -> test_16_load!
        -> bugfix load of info, e.g album != "" (use directory name instead)
        -> bugfix load of artists, should include relevant albums
        -> check if image of 'Erlkönig' is added (seems not to be)
        -> add another album for reload or empty db and reload?
        -> ensure card-data are still valid after reload
        -> add images and check reload of images
        -< NOT HERE: check several file types and metadata extraction -> for test_15_music_metadata
        """
        self.start_threads()
        self.clean_db()

        self.assertEqual(self.couch.read("album_info"), {})
        self.assertEqual(self.couch.read("albums"), {})
        self.assertEqual(self.couch.read("tracks"), {})
        self.assertEqual(self.couch.read("files"), {})
        self.assertEqual(self.couch.read("artists"), {})
        self.assertEqual(self.couch.read("radio"), {})
        self.assertEqual(self.couch.read("cards"), {})
        self.assertEqual(self.couch.read("playlists"), {})

        print("--- ALL")
        data = self.api_calls.load("all")
        self.assertTrue(self.api_calls.music_load.reload_all)
        time.sleep(0.5)
        data = self.api_calls.status()
        self.assertTrue(data["STATUS"]["load_data"]["reload_all"])
        while self.api_calls.music_load.reload_all:
            print(". "+str(data["STATUS"]["load_data"]["reload_progress"]))
            time.sleep(1)
        print("album_info: " + str(len(self.couch.read("album_info"))))
        self.assertTrue(len(self.couch.read("album_info")) >= 3)
        data = self.couch.read("album_info")
        for uuid in data:
            print(str(uuid)+": "+str(data[uuid]))
            self.assertTrue(uuid != "")
        print("albums: " + str(len(self.couch.read("albums"))))
        self.assertTrue(len(self.couch.read("albums")) >= 3)
        data = self.couch.read("albums")
        for uuid in data:
            print(str(uuid)+": "+str(data[uuid]))
            self.assertTrue(uuid != "")
        print("tracks: " + str(len(self.couch.read("tracks"))))
        self.assertTrue(len(self.couch.read("tracks")) >= 20)
        print("files: " + str(len(self.couch.read("files"))))
        self.assertTrue(len(self.couch.read("files")) >= 20)
        data = self.couch.read("artists")
        for uuid in data:
            print(str(uuid)+": "+str(data[uuid]))
            self.assertTrue(uuid != "")
        print("artists: " + str(len(self.couch.read("artists"))))
        self.assertTrue(len(self.couch.read("artists")) >= 1)

        print("--- NEW")
        self.clean_db()
        self.assertTrue(len(self.couch.read("albums")) == 0)
        data = self.api_calls.load("new")
        self.assertTrue(self.api_calls.music_load.reload_new)
        time.sleep(0.5)
        data = self.api_calls.status()
        self.assertTrue(data["STATUS"]["load_data"]["reload_new"])
        while self.api_calls.music_load.reload_new:
            print(".")
            time.sleep(1)
        print("albums: " + str(len(self.couch.read("albums"))))
        self.assertTrue(len(self.couch.read("albums")) >= 3)
        print("tracks: " + str(len(self.couch.read("tracks"))))
        self.assertTrue(len(self.couch.read("tracks")) >= 20)
        print("files: " + str(len(self.couch.read("files"))))
        self.assertTrue(len(self.couch.read("files")) >= 20)

        print("--- IMAGES")
        # add a cover image to a folder and check result
        data = self.api_calls.load("images")
        self.assertTrue(self.api_calls.music_load.reload_img)
        while self.api_calls.music_load.reload_img:
            print(".")
            time.sleep(1)

        self.end_threads()
        self.fail()

    def test_check_version(self):
        self.start_threads()
        data = self.api_calls.check_version(mbox.app_version)
        self.assertEqual(data["STATUS"]["check-version"]["Code"], "800")
        data = self.api_calls.check_version(mbox.app_support[len(mbox.app_support)-1])
        self.assertEqual(data["STATUS"]["check-version"]["Code"], "801")
        data = self.api_calls.check_version("v0.0.1")
        self.assertEqual(data["STATUS"]["check-version"]["Code"], "802")
        self.end_threads()

    def test_test_uuid(self):
        self.start_threads()
        data = {"a_test-uuid-1234": {"k": 1}, "a_test-uuid-5678": {"k": 1}, "a_test-uuid-9012": {"k": 1}}
        self.couch.write("album_info", data)
        key = self.api_calls.test_uuid("album_info", "test")
        self.assertEqual(data[key], {"k": 1})
        data = {"t_test-uuid-1234": {"l": 1}, "t_test-uuid-5678": {"l": 1}, "t_test-uuid-9012": {"l": 1}}
        self.couch.write("tracks", data)
        key = self.api_calls.test_uuid("tracks", "test")
        self.assertEqual(data[key], {"l": 1})
        key = self.api_calls.test_uuid("tracks", "124")
        self.assertEqual(key, "124")
        self.end_threads()

    def test_check_active_card(self):
        self.start_threads()
        data_input = {"LOAD": {"RFID": ""}, "DATA": {"SHORT": {}}}
        data = self.api_calls.check_active_card(data_input)
        self.assertEqual(data, data_input)
        data_write = {"123,456,789,012": {"o": 1}, "456,789,012,123": {"o": 1}}
        self.couch.write("cards", data_write)
        data_input = {"LOAD": {"RFID": "123,456,789,012"}}
        data = self.api_calls.check_active_card(data_input)
        self.assertEqual(data["LOAD"]["CARD"], "known")
        data_input = {
            "LOAD": {"RFID": "123,456,789,000"},
            "DATA": {"SHORT": {}}
        }
        data = self.api_calls.check_active_card(data_input)
        self.assertEqual(data["LOAD"]["CARD"], "unknown")
        data_write = podcast_test_data
        self.couch.write("radio", data_write)
        data_write = {"a_1234-abcd": {
            "album": "test-album",
            "artist": "test-artist"
        }}
        self.couch.write("album_info", data_write)
        data = self.api_calls.check_active_card(data_input)
        self.assertEqual(data["DATA"]["SHORT"]["radio"], {"r_1234-abcd": "test-radio"})
        self.assertEqual(data["DATA"]["SHORT"]["album_info"], {"a_1234-abcd": "test-album (test-artist)"})
        self.end_threads()

    def test_filter(self):
        data = {"REQUEST": {"test": 1}}
        data = server_cmd.ServerApi.filter(data, "test-filter")
        self.assertEqual(data["REQUEST"]["db_filter"], "test-filter")
        data = server_cmd.ServerApi.filter(data, "test-filter-2")
        self.assertEqual(data["REQUEST"]["db_filter"], "test-filter||test-filter-2")
        data = server_cmd.ServerApi.filter(data, "test-filter-3")
        self.assertEqual(data["REQUEST"]["db_filter"], "test-filter||test-filter-2||test-filter-3")
