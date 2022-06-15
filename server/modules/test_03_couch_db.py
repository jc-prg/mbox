import time
import os
import json
from unittest import TestCase
import modules.config_stage as stage
import modules.config_mbox as mbox
import modules.couch_db as couch_db
import modules.music_speak as music_speak
import modules.music_vlc as music_vlc
import modules.json_db as json_db

test_key = "test_key"
test_data = {
    "test": "this is a test data set",
    "array": [0, 1, 2, 3, 4],
    "dict": {"key1": "value1", "key2": "value2"}
}


def set_vars_couch():
    json_db.jsonPath = "../test_data/couchdb_backup/"
    json_db.jsonAppDir = os.getcwd()
    json_db.init()


class TestCouchDB(TestCase):

    def start_vlc(self):
        set_vars_couch()
        self.vlc = music_vlc.VlcThread("test")
        self.vlc.start()
        self.speak = music_speak.SpeakThread(self.vlc, "test")
        self.speak.start()

    def test_init(self):
        self.start_vlc()
        self.couch = couch_db.CouchDB(stage.data_db, self.speak, "test")
        self.assertEqual(self.couch.connected, True)

    def test_check_db(self):
        self.start_vlc()
        self.couch = couch_db.CouchDB(stage.data_db, self.speak, "test")
        self.assertEqual(self.couch.connected, True)

        for category in mbox.databases:
            for key in mbox.databases[category]:
                self.assertTrue(key in self.couch.database)
                del self.couch.database[key]
                self.assertTrue(key not in self.couch.database)
        self.couch.check_db()
        for category in mbox.databases:
            for key in mbox.databases[category]:
                print(key)
                self.assertTrue(key in self.couch.database)

    def test_create(self):
        self.start_vlc()
        self.couch = couch_db.CouchDB(stage.data_db, self.speak, "test")
        self.assertEqual(self.couch.connected, True)
        if test_key in self.couch.database:
            del self.couch.database[test_key]
        self.assertTrue(test_key not in self.couch.database)
        self.couch.create(test_key)
        self.assertTrue(test_key in self.couch.database)
        self.assertTrue("main" in self.couch.database[test_key])
        self.assertTrue("data" in self.couch.database[test_key]["main"])
        del self.couch.database[test_key]
        self.assertTrue(test_key not in self.couch.database)

    def test_read_and_write(self):
        self.start_vlc()
        self.couch = couch_db.CouchDB(stage.data_db, self.speak, "test")
        self.assertEqual(self.couch.connected, True)
        self.couch.create(test_key)
        test_data["time"] = time.time()
        self.couch.write(test_key, test_data)
        read_data = self.couch.read(test_key)
        self.assertEqual(read_data, test_data)
        self.assertEqual(self.couch.cache[test_key], test_data)
        self.assertEqual(read_data["array"], self.couch.database[test_key]["main"]["data"]["array"])
        del self.couch.database[test_key]
        self.assertTrue(test_key not in self.couch.database)

    def test_read_group(self):
        self.start_vlc()
        self.couch = couch_db.CouchDB(stage.data_db, self.speak, "test")
        self.assertEqual(self.couch.connected, True)
        for group in mbox.databases:
            data = self.couch.read_group(group)
            for key in data:
                self.assertTrue(key in mbox.databases[group])
                self.assertEqual(data[key], self.couch.read(key))

    def test_fill_cache(self):
        self.start_vlc()
        self.couch = couch_db.CouchDB(stage.data_db, self.speak, "test")
        self.assertEqual(self.couch.connected, True)
        self.couch.create(test_key)
        test_data["time"] = time.time()
        self.couch.write(test_key, test_data)
        self.couch.cache = {}
        self.assertEqual(self.couch.cache, {})
        self.couch.fill_cache()
        self.assertEqual(self.couch.cache[test_key], test_data)
        del self.couch.database[test_key]
        self.assertTrue(test_key not in self.couch.database)

    def test_read_cache(self):
        self.start_vlc()
        self.couch = couch_db.CouchDB(stage.data_db, self.speak, "test")
        self.assertEqual(self.couch.connected, True)
        self.couch.create(test_key)
        test_data["time"] = time.time()
        self.couch.write(test_key, test_data)
        self.assertEqual(self.couch.read_cache(test_key), test_data)
        self.couch.cache = {}
        self.assertEqual(self.couch.cache, {})
        self.assertEqual(self.couch.read_cache(test_key), test_data)
        self.assertEqual(self.couch.read_cache("does not exist"), "")

    def test_backup_and_restore_json(self):
        self.start_vlc()
        self.couch = couch_db.CouchDB(stage.data_db, self.speak, "test")
        self.assertEqual(self.couch.connected, True)

        self.assertEqual(self.couch.backup_to_json(), "ok")
        file_list = os.listdir(json_db.jsonSettingsPath)
        print(json_db.jsonSettingsPath)
        for file in file_list:
            db_key = file.split(".")[0]
            print(db_key)
            self.assertTrue(db_key in self.couch.database)
            data = self.couch.read(db_key)
            filename = os.path.join(json_db.jsonSettingsPath, db_key + ".json")
            self.assertTrue(os.path.isfile(filename))
            self.assertEqual(json_db.read(db_key), data)

        self.couch.create(test_key)
        test_data["time"] = time.time()
        self.couch.write(test_key, test_data)
        self.assertEqual(self.couch.backup_to_json([test_key]), "ok")

        filename = os.path.join(json_db.jsonSettingsPath, test_key + ".json")
        self.assertTrue(os.path.isfile(filename))
        self.assertEqual(json_db.read(test_key), test_data)
