import modules.json_db as json_db
import modules.config_stage as stage
import modules.config_mbox as mbox
from modules.run_cmd import *

import sys
import logging
import time
import couchdb
import requests


class CouchDB:

    def __init__(self, url, thread_speak, start_time):
        """set initial values to vars and start radio"""

        self.db_url = url
        self.speak = thread_speak
        self.databases = mbox.databases

        self.logging = logging.getLogger("couch-db")
        self.logging.setLevel = stage.logging_level
        self.logging.info("Connect CouchDB ... " + self.db_url + " ... " + start_time)

        connects2db = 0
        max_connects = 30

        while connects2db < max_connects + 1:

            if connects2db == 8 or connects2db == 15 or connects2db == 25:
                self.speak.speak_message("WAITING-FOR-DB")

            try:
                self.logging.info(" - Try to connect to CouchDB")
                response = requests.get(self.db_url)
                connects2db = max_connects + 1

            except requests.exceptions.RequestException as e:
                connects2db += 1
                self.logging.warning(" - Waiting 5s for next connect to CouchDB: " + str(connects2db) + "/" + str(max_connects))
                self.logging.warning("   -> " + str(e))
                time.sleep(5)

            if connects2db == max_connects:
                self.speak.speak_message("NO-DB-CONNECTION")
                time.sleep(1)
                if stage.speak_ask_whom != "ASK--FOR-HELP":
                    self.speak.speak_message(stage.speak_ask_whom)

                self.logging.warning("Error connecting to CouchDB, give up.")
                sys.exit(1)

        self.database = couchdb.Server(self.db_url)
        self.check_db()

        self.logging.info("Connected.")
        self.changed_data = False
        self.cache = {}
        self.keys = []
        self.fill_cache()

    def check_db(self):
        """
        Check if required databases exist, and create if not
        """
        self.logging.info(" - Check if DB exist ... ")
        self.keys = []
        for cat_key in self.databases:
            for db_key in self.databases[cat_key]:
                if db_key in self.database and "main" in self.database[db_key]:
                    self.logging.debug("  OK: DB " + db_key + " exists.")
                else:
                    self.logging.info("  -> DB " + db_key + " have to be created ...")
                    try:
                        self.create(db_key)
                    except Exception as e:
                        self.logging.error("  -> Could not create DB " + db_key + "! " + str(e))

    def fill_cache(self):
        """
        copy all databases to cache
        """
        self.keys = []
        for key in self.database:
            self.cache[key] = self.read(key)
            self.keys.append(key)

    def create(self, db_key):
        """
        create database
        """
        self.logging.info("   -> create DB " + db_key)
        if db_key in self.database:
            self.logging.warning("   -> DB " + db_key + " exists.")
            db = self.database[db_key]
        else:
            try:
                db = self.database.create(db_key)
            except Exception as e:
                self.logging.error("   -> Could not create DB " + db_key + "! " + str(e))
                return

        # create initial data
        if "main" in self.database[db_key]:
            self.logging.warning("CouchDB - Already data in " + db_key + "!")
            return
        else:
            doc = db.get("main")
            if doc is None:
                doc = {
                    '_id': 'main',
                    'type': db_key,
                    'time': time.time(),
                    'change': 'new',
                    'data': {}
                }
            try:
                db.save(doc)
            except Exception as e:
                self.logging.error("CouchDB - Could not save after create: " + db_key + "  " + str(e))
                return

        # success
        self.logging.info("  -> DB created: " + db_key + " " + str(time.time()))
        return

    def read(self, db_key, entry_key=""):
        """
        read data from database and add to/update in cache
        """
        start_time = time.time()
        if db_key.startswith("_"):
            return

        elif db_key in self.database:

            self.logging.debug("CouchDB read: " + db_key + " - " + str(int(start_time - time.time())) + "s")

            try:
                db = self.database[db_key]
                if entry_key == "":
                    return db["main"]["data"].copy()
                elif entry_key in db["main"]["data"]:
                    return db["main"]["data"][entry_key].copy()

            except Exception as e:
                self.logging.error("CouchDB ERROR read: " + db_key + "/" + entry_key + " - " + str(e))

        else:
            self.logging.warning("CouchDB ERROR read: " + db_key + " - " + str(int(start_time - time.time())) + "s")
            self.create(db_key)
            return self.database[db_key]["main"]["data"]

    def read_group(self, group_key):
        """
        read complete table/group from database (e.g. radio, albums, ...)
        """
        data = {}
        try:
            for key in self.databases[group_key]:
                data[key] = self.read(key)
            self.changed_data = False

        except Exception as e:
            self.logging.warning("CouchDB ERROR read group: " + group_key + " " + str(time.time()) + " - " + str(e))

        return data

    def read_cache(self, db_key, entry_key=""):
        """
        return data from cache
        """
        if entry_key == "" and db_key in self.cache:
            self.logging.debug("CouchDB read cache: " + db_key + " " + str(time.time()))
            return self.cache[db_key].copy()
        elif db_key in self.cache and entry_key in self.cache[db_key]:
            self.logging.debug("CouchDB read cache: " + db_key + "/" + entry_key + "/" + (time.time()))
            return self.cache[db_key][entry_key].copy()
        else:
            self.logging.warning("CouchDB read cache: " + db_key + " doesn't exist in cache")
            return

    def write(self, key, data):
        """
        write data to database
        """
        self.changed_data = True
        if key not in self.database:
            self.database.create(key)
        db = self.database[key]
        doc = db.get("main")
        if doc is None:
            doc = {
                '_id': 'main',
                'type': key,
                'time': time.time(),
                'change': 'new',
                'data': data
            }
        else:
            doc["data"] = data
            doc['time'] = time.time()
            doc['change'] = 'save changes'

        try:
            db.save(doc)
        except Exception as e:
            self.logging.warning("CouchDB ERROR save: " + key + " " + str(e))
            return
        self.cache[key] = self.read(key)

        self.logging.debug("CouchDB save: " + key + " " + str(time.time()))
        return

    def backup_to_json(self):
        """
        write all databases to JSON files as backup
        """
        self.logging.info("BACKUP to JSON")
        for db_key in self.databases:
            for key in self.databases[db_key]:
                db = self.database[key]
                doc = db.get("main")
                json_db.write(key, doc["data"])

    def restore_from_json(self):
        """
        restore databases from JSON files, where files exist
        """
        self.logging.info("RESTORE from JSON")
        self.changed_data = True
        for db_key in self.databases:
            for key in self.databases[db_key]:
                txt = json_db.read(key)
                db = self.database[key]
                doc = db.get("main")
                if doc is None:
                    doc = {
                        '_id': 'main',
                        'type': key,
                        'time': time.time(),
                        'change': 'restore backup',
                        'data': txt
                    }
                else:
                    doc["data"] = txt
                    doc['time'] = time.time()
                    doc['change'] = 'restore backup'

                try:
                    db.save(doc)
                    self.logging.warning("save: ..." + key)
                except Exception as e:
                    self.logging.error("save ERROR: " + key + " - " + str(e))
                    return
