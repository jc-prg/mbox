import modules.jcJson          as jcJSON
import modules.config_stage    as stage
import modules.config_mbox     as mbox
import modules.speakmsg        as speak

import logging, time, uuid
import couchdb, requests, json


#-------------------------------------------------
# Database Definition
#-------------------------------------------------

database   = couchdb.Server(stage.data_db)
databases  = mbox.databases

#---------------------------------------------
# database access
#---------------------------------------------

class jcCouchDB ():

   def __init__(self):
      '''set initial values to vars and start radio'''

      global databases

      logging.debug("Connect to CouchDB: "+stage.data_db)

      connects2db  = 0
      max_connects = 30

      self.speak = speak.speakThread(4, "Thread speak", 1, "")  #  jcJSON.read("music"), jcJSON.read("radio"))
      self.speak.start()

      while connects2db < max_connects+1:

          if connects2db == 8 or connects2db == 15 or connects2db == 25:
              self.speak.speak_message("WAITING-FOR-DB")

          try:
              logging.info("Try to connect to CouchDB")
              response = requests.get(stage.data_db)
              connects2db = max_connects+1

          except requests.exceptions.RequestException as e:
              connects2db += 1
              logging.warning("Waiting 5s for connect to CouchDB: " + str(connects2db) + "/" + str(max_connects) + " ("+stage.data_db+")")
              logging.info(   "                      ... to CouchDB: " + stage.data_db)

              time.sleep(5)

          if connects2db == max_connects:

              self.speak.speak_message("NO-DB-CONNECTION")
              time.sleep(1)
              if stage.speak_ask_whom != "ASK--FOR-HELP":
                 self.speak.speak_message(stage.speak_ask_whom)

              logging.warning("Error connecting to CouchDB, give up.")
              sys.exit(1)  ### -> LEADS TO AN ERROR !!!


      self.database      = couchdb.Server(stage.data_db)
      self.databases     = databases
      self.check_db()

      self.changed_data  = False
      self.cache         = {}
      self.keys          = []
      self.fill_cache()
      

      logging.debug("Connect to CouchDB: "+stage.data_db)

   #--------------------------------------

   def check_db(self):
       self.keys = []
       for cat_key in self.databases:
           for db_key in self.databases[cat_key]:
               if db_key in self.database and "main" in self.database[db_key]:
                   logging.debug("OK: DB " + db_key + " exists.")
               else:
                   logging.debug("OK: DB " + db_key + " have to be created ...")
                   try:
                     self.create(db_key)
                   except Exception as e:
                     logging.error("CouchDB - Could not create DB " + db_key + "! " + str(e))

   #--------------------------------------

   def fill_cache(self):
       self.keys = []
       for key in self.database:
           self.cache[key] = self.read(key)
           self.keys.append(key)

   #--------------------------------------

   def create(self,db_key):

       # create DB
       if db_key in self.database:
           logging.warn("CouchDB "+db_key+" exists.")
           db = self.database[db_key]
       else:
           try:
               db = self.database.create(db_key)
           except Exception as e:
               logging.error("CouchDB - Could not create DB "+db_key+"! " + str(e))
               return

       # create initial data
       if "main" in self.database[db_key]:
           logging.warn("CouchDB - Already data in "+db_key+"!")
           return
       else:
           doc = db.get("main")
           if doc is None:
              doc = {
              '_id'    : 'main',
              'type'   : db_key,
              'time'   : time.time(),
              'change' : 'new',
              'data'   : {}
              }
           try:
               db.save(doc)
           except Exception as e:
               logging.error("CouchDB - Could not save after create: " + db_key + "  " + str(e))
               return

       # success
       logging.info("CouchDB created: " + db_key + " " +str(time.time()))
       return

   #--------------------------------------

   def readGroup(self,group_key):
       data = {}
       try:
           for key in self.databases[group_key]:
               data[key] = self.read(key)
           self.changed_data = False

       except:
           logging.warn("CouchDB ERROR read group: " + db_key + " " +str(time.time()))

       return data


   #--------------------------------------

   def read_cache(self,db_key,entry_key=""):

       if entry_key == "" and db_key in self.cache:
           return self.cache[db_key]

       elif db_key in self.cache:
           return self.cache[db_key][entry_key]

       logging.info("CouchDB read cache: " + db_key + " " +str(time.time()))

       return

   #--------------------------------------

   def read(self,db_key,entry_key=""):

       start_time = time.time()
       if db_key in self.database:

           logging.info("CouchDB read: " + db_key + " - " + str(int(start_time - time.time())) + "s")
           db = self.database[db_key]
           self.cache[db_key] = db

           if entry_key == "":                    return db["main"]["data"]
           elif entry_key in db["main"]["data"]:  return db["main"]["data"][entry_key]

       else:
           logging.warn("CouchDB ERROR read: " + db_key + " - " + str(int(start_time - time.time())) + "s")
           data = {}
           self.create(db_key) #, data)
           return self.database[db_key]["main"]["data"]


   #--------------------------------------
   #################### FEHLER ###########

   def write(self,key,data):
       self.changed_data = True
       try:
           db = self.database[key]
       except:
           db = self.database.create(key)
           db = self.database[key]

       doc = db.get("main")
       if doc is None:
            doc = {
              '_id'    : 'main',
              'type'   : key,
              'time'   : time.time(),
              'change' : 'new',
              'data'   : data
              }
       else:
            doc["data"]   = data
            doc['time']   = time.time()
            doc['change'] = 'save changes'

       try:
           db.save(doc)
       except Exception as e:
           logging.warn("CouchDB ERROR save: " + key + " " + str(e))
           return
       self.cache[key] = self.read(key)

       logging.info("CouchDB save: " + key + " " +str(time.time()))
       return

   #--------------------------------------

   def backupToJson(self):
       logging.info("BACKUP to JSON")
       for db_key in self.databases:
           for key in self.databases[db_key]:
               db  = self.database[key]
               doc = db.get("main")
               jcJSON.write(key,doc["data"])

   def restoreFromJson(self):
       logging.info("RESTORE from JSON")
       self.changed_data = True
       for db_key in self.databases:
           for key in self.databases[db_key]:
               txt = jcJSON.read(key)
               db  = self.database[key]
               doc = db.get("main")
               if doc is None:
                  doc = {
                        '_id'    : 'main',
                        'type'   : key,
                        'time'   : time.time(),
                        'change' : 'restore backup',
                        'data'   : txt
                        }
               else:
                   doc["data"]   = txt
                   doc['time']   = time.time()
                   doc['change'] = 'restore backup'

               try:
                   db.save(doc)
                   logging.warn("save: ..." + key)
               except:
                   logging.error("save ERROR: " + key)
                   return
          

