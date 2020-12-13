# ---------------------------------
# mbox Stage Configuration
# ---------------------------------
# ${THIS_IS_THE_PROJECT_TEMPLATE}
# ---------------------------------
# this script will be replace by
# the rollout script for PROD stage


rollout        = "${MBOX_CURRENT_STAGE}"

data_dir       = "${MBOX_DIR_DATA}"
data_backup    = "${MBOX_DIR_DATA}/couchdb_backup/"
data_db        = "http://${MBOX_DB_USER}:${MBOX_DB_PASSWORD}@${MBOX_DATABASE_SERVER}:${MBOX_DATABASE_PORT}/"
data_db_test   = "http://${MBOX_DB_USER}:${MBOX_DB_PASSWORD}@${MBOX_DOCKER_DATABASE}:${MBOX_DATABASE_PORT}/"


mount_system   = "${MBOX_MOUNT_SYSTEM}"
mount_data     = "${MBOX_MOUNT_DATA}"

demo_card      = "${MBOX_RFID_DEMOCARD}"

language       = "${MBOX_LANGUAGE}"
speak_msg      = "${MBOX_SPEEK_MSG}"
speak_ask_whom = "ASK-${MBOX_SPEEK_ASK_WHOM}-FOR-HELP"

server_port    = ${MBOX_SERVER_PORT}
server_ip      = "${MBOX_DATABASE_SERVER}"
server_dns     = [ "${DNS01}","${DNS02}","${DNS03}"]

log_level      = "${MBOX_LOGLEVEL}"

# ---------------------------------

if rollout == "test": test  = True
else:                 test  = False


# ---------------------------------

import logging

def init_logging(string,logfilename="",stage="test"):
    """
    Initialize logging and print software title
    When stage != "test" write and filename is specified, write log into file
    """
    
    if (log_level == "debug"): 
      logging.basicConfig(level=logging.DEBUG)       # DEBUG, INFO, WARNING, ERROR, CRITICAL
      logging.info("Start - Log-Level DEBUG ...")
      logging.info("--------------------------------")
      logging.info(string)
      logging.info("--------------------------------")       
       
    elif (log_level == "info" and stage != "test"): 
      if (logfilename != "" and stage != "test"):
         logging.basicConfig(filename=logfilename,
                       filemode='a',
                       format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                       datefmt='%d.%m.%y %H:%M:%S',
                       level=logging.INFO)    
      else:
         logging.basicConfig(level=logging.INFO)

      logging.info("Start - Log-Level INFO ...")
      logging.info("--------------------------------")
      logging.info(string)
      logging.info("--------------------------------")       
    
   
    elif (log_level == "warning"): 
      if (logfilename != "" and stage != "test"):
         logging.basicConfig(filename=logfilename,
                       filemode='a',
                       format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                       datefmt='%d.%m.%y %H:%M:%S',
                       level=logging.WARNING)    
      else:
         logging.basicConfig(level=logging.WARNING)

      logging.warning("Start ["+string+"] - Log-Level WARNING ...")
      
    else: 
      if (logfilename != "" and stage != "test"):
         logging.basicConfig(filename=logfilename,
                       filemode='a',
                       format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                       datefmt='%d.%m.%y %H:%M:%S',
                       level=logging.ERROR)    
      else:
         logging.basicConfig(level=logging.ERROR)
         
      logging.error("Start ["+string+"] Log-Level ERROR ...")
           
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.WARN)
                      


