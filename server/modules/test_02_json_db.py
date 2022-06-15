from unittest import TestCase
import modules.config_stage as stage
import modules.json_db as json_db
import os
import time

json_db.jsonPath = "../test_data/"
json_db.jsonAppDir = os.getcwd()
test_db = "test_json/test"
test_db_error = "test_json/test_error"
test_db_write = "test_json/test_write"


class TestJsonDB(TestCase):
    def test_init(self):
        json_db.init()
        print(json_db.jsonSettingsPath)
        self.assertEqual(os.path.isdir(json_db.jsonSettingsPath), True)

    def test_read(self):
        data = json_db.read(test_db)
        print(str(data))
        self.assertEqual(data["application"], "jc://mbox/")
        self.assertEqual(len(data["test-data"]["array"]), 6)
        data = json_db.read(test_db_error)
        print(str(data))
        self.assertTrue("error" in data)

    def test_write(self):
        data = json_db.read(test_db)
        print(str(data))
        self.assertEqual(data["application"], "jc://mbox/")
        self.assertEqual(len(data["test-data"]["array"]), 6)
        current_time = time.time()
        data["test-data"]["current-time"] = current_time
        self.assertEqual(json_db.write(test_db_write, data), "ok")
        data_write = json_db.read(test_db_write)
        self.assertEqual(data["test-data"]["current-time"], current_time)

