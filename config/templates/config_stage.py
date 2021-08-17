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
data_db_ip     = "${MBOX_NETWORK}.1"
data_db        = "http://${MBOX_DB_USER}:${MBOX_DB_PASSWORD}@"+data_db_ip+":${MBOX_DATABASE_PORT}/"

mount_system   = "${MBOX_MOUNT_SYSTEM}"
mount_data     = "${MBOX_MOUNT_DATA}"

demo_card      = "${MBOX_RFID_DEMOCARD}"

language       = "${MBOX_LANGUAGE}"
speak_msg      = "${MBOX_SPEEK_MSG}"
speak_ask_whom = "ASK-${MBOX_SPEEK_ASK_WHOM}-FOR-HELP"

server_port      = ${MBOX_SERVER_PORT}
server_ip        = data_db_ip
server_dns       = [ "${DNS01}","${DNS02}","${DNS03}"]

log_level        = "${MBOX_LOGLEVEL}"
log_to_file      = "${MBOX_LOG2FILE}"

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

    if   log_level == "debug":   level = logging.DEBUG
    elif log_level == "info":    level = logging.INFO
    elif log_level == "warning": level = logging.WARNING
    elif log_level == "error":   level = logging.ERROR
    
    if log_to_file == "yes":
       logging.basicConfig(filename=logfilename,
                       filemode='a',
                       format='%(asctime)s %(name)s %(levelname)s %(message)s',
                       datefmt='%d.%m.%y %H:%M:%S',
                       level=level)
    else:
       logging.basicConfig(level=level)

    if log_level == "debug" or log_level == "info":
       logging.info("Start - Log-Level "+log_level+" ...")
       logging.info("--------------------------------")
       logging.info(string)
       logging.info("--------------------------------")       
    elif log_level == "warning":
       logging.warning("Start: "+string+" ("+log_level+") ...")
    else:
       logging.error("Start: "+string+" ("+log_level+") ...")
                  
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.WARN)
                      


