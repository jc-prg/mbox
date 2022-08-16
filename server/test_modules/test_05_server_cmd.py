import time
import os
import logging
import shutil
from unittest import TestCase

import modules.config_mbox as mbox
import modules.config_stage as stage
import modules.server_init as server_init
import modules.server_cmd as server_cmd
import modules.run_cmd as run_cmd
import modules.json_db as json_db

working_dir = os.getcwd()
podcast_test_url = "https://raw.githubusercontent.com/jc-prg/mbox/dev/test_data/test_podcast/test_podcast.xml"
podcast_test_img = "https://raw.githubusercontent.com/jc-prg/mbox/master/app/favicon.png"
podcast_test_uuid = "r_1234-abcd"
podcast_test_data = {podcast_test_uuid: {
            "title": "test-radio",
            "stream_url": podcast_test_url,
            "stream_url2": "",
            "description": "test radio description"
        }}
music_test_cover = "../test_data/test_cover/cover.png"
backup_dir = "../test_data/couchdb_backup/"
stage.log_filename_data = "/tmp/load_metadata.log"


def set_vars_couch():
    json_db.jsonPath = "../test_data/couchdb_backup/"
    json_db.jsonAppDir = os.getcwd()
    json_db.init()


class TestServerApi(TestCase):
    
    def start_threads(self):
        set_vars_couch()

        # init all required threads
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

        # set test specific vars
        stage.data_backup = os.path.join(os.getcwd(), backup_dir)
        stage.data_dir = os.path.join(os.getcwd(), "../test_data")
        mbox.music_dir = os.path.join(working_dir, "../test_data/music")
        mbox.music_cover = os.path.join(working_dir, "../test_data/cover")
        mbox.music_cover_upload = os.path.join(working_dir, "../test_data/cover_upload")
        mbox.log_connection = "/tmp/check_log_connection"

    def end_threads(self):
        # close threads
        server_init.end_modules(raise_error=False)

        # reset vars
        mbox.music_dir = self.mbox_music_dir
        mbox.music_cover = self.mbox_music_cover
        mbox.music_cover_upload = self.mbox_music_cover_upload
        mbox.log_connection = self.mbox_log_connection

    def clean_db(self):
        # remove all db entries
        self.couch.write("album_info", {})
        self.couch.write("albums", {})
        self.couch.write("tracks", {})
        self.couch.write("files", {})
        self.couch.write("artists", {})
        self.couch.write("radio", {})
        self.couch.write("playlists", {})
        self.couch.write("cards", {})

    def load_data(self):
        # load metadate from test files
        print("Load Album Data")
        self.clean_db()
        self.api_calls.load("all")
        time.sleep(0.5)
        while self.api_calls.music_load.reload_all:
            print(".")
            time.sleep(1)
        print("-> albums: " + str(len(self.couch.read("albums"))))
        print("-> tracks: " + str(len(self.couch.read("tracks"))))
        print("-> files: " + str(len(self.couch.read("files"))))

        # create test podcast
        self.couch.write("radio", podcast_test_data)
        print("-> radio: " + str(len(self.couch.read("radio"))))

    def test_response_error(self):
        self.start_threads()
        data = {"REQUEST": {"status": "success", "c-name": "test"}}
        data = self.api_calls.response_error(data=data, error="1")
        self.assertEqual(data["REQUEST"]["status"], "error")
        self.assertEqual(data["REQUEST"]["error"], "1")
        data = self.api_calls.response_error(data=data, error="2")
        self.assertEqual(data["REQUEST"]["status"], "error")
        self.assertEqual(data["REQUEST"]["error"], "1, 2")
        self.end_threads()

    def test_response_start(self):
        self.start_threads()
        data = self.api_calls.response_start(call_name="call_name", cmd1="cmd1", cmd2="cmd2",
                                             param1="param1", param2="param2")
        self.assertTrue("API" in data)
        self.assertTrue("DATA" in data)
        self.assertTrue("REQUEST" in data)
        self.assertTrue("LOAD" in data)
        self.assertTrue("STATUS" in data)
        self.assertEqual(data["REQUEST"]["status"], "success")
        self.assertEqual(data["REQUEST"]["c-name"], "call_name")
        self.assertEqual(data["REQUEST"]["c-param"], "param1 param2")
        self.assertTrue(10000 < data["REQUEST"]["start-time"] < time.time())
        self.end_threads()

    def test_response_end(self):
        self.start_threads()
        self.load_data()

        data_init = self.api_calls.response_start(call_name="call_name", cmd1="cmd1", cmd2="cmd2",
                                                  param1="param1", param2="param2")
        data_init = self.api_calls.response_error(data_init, "test error")
        data_test = self.api_calls.response_end(data_init)

        self.assertTrue("playback" in data_test["STATUS"])
        self.assertTrue("volume" in data_test["STATUS"]["playback"])
        self.assertTrue(0 <= data_test["STATUS"]["playback"]["volume"] <= 1)

        self.assertTrue("system" in data_test["STATUS"])
        self.assertTrue(data_test["STATUS"]["system"]["server_start"] == mbox.start_time)
        self.assertTrue(data_test["STATUS"]["system"]["server_running"] > 0)
        runtime = data_test["STATUS"]["system"]["server_running"]
        data_test = self.api_calls.response_end(data_init)
        self.assertTrue(data_test["STATUS"]["system"]["server_running"] > runtime)

        self.assertTrue("load_data" in data_test["STATUS"])
        self.assertTrue("reload_all" in data_test["STATUS"]["load_data"])
        self.assertTrue("reload_new" in data_test["STATUS"]["load_data"])
        self.assertTrue("reload_progress" in data_test["STATUS"]["load_data"])

        self.assertTrue("statistic" in data_test["STATUS"])
        self.assertTrue(data_test["STATUS"]["statistic"]["radio"] == 1)
        self.assertTrue(data_test["STATUS"]["statistic"]["album_info"] > 1)
        self.assertTrue(data_test["STATUS"]["statistic"]["tracks"] > 1)
        self.assertTrue(data_test["STATUS"]["statistic"]["files"] > 1)

        data_test = self.api_calls.response_end(data_init, ["no-system"])
        self.assertTrue("system" not in data_test["STATUS"])
        data_test = self.api_calls.response_end(data_init, ["no-playback"])
        self.assertTrue("playback" not in data_test["STATUS"])
        data_test = self.api_calls.response_end(data_init, ["no-request"])
        self.assertTrue("REQUEST" not in data_test)
        data_test = self.api_calls.response_end(data_init, ["no-load"])
        self.assertTrue("LOAD" not in data_test)
        data_test = self.api_calls.response_end(data_init, ["no-api"])
        self.assertTrue("API" not in data_test)
        data_test = self.api_calls.response_end(data_init, ["no-api", "no-request", "no-load"])
        self.assertTrue("REQUEST" not in data_test)
        self.assertTrue("LOAD" not in data_test)
        self.assertTrue("API" not in data_test)

        self.end_threads()

    def test_status(self):
        self.start_threads()

        # get status data
        data = self.api_calls.status()
        self.assertEqual(data["REQUEST"]["status"], "success")

        # check if main parameter are returned
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
        # normalize volume
        volume = self.player.volume
        if volume < 1:
            volume = volume * 100
        print(str(volume))

        # check if volume set correctly
        data = self.api_calls.volume("up")
        self.assertEqual(data["REQUEST"]["status"], "success")
        self.assertEqual(data["STATUS"]["playback"]["volume"], (volume + 5)/100)

        data = self.api_calls.volume("down")
        self.assertEqual(data["REQUEST"]["status"], "success")
        self.assertEqual(data["STATUS"]["playback"]["volume"], volume/100)

        data = self.api_calls.volume("set:50")
        self.assertEqual(data["REQUEST"]["status"], "success")
        self.assertEqual(data["STATUS"]["playback"]["volume"], 0.5)

        data = self.api_calls.volume("set:60")
        self.assertEqual(data["REQUEST"]["status"], "success")
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

        # check if first track of album is played
        print("Test album: "+str(test_key))
        data = self.api_calls.play(uuid=test_uuid)
        self.assertEqual(data["REQUEST"]["status"], "success")

        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playing"], 1)
        self.assertEqual(data["STATUS"]["playback"]["playlist_pos"], 1)
        self.assertEqual(data["STATUS"]["playback"]["song"]["album_uuid"], test_uuid)
        time.sleep(2)

        # check if single track is played
        print("Test track: "+str(test_uuid_track))
        data = self.api_calls.play(uuid=test_uuid_track)
        self.assertEqual(data["REQUEST"]["status"], "success")

        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playing"], 1)
        self.assertEqual(data["STATUS"]["playback"]["song"]["uuid"], test_uuid_track)
        time.sleep(2)

        self.end_threads()

    def test_play_position(self):
        self.start_threads()
        self.load_data()

        # select album to be played
        data = self.couch.read("album_info")
        test_key = ""
        for key in data:
            if "Unknown" not in data[key]["artist"] and "error" not in key:
                test_key = key
        test_uuid = test_key

        # start to play
        data = self.api_calls.play(uuid=test_uuid)
        self.assertEqual(data["REQUEST"]["status"], "success")

        time.sleep(2)
        data = self.api_calls.status()
        print(data["STATUS"]["playback"])
        pl_length = data["STATUS"]["playback"]["playlist_len"]
        pl_position = data["STATUS"]["playback"]["playlist_pos"]
        self.assertEqual(data["STATUS"]["playback"]["playlist_pos"], 1)
        self.assertEqual(len(data["STATUS"]["playback"]["playlist"]), pl_length)

        # check if different positions on the album are played correctly
        data = self.api_calls.play_position(test_uuid, 2)
        self.assertEqual(data["REQUEST"]["status"], "success")

        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playlist_pos"], 3)

        self.api_calls.play_position(test_uuid, 0)
        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playlist_pos"], 1)

        self.api_calls.play_position(test_uuid, 3)
        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playlist_pos"], 4)

        self.end_threads()

    def test_pause(self):
        self.start_threads()
        self.load_data()

        # select album to be played
        data = self.couch.read("album_info")
        test_key = ""
        for key in data:
            if "Unknown" not in data[key]["artist"] and "error" not in key:
                test_key = key
        test_uuid = test_key
        test_uuid_track = data[test_key]["tracks"][0]

        # start to play album
        print("Test album: "+str(test_key))
        data = self.api_calls.play(uuid=test_uuid)
        self.assertEqual(data["REQUEST"]["status"], "success")

        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playing"], 1)
        self.assertEqual(data["STATUS"]["playback"]["song"]["album_uuid"], test_uuid)

        # pause playback
        data = self.api_calls.pause()
        self.assertEqual(data["REQUEST"]["status"], "success")

        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playing"], 0)
        self.assertEqual(data["STATUS"]["playback"]["song"]["album_uuid"], test_uuid)

        # un-pause playback
        self.api_calls.pause()
        time.sleep(2)
        data = self.api_calls.pause()
        self.assertEqual(data["REQUEST"]["status"], "success")

        self.assertEqual(data["STATUS"]["playback"]["playing"], 1)
        self.assertEqual(data["STATUS"]["playback"]["song"]["album_uuid"], test_uuid)
        self.end_threads()

    def test_stop(self):
        self.start_threads()
        self.load_data()

        # select album to be played
        data = self.couch.read("album_info")
        test_key = ""
        for key in data:
            if "Unknown" not in data[key]["artist"] and "error" not in key:
                test_key = key
        test_uuid = test_key
        test_uuid_track = data[test_key]["tracks"][0]

        # start playback
        print("Test album: "+str(test_key))
        print(data[test_key])
        data = self.api_calls.play(uuid=test_uuid)
        self.assertEqual(data["REQUEST"]["status"], "success")

        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playing"], 1)
        self.assertEqual(data["STATUS"]["playback"]["song"]["album_uuid"], test_uuid)

        # stop playback
        data = self.api_calls.stop()
        self.assertEqual(data["REQUEST"]["status"], "success")

        time.sleep(2)
        data = self.api_calls.status()
        print(data["STATUS"]["playback"])
        self.assertEqual(data["STATUS"]["playback"]["playing"], 0)
        self.assertTrue(data["STATUS"]["playback"]["status"] == "State.Ended" or
                        data["STATUS"]["playback"]["status"] == "")
        self.assertEqual(data["STATUS"]["playback"]["song"], {})

        self.end_threads()

    def test_next_and_last(self):
        self.start_threads()
        self.load_data()

        # select album to be played
        data = self.couch.read("album_info")
        test_key = ""
        for key in data:
            if "Unknown" not in data[key]["artist"] and "error" not in key:
                test_key = key
        test_uuid = test_key

        # start playback
        data = self.api_calls.play(uuid=test_uuid)
        self.assertEqual(data["REQUEST"]["status"], "success")

        time.sleep(2)
        data = self.api_calls.status()
        print(data["STATUS"]["playback"])
        pl_length = data["STATUS"]["playback"]["playlist_len"]
        pl_position = data["STATUS"]["playback"]["playlist_pos"]
        self.assertEqual(data["STATUS"]["playback"]["playlist_pos"], 1)
        self.assertEqual(len(data["STATUS"]["playback"]["playlist"]), pl_length)

        # check different jumps back and forward
        data = self.api_calls.next(step=1)
        self.assertEqual(data["REQUEST"]["status"], "success")

        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playlist_pos"], 2)

        data = self.api_calls.next(step=2)
        self.assertEqual(data["REQUEST"]["status"], "success")

        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playlist_pos"], 4)

        data = self.api_calls.next(step=-1)
        self.assertEqual(data["REQUEST"]["status"], "success")

        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playlist_pos"], 3)

        data = self.api_calls.last(step=1)
        self.assertEqual(data["REQUEST"]["status"], "success")

        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playlist_pos"], 2)

        data = self.api_calls.next(step=-4)
        self.assertEqual(data["REQUEST"]["status"], "success")

        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playlist_pos"], 2)

        data = self.api_calls.next(step=15)
        self.assertEqual(data["REQUEST"]["status"], "success")

        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playlist_pos"], 2)

        self.end_threads()

    def test_jump(self):
        self.start_threads()
        self.load_data()

        # select album to be played
        data = self.couch.read("album_info")
        data_tracks = self.couch.read("tracks")
        test_key = ""
        for key in data:
            if "Unknown" not in data[key]["artist"] and "error" not in key:
                test_key = key
        test_uuid = test_key
        test_uuid_track = data[test_key]["tracks"][1]
        test_length = data_tracks[test_uuid_track]["length"]
        print(data_tracks[test_uuid_track])
        print(test_length)

        # start playback
        print("Test track: "+str(test_key))
        data = self.api_calls.play(uuid=test_uuid_track)
        self.assertEqual(data["REQUEST"]["status"], "success")

        time.sleep(1)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playing"], 1)
        self.assertEqual(data["STATUS"]["playback"]["song"]["uuid"], test_uuid_track)
        self.assertTrue(data["STATUS"]["playback"]["position"] < 2)
        print(data["STATUS"]["playback"])

        # jump to the middle
        data = self.api_calls.jump(percentage=50)
        self.assertEqual(data["REQUEST"]["status"], "success")

        time.sleep(1)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playing"], 1)
        self.assertEqual(data["STATUS"]["playback"]["song"]["uuid"], test_uuid_track)
        self.assertTrue(test_length/2 < data["STATUS"]["playback"]["position"] < test_length/2+2)
        print(data["STATUS"]["playback"])

        # jump back nearly to the beginning
        data = self.api_calls.jump(percentage=10)
        self.assertEqual(data["REQUEST"]["status"], "success")

        time.sleep(1)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playing"], 1)
        self.assertEqual(data["STATUS"]["playback"]["song"]["uuid"], test_uuid_track)
        self.assertTrue(data["STATUS"]["playback"]["position"] < test_length*0.3)
        print(data["STATUS"]["playback"])

        self.end_threads()

    def test_read_db(self):
        self.start_threads()
        self.load_data()

        # check if all returns all relevant databases completely
        data = self.api_calls.read_db("all")
        self.assertEqual(data["REQUEST"]["status"], "success")
        db_list = ["files", "tracks", "albums", "album_info", "cards", "playlists", "radio", "artists"]
        count = 0
        for db in db_list:
            if db in data["DATA"]:
                count += 1
        self.assertEqual(len(db_list), count)
        for db in db_list:
            self.assertEqual(self.couch.read(db), data["DATA"][db])

        # check if artists returns relevant 3 db
        data = self.api_calls.read_db("artists")
        self.assertEqual(data["REQUEST"]["status"], "success")
        db_list = ["albums", "album_info", "artists"]
        count = 0
        for db in db_list:
            print(db)
            print(db in data["DATA"])
            if db in data["DATA"]:
                count += 1
        self.assertEqual(len(db_list), count)
        for db in db_list:
            self.assertEqual(self.couch.read(db), data["DATA"][db])

        # check if combined request returns selected db
        data = self.api_calls.read_db("radio--cards")
        self.assertEqual(data["REQUEST"]["status"], "success")
        db_list = ["radio", "cards"]
        count = 0
        for db in db_list:
            if db in data["DATA"]:
                count += 1
        self.assertEqual(len(db_list), count)
        for db in db_list:
            self.assertEqual(self.couch.read(db), data["DATA"][db])

        # check if single requests return expected db
        db_list = ["files", "tracks", "albums", "album_info", "cards", "playlists", "radio"]
        for db in db_list:
            data = self.api_calls.read_db(db)
            self.assertEqual(data["REQUEST"]["status"], "success")
            self.assertEqual(self.couch.read(db), data["DATA"][db])

        # check if unknown db name returns an error
        data = self.api_calls.read_db("radio--card")
        self.assertEqual(data["REQUEST"]["status"], "error")
        data = self.api_calls.read_db("not-defined")
        self.assertEqual(data["REQUEST"]["status"], "error")

        self.end_threads()

    def test_read_entry(self):
        self.start_threads()
        self.load_data()

        db_list = ["radio", "album_info", "tracks", "playlists", "cards"]
        for db in db_list:
            data = self.couch.read(db)
            for key in data:
                result = self.api_calls.read_entry(uuid=key)
                print(key)
                self.assertEqual(result["DATA"]["_selected_uuid"], key)
                self.assertEqual(result["DATA"]["_selected_db"], db)
                for entry_key in data[key]:
                    self.assertEqual(data[key][entry_key], result["DATA"]["_selected"][entry_key])

        result = self.api_calls.read_entry("a_does-not-exist")

        print(result["REQUEST"])
        self.assertEqual(result["DATA"], {})
        self.assertEqual(result["REQUEST"]["status"], "error")
        self.assertTrue(result["REQUEST"]["error"] != "")

        result = self.api_calls.read_entry("k_does-not-exist")
        print(result["REQUEST"])
        self.assertEqual(result["DATA"], {})
        self.assertEqual(result["REQUEST"]["status"], "error")
        self.assertTrue(result["REQUEST"]["error"] != "")

        self.end_threads()

    def test_add(self):
        self.start_threads()

        # add podcast
        data = self.api_calls.add(database="radio",
                                  param="Test Podcast||Test Podcast Description||https://github.com/jc-prg/mbox||" +
                                  podcast_test_url + "||" + podcast_test_img)
        self.assertEqual(data["REQUEST"]["status"], "success")

        test_key = "XXX"
        data = self.couch.read("radio")
        for key in data:
            if data[key]["title"] == "Test Podcast":
                test_key = key
        self.assertTrue(test_key in data)
        self.assertEqual(data[test_key]["description"], "Test Podcast Description")
        self.assertEqual(data[test_key]["stream_info"], "https://github.com/jc-prg/mbox")
        self.assertEqual(data[test_key]["stream_url"], podcast_test_url)
        self.assertEqual(data[test_key]["cover_images"]["url"][0], podcast_test_img)
        self.assertEqual(data[test_key]["cover_images"]["active"], "url")

        # add playlist
        data = self.api_calls.add(database="playlists",
                                  param="Test Playlist||Test Playlist Description")
        self.assertEqual(data["REQUEST"]["status"], "success")

        test_key = "XXX"
        data = self.couch.read("playlists")
        for key in data:
            if data[key]["title"] == "Test Playlist":
                test_key = key
        self.assertTrue(test_key in data)
        self.assertEqual(data[test_key]["description"], "Test Playlist Description")
        self.assertEqual(data[test_key]["cover_images"]["url"], [])
        self.assertEqual(data[test_key]["cover_images"]["active"], "none")
        self.end_threads()

    def test_edit(self):
        self.start_threads()
        self.load_data()

        # prepare podcast
        data = self.api_calls.add(database="radio",
                           param="Test Podcast||Test Podcast Description||https://github.com/jc-prg/mbox||" +
                                 podcast_test_url + "||" + podcast_test_img)
        entry_uuid = data["LOAD"]["UUID"]
        entry_data = self.couch.read("radio", entry_uuid)
        entry_data["title"] += "... changed"
        entry_data["new_value"] = "test"  # should not be added to the entry

        # edit podcast
        data = self.api_calls.edit(uuid=entry_uuid, entry_data=entry_data)
        self.assertEqual(data["REQUEST"]["status"], "success")

        del entry_data["new_value"]
        entry_data_compare = self.couch.read("radio")[entry_uuid]
        self.assertTrue(entry_data == entry_data_compare)

        # prepare playlist
        data = self.api_calls.add(database="playlists",
                           param="Test Playlist||Test Playlist Description")
        entry_uuid = data["LOAD"]["UUID"]
        entry_data = self.couch.read("playlists", entry_uuid)
        entry_data["title"] += "... changed"
        entry_data["new_value"] = "test"  # should not be added to the entry

        # edit playlist
        data = self.api_calls.edit(uuid=entry_uuid, entry_data=entry_data)
        self.assertEqual(data["REQUEST"]["status"], "success")
        del entry_data["new_value"]
        entry_data_compare = self.couch.read("playlists")[entry_uuid]
        self.assertTrue(entry_data == entry_data_compare)

        # identify track
        data = self.couch.read("tracks")
        count = 0
        entry_uuid = ""
        for key in data:
            count += 1
            if count == 5:
                entry_uuid = key
        entry_data = data[entry_uuid]
        entry_data["title"] += "... changed"
        entry_data["new_value"] = "test"  # should not be added to the entry

        # edit track
        data = self.api_calls.edit(uuid=entry_uuid, entry_data=entry_data)
        self.assertEqual(data["REQUEST"]["status"], "success")

        del entry_data["new_value"]
        entry_data_compare = self.couch.read("tracks")[entry_uuid]
        self.assertTrue(entry_data == entry_data_compare)

        # identify album
        data = self.couch.read("album_info")
        count = 0
        entry_uuid = ""
        for key in data:
            count += 1
            if count == 3:
                entry_uuid = key
        entry_data = data[entry_uuid]
        entry_data["artist"] += "... changed"
        entry_data["album"] += "... changed"
        entry_data["new_value"] = "test"  # should not be added to the entry

        # edit album
        data = self.api_calls.edit(uuid=entry_uuid, entry_data=entry_data)
        self.assertEqual(data["REQUEST"]["status"], "success")

        del entry_data["new_value"]
        entry_data_compare = self.couch.read("album_info")[entry_uuid]
        self.assertTrue(entry_data == entry_data_compare)

        self.end_threads()

    def test_delete(self):
        self.start_threads()
        self.load_data()

        #prepare data radio
        print("Check deletion of radio")
        self.api_calls.add(database="radio",
                           param="Test Podcast Delete||Test Podcast Description||https://github.com/jc-prg/mbox||" +
                                 podcast_test_url + "||" + podcast_test_img)
        self.api_calls.add(database="radio",
                           param="Test Podcast Delete 2||Test Podcast Description||https://github.com/jc-prg/mbox||" +
                                 podcast_test_url + "||" + podcast_test_img)
        test_key = "XXX"
        data = self.couch.read("radio")
        data_length = len(data)
        for key in data:
            if data[key]["title"] == "Test Podcast Delete":
                test_key = key
        self.assertTrue(test_key in data)
        self.assertEqual(data[test_key]["description"], "Test Podcast Description")
        self.assertEqual(data[test_key]["stream_url"], podcast_test_url)

        # delete radio
        print(test_key)
        self.api_calls.delete(test_key)
        data = self.couch.read("radio")
        self.assertTrue(test_key not in data)
        self.assertTrue(len(data) == data_length - 1)

        # prepare data album_info
        print("Check deletion of album_info")
        data = self.couch.read("album_info")
        data_tracks = self.couch.read("tracks")
        album_uuid = ""
        for key in data:
            if "error" not in key and key != "":
                album_uuid = key
                continue
        print(album_uuid)
        print(data[album_uuid])
        album_tracks = data[album_uuid]["tracks"]
        album_files = []
        album_artist = data[album_uuid]["artist"]
        album_name = data[album_uuid]["album"]
        for key in album_tracks:
            album_files.append(data_tracks[key]["file"])

        print(album_uuid)
        print(album_tracks)
        print(album_files)

        data_test = self.couch.read("albums")
        print(data_test)
        self.assertTrue(album_artist in data_test)
        self.assertTrue(album_name in data_test[album_artist])
        data_test = self.couch.read("artists")
        self.assertTrue(album_artist in data_test)
        data_test = self.couch.read("tracks")
        for key in album_tracks:
            self.assertTrue(key in data_test)
        data_test = self.couch.read("files")
        for key in album_files:
            self.assertTrue(key in data_test)

        # delete album info incl. artists, album, tracks and files
        print("Check deletion of related artist, album, tracks, files")
        self.api_calls.delete(album_uuid)
        data_test = self.couch.read("album_info")
        self.assertTrue(album_uuid not in data_test)
        data_test = self.couch.read("albums")
        print(data_test)
        if album_artist in data_test:
            self.assertTrue(album_name not in data_test[album_artist])
        data_test = self.couch.read("tracks")
        for key in album_tracks:
            self.assertTrue(key not in data_test)
        data_test = self.couch.read("files")
        for key in album_files:
            self.assertTrue(key not in data_test)

        self.end_threads()

    def test_images(self):
        self.start_threads()

        # prepare data
        data = self.api_calls.add(database="playlists",
                                  param="Test Playlist||Test Playlist Description")
        test_key = data["LOAD"]["UUID"]
        data = self.couch.read("playlists")
        self.assertTrue(test_key in data)
        print(data[test_key])
        self.assertEqual(data[test_key]["description"], "Test Playlist Description")
        self.assertEqual(data[test_key]["cover_images"]["url"], [])
        self.assertEqual(data[test_key]["cover_images"]["active"], "none")

        # add filename for uploaded image
        self.api_calls.images(cmd="upload", uuid=test_key, param="test.jpg")
        data = self.couch.read("playlists")
        self.assertTrue("test.jpg" in data[test_key]["cover_images"]["upload"])
        self.assertEqual(data[test_key]["cover_images"]["active"], "upload")

        # change active image
        self.api_calls.images(cmd="set_active", uuid=test_key, param="dir")
        data = self.couch.read("playlists")
        self.assertTrue("test.jpg" in data[test_key]["cover_images"]["upload"])
        self.assertEqual(data[test_key]["cover_images"]["active"], "dir")

        # check for errors
        data = self.api_calls.images(cmd="not-defined", uuid=test_key, param="dir")
        self.assertEqual(data["REQUEST"]["status"], "error")
        self.api_calls.images(cmd="set_active", uuid=test_key, param="not-defined")
        self.assertEqual(data["REQUEST"]["status"], "error")
        self.api_calls.images(cmd="set_active", uuid="p_not-defined", param="dir")
        self.assertEqual(data["REQUEST"]["status"], "error")

        self.end_threads()

    def test_playlist_items(self):
        self.start_threads()
        self.load_data()

        # prepare data
        test_key_album = ""
        test_key_track = ""
        count = 0
        data = self.couch.read("album_info")
        for key in data:
            if count == 2:
                test_key_album = key
            count += 1
        count = 0
        data = self.couch.read("tracks")
        for key in data:
            if count == 2:
                test_key_track = key
            count += 1

        data = self.api_calls.add(database="playlists",
                                  param="Test Playlist||Test Playlist Description")
        test_key = data["LOAD"]["UUID"]
        print(test_key)
        data = self.couch.read("playlists")
        self.assertTrue(test_key in data)
        print(data[test_key])
        self.assertEqual(data[test_key]["description"], "Test Playlist Description")
        self.assertEqual(data[test_key]["tracks"], [])
        self.assertEqual(data[test_key]["tracks_ref"], [])
        self.assertEqual(data[test_key]["cover_images"]["url"], [])
        self.assertEqual(data[test_key]["cover_images"]["active"], "none")

        # add playlist items
        self.api_calls.playlist_items(cmd="add", uuid=test_key, param=test_key_album)
        self.api_calls.playlist_items(cmd="add", uuid=test_key, param=test_key_track)
        data = self.couch.read("playlists")
        self.assertTrue(test_key_album in data[test_key]["tracks"])
        self.assertTrue(test_key_track in data[test_key]["tracks"])

        # delete playlist items
        self.api_calls.playlist_items(cmd="delete", uuid=test_key, param=test_key_album)
        self.api_calls.playlist_items(cmd="delete", uuid=test_key, param=test_key_track)
        data = self.couch.read("playlists")
        self.assertTrue(test_key_album not in data[test_key]["tracks"])
        self.assertTrue(test_key_track not in data[test_key]["tracks"])

        # check for errors
        data = self.api_calls.playlist_items(cmd="cmd-not-defined", uuid=test_key, param=test_key_album)
        self.assertEqual(data["REQUEST"]["status"], "error")
        data = self.api_calls.playlist_items(cmd="add", uuid="p_not-defined", param=test_key_album)
        self.assertEqual(data["REQUEST"]["status"], "error")
        data = self.api_calls.playlist_items(cmd="add", uuid=test_key, param="t_not-defined")
        self.assertEqual(data["REQUEST"]["status"], "error")

        self.end_threads()

    def test_cards(self):
        self.start_threads()
        self.load_data()

        # prepare data
        data = self.api_calls.add(database="radio",
                                  param="Test Podcast||Test Podcast Description||https://github.com/jc-prg/mbox||" +
                                  podcast_test_url + "||" + podcast_test_img)
        test_uuid_radio = data["LOAD"]["UUID"]
        data = self.api_calls.add(database="playlists",
                                  param="Test Podcast Card||Test Podcast Description||https://github.com/jc-prg/mbox||" +
                                  podcast_test_url + "||" + podcast_test_img)
        test_uuid_playlist = data["LOAD"]["UUID"]
        data = self.couch.read("album_info")
        count = 0
        test_uuid_album = ""
        for key in data:
            count += 1
            if count == 2:
                test_uuid_album = key

        # check add card-id to album_info
        data = self.api_calls.cards(uuid=test_uuid_album, param="1,2,3,4")
        self.assertEqual(data["REQUEST"]["status"], "success")
        data = self.couch.read("album_info")
        self.assertEqual(data[test_uuid_album]["card_id"], "1,2,3,4")
        data = self.couch.read("cards")
        self.assertEqual(data["1,2,3,4"][0], test_uuid_album)

        # check add card-id to playlist
        data = self.api_calls.cards(uuid=test_uuid_playlist, param="2,3,4,5")
        self.assertEqual(data["REQUEST"]["status"], "success")
        data = self.couch.read("playlists")
        self.assertEqual(data[test_uuid_playlist]["card_id"], "2,3,4,5")
        data = self.couch.read("cards")
        self.assertEqual(data["2,3,4,5"][0], test_uuid_playlist)

        # check add card-id to radio
        data = self.api_calls.cards(uuid=test_uuid_radio, param="3,4,5,6")
        self.assertEqual(data["REQUEST"]["status"], "success")
        data = self.couch.read("radio")
        self.assertEqual(data[test_uuid_radio]["card_id"], "3,4,5,6")
        data = self.couch.read("cards")
        self.assertEqual(data["3,4,5,6"][0], test_uuid_radio)

        # check errors (uuid doesn't exist)
        data = self.api_calls.cards(uuid="a_uuid", param="0,0,0,0")
        self.assertEqual(data["REQUEST"]["status"], "error")
        data = self.couch.read("cards")
        self.assertTrue("0,0,0,0" not in data)

        self.end_threads()

    def test_card_info(self):
        self.start_threads()
        self.load_data()

        # add card information to db (see test_cards)
        # prepare data
        data = self.api_calls.add(database="radio",
                                  param="Test Podcast||Test Podcast Description||https://github.com/jc-prg/mbox||" +
                                  podcast_test_url + "||" + podcast_test_img)
        test_uuid_radio = data["LOAD"]["UUID"]
        data = self.api_calls.add(database="playlists",
                                  param="Test Podcast Card||Test Podcast Description||https://github.com/jc-prg/mbox||" +
                                  podcast_test_url + "||" + podcast_test_img)
        test_uuid_playlist = data["LOAD"]["UUID"]
        data = self.couch.read("album_info")
        count = 0
        test_uuid_album = ""
        for key in data:
            count += 1
            if count == 2:
                test_uuid_album = key

        data = self.api_calls.cards(uuid=test_uuid_album, param="1,2,3,4")
        self.assertEqual(data["REQUEST"]["status"], "success")
        data = self.api_calls.cards(uuid=test_uuid_playlist, param="2,3,4,5")
        self.assertEqual(data["REQUEST"]["status"], "success")
        data = self.api_calls.cards(uuid=test_uuid_radio, param="3,4,5,6")
        self.assertEqual(data["REQUEST"]["status"], "success")

        for key_card in ["1,2,3,4", "2,3,4,5", "3,4,5,6"]:
            # check if card db return correctly
            data = self.api_calls.card_info(filter=key_card)
            self.assertEqual(data["REQUEST"]["status"], "success")
            data_cards = self.couch.read("cards")
            self.assertEqual(data_cards[key_card], data["DATA"]["cards"][key_card])

            # check if detailed entry exists
            key_uuid = data_cards[key_card][0]
            if key_uuid.startswith("a_"):
                entry_type = "album_info"
            elif key_uuid.startswith("r_"):
                entry_type = "radio"
            elif key_uuid.startswith("p_"):
                entry_type = "playlists"
            else:
                self.fail()
            self.assertEqual(data["DATA"][entry_type][key_uuid]["card_id"], key_card)

        self.end_threads()

    def test_card_set(self):
        self.start_threads()
        self.api_calls.card_set("123,456,789,012")
        self.assertEqual(mbox.rfid_ctrl["cardUID"], "123,456,789,012")
        data = self.api_calls.status()
        self.assertEqual(data["LOAD"]["RFID"], "123,456,789,012")
        self.api_calls.card_set("123,456,789,abc")
        self.assertEqual(mbox.rfid_ctrl["cardUID"], "123,456,789,abc")
        self.api_calls.card_set("no_card")
        self.assertEqual(mbox.rfid_ctrl["cardUID"], "")
        self.end_threads()

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
        self.start_threads()
        self.load_data()

        data = self.api_calls.set_button(buttonID="no_button")
        self.assertEqual(data["REQUEST"]["status"], "success")
        self.assertEqual(mbox.rfid_ctrl["buttonID"], "")
        data = self.api_calls.set_button(buttonID="next")
        self.assertEqual(data["REQUEST"]["status"], "success")
        self.assertEqual(mbox.rfid_ctrl["buttonID"], "next")
        data = self.api_calls.set_button(buttonID="last")
        self.assertEqual(data["REQUEST"]["status"], "success")
        self.assertEqual(mbox.rfid_ctrl["buttonID"], "last")
        data = self.api_calls.set_button(buttonID="mute")
        self.assertEqual(data["REQUEST"]["status"], "success")
        self.assertEqual(mbox.rfid_ctrl["buttonID"], "mute")
        data = self.api_calls.set_button(buttonID="pause")
        self.assertEqual(data["REQUEST"]["status"], "success")
        self.assertEqual(mbox.rfid_ctrl["buttonID"], "pause")

        data = self.couch.read("album_info")
        test_key = ""
        for key in data:
            if "Unknown" not in data[key]["artist"] and "error" not in key:
                test_key = key
        test_uuid = test_key
        self.api_calls.play(uuid=test_uuid)
        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playing"], 1)
        self.assertEqual(data["STATUS"]["playback"]["song"]["album_uuid"], test_uuid)

        self.api_calls.set_button(buttonID="pause")
        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playing"], 0)

        self.api_calls.set_button(buttonID="pause")
        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playing"], 1)

        self.api_calls.set_button(buttonID="next")
        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playlist_pos"], 2)

        self.api_calls.set_button(buttonID="back")
        time.sleep(2)
        data = self.api_calls.status()
        self.assertEqual(data["STATUS"]["playback"]["playlist_pos"], 1)

        self.end_threads()

    def test_button_error(self):
        self.start_threads()
        result = self.api_calls.button_error("back", 5)
        self.assertEqual(result["REQUEST"]["status"], "error")
        self.assertTrue("is pressed for" in result["REQUEST"]["error"] and "back" in result["REQUEST"]["error"])
        self.end_threads()

    def test_backup(self):
        self.start_threads()
        self.load_data()
        # prepare data
        check_backup = ["album_info", "albums", "radio", "cards", "files", "tracks", "playlists", "status"]
        directory = os.path.join(os.getcwd(), backup_dir)
        for root, directories, files in os.walk(directory):
            for file in files:
                os.remove(os.path.join(directory, file))

        # check backup
        data = self.api_calls.backup("db2json")
        self.assertEqual(data["REQUEST"]["status"], "success")
        for file in check_backup:
            path = os.path.join(directory, file+".json")
            self.assertTrue(os.path.isfile(path))
            if file != "status":
                self.assertEqual(json_db.read(file), self.couch.read(file))

        for db in check_backup:
            self.couch.write(db, {})

        # check restore
        data = self.api_calls.backup("json2db")
        self.assertEqual(data["REQUEST"]["status"], "success")
        for file in check_backup:
            data = self.couch.read(file)
            print(file+" ... "+str(len(data)))
            self.assertEqual(json_db.read(file), data)

        self.end_threads()

    def test_load(self):
        self.start_threads()

        # cleanup database and additional image file
        self.clean_db()
        self.assertEqual(self.couch.read("album_info"), {})
        self.assertEqual(self.couch.read("albums"), {})
        self.assertEqual(self.couch.read("tracks"), {})
        self.assertEqual(self.couch.read("files"), {})
        self.assertEqual(self.couch.read("artists"), {})
        self.assertEqual(self.couch.read("radio"), {})
        self.assertEqual(self.couch.read("cards"), {})
        self.assertEqual(self.couch.read("playlists"), {})
        destination = os.path.join(os.getcwd(), "../test_data/music/01_Music/Goethe, Der Zauberlehrling/cover.png")
        if os.path.isfile(destination):
            os.remove(destination)

        # reload all data
        print("--- ALL")
        data = self.api_calls.load("all")
        self.assertEqual(data["REQUEST"]["status"], "success")
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

        data_albums = self.couch.read("album_info")
        for album_uuid in data_albums:
            if "Goethe, Der Erlkoenig" in data_albums[album_uuid]["albumpath"]:
                print(data_albums[album_uuid]["album"])
                print(data_albums[album_uuid]["cover_images"])
                self.assertTrue(data_albums[album_uuid]["cover_images"]["dir"] != [] or
                                data_albums[album_uuid]["cover_images"]["track"] != [])

        # check for new data only (at the moment complete reload also)
        print("--- NEW")
        self.clean_db()
        self.assertTrue(len(self.couch.read("albums")) == 0)
        data = self.api_calls.load("new")
        self.assertEqual(data["REQUEST"]["status"], "success")
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

        # add a cover image to a folder and check result
        print("--- IMAGES")
        source = os.path.join(os.getcwd(), music_test_cover)
        destination = os.path.join(os.getcwd(), "../test_data/music/01_Music/Goethe, Der Zauberlehrling/cover.png")
        shutil.copy(source, destination)

        data_albums = self.couch.read("album_info")
        for album_uuid in data_albums:
            if "Goethe, Der Zauberlehrling" in data_albums[album_uuid]["albumpath"]:
                print(data_albums[album_uuid]["album"])
                print(data_albums[album_uuid]["cover_images"])
                self.assertEqual(data_albums[album_uuid]["cover_images"]["dir"], [])

        self.api_calls.load("images")
        self.assertTrue(self.api_calls.music_load.reload_img)
        while self.api_calls.music_load.reload_img:
            print(".")
            time.sleep(1)

        data_albums = self.couch.read("album_info")
        for album_uuid in data_albums:
            if "Goethe, Der Zauberlehrling" in data_albums[album_uuid]["albumpath"]:
                print(data_albums[album_uuid]["album"])
                print(data_albums[album_uuid]["cover_images"])
                self.assertEqual(data_albums[album_uuid]["cover_images"]["active"], "dir")
                self.assertEqual(data_albums[album_uuid]["cover_images"]["dir"][0], "/01_Music/Goethe, Der Zauberlehrling/cover.png")

        self.end_threads()

    def test_check_version(self):
        self.start_threads()
        data = self.api_calls.check_version(mbox.app_version)
        self.assertEqual(data["REQUEST"]["status"], "success")
        self.assertEqual(data["STATUS"]["check-version"]["Code"], "800")
        data = self.api_calls.check_version(mbox.app_support[len(mbox.app_support)-1])
        self.assertEqual(data["REQUEST"]["status"], "success")
        self.assertEqual(data["STATUS"]["check-version"]["Code"], "801")
        data = self.api_calls.check_version("v0.0.1")
        self.assertEqual(data["REQUEST"]["status"], "success")
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
