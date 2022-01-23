import modules.jcJson          as jcJSON
import modules.config_stage    as stage
import modules.config_mbox     as mbox
import modules.music_speak     as speak
from   modules.jcRunCmd        import *

import logging, time, uuid
import couchdb, requests, json

cdb_logging = logging.getLogger("couch-db")
cdb_logging.setLevel = stage.logging_level

#-------------------------------------------------

def createDB_URL():
    '''
    get IP address for internal device
    '''
    command = "/sbin/ip -o -4 addr list "+stage.server_ip_device+" | awk '{print $4}' | cut -d/ -f1"
    ip, err = runCmd(command)
    db_url  = "http://"+stage.data_db_auth+"@"+ip+":"+stage.server_port+"/"
    cdb_logging.info("connectionInternalIP: "+db_url)
    return ip, db_url
    

#-------------------------------------------------
# Database Definition
#-------------------------------------------------

#db_ip, db_url    = createDB_URL()
#database   = couchdb.Server(db_url)
#database   = couchdb.Server(stage.data_db_test)
#database   = couchdb.Server(stage.data_db)
#databases  = mbox.databases

#---------------------------------------------
# database access
#---------------------------------------------

class jcCouchDB ():

   def __init__(self, url):
      '''set initial values to vars and start radio'''

      self.db_url     = url
      self.databases  = mbox.databases

      cdb_logging.debug("Connect to CouchDB: "+self.db_url)

      connects2db  = 0
      max_connects = 30

      self.speak = speak.speakThread(4, "Thread speak", 1, "")  #  jcJSON.read("music"), jcJSON.read("radio"))
      self.speak.start()

      while connects2db < max_connects+1:

          if connects2db == 8 or connects2db == 15 or connects2db == 25:
              self.speak.speak_message("WAITING-FOR-DB")

          try:
              cdb_logging.info("Try to connect to CouchDB")
              response = requests.get(self.db_url)
              connects2db = max_connects+1

          except requests.exceptions.RequestException as e:
              connects2db += 1
              cdb_logging.warning("Waiting 5s for connect to CouchDB: " + str(connects2db) + "/" + str(max_connects) + " ("+self.db_url+")")
              cdb_logging.info(   "                      ... to CouchDB: " + self.db_url)

              time.sleep(5)

          if connects2db == max_connects:

              self.speak.speak_message("NO-DB-CONNECTION")
              time.sleep(1)
              if stage.speak_ask_whom != "ASK--FOR-HELP":
                 self.speak.speak_message(stage.speak_ask_whom)

              cdb_logging.warning("Error connecting to CouchDB, give up.")
              sys.exit(1)  ### -> LEADS TO AN ERROR !!!


      self.database      = couchdb.Server(self.db_url)
      self.check_db()

      self.changed_data  = False
      self.cache         = {}
      self.keys          = []
      self.fill_cache()
      

      cdb_logging.debug("Connect to CouchDB: "+self.db_url)

   #--------------------------------------

   def check_db(self):
       self.keys = []
       for cat_key in self.databases:
           for db_key in self.databases[cat_key]:
               if db_key in self.database and "main" in self.database[db_key]:
                   cdb_logging.debug("OK: DB " + db_key + " exists.")
               else:
                   cdb_logging.debug("OK: DB " + db_key + " have to be created ...")
                   try:
                     self.create(db_key)
                   except Exception as e:
                     cdb_logging.error("CouchDB - Could not create DB " + db_key + "! " + str(e))

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
           cdb_logging.warn("CouchDB "+db_key+" exists.")
           db = self.database[db_key]
       else:
           try:
               db = self.database.create(db_key)
           except Exception as e:
               cdb_logging.error("CouchDB - Could not create DB "+db_key+"! " + str(e))
               return

       # create initial data
       if "main" in self.database[db_key]:
           cdb_logging.warn("CouchDB - Already data in "+db_key+"!")
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
               cdb_logging.error("CouchDB - Could not save after create: " + db_key + "  " + str(e))
               return

       # success
       cdb_logging.info("CouchDB created: " + db_key + " " +str(time.time()))
       return

   #--------------------------------------

   def readGroup(self,group_key):
       data = {}
       try:
           for key in self.databases[group_key]:
               data[key] = self.read(key)
           self.changed_data = False

       except:
           cdb_logging.warn("CouchDB ERROR read group: " + db_key + " " +str(time.time()))

       return data


   #--------------------------------------

   def read_cache(self,db_key,entry_key=""):

       if entry_key == "" and db_key in self.cache:
           return self.cache[db_key]

       elif db_key in self.cache:
           return self.cache[db_key][entry_key]

       cdb_logging.debug("CouchDB read cache: " + db_key + " " +str(time.time()))

       return

   #--------------------------------------

   def read(self,db_key,entry_key=""):

       start_time = time.time()
       if db_key in self.database:

           cdb_logging.debug("CouchDB read: " + db_key + " - " + str(int(start_time - time.time())) + "s")
           
           try:
             db = self.database[db_key]
             self.cache[db_key] = db
             if entry_key == "":                    return db["main"]["data"]
             elif entry_key in db["main"]["data"]:  return db["main"]["data"][entry_key]
             
           except Exception as e:
             if (db_key != "_users" and db_key != "_replicator"):
               cdb_logging.error("CouchDB ERROR read: " + db_key + "/" + entry_key + " - " + str(e))


       else:
           cdb_logging.warn("CouchDB ERROR read: " + db_key + " - " + str(int(start_time - time.time())) + "s")
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
           cdb_logging.warn("CouchDB ERROR save: " + key + " " + str(e))
           return
       self.cache[key] = self.read(key)

       cdb_logging.debug("CouchDB save: " + key + " " +str(time.time()))
       return

   #--------------------------------------

   def backupToJson(self):
       cdb_logging.info("BACKUP to JSON")
       for db_key in self.databases:
           for key in self.databases[db_key]:
               db  = self.database[key]
               doc = db.get("main")
               jcJSON.write(key,doc["data"])

   def restoreFromJson(self):
       cdb_logging.info("RESTORE from JSON")
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
                   cdb_logging.warn("save: ..." + key)
               except:
                   cdb_logging.error("save ERROR: " + key)
                   return
          

