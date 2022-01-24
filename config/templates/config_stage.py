# ---------------------------------
# mbox Stage Configuration
# ---------------------------------
# ${THIS_IS_THE_PROJECT_TEMPLATE}
# ---------------------------------
# template:
# ./config/templates/config_stage.py
# create configuration:
# $ cd ./config
# $ ./create

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

server_port    = ${MBOX_SERVER_PORT}
server_ip      = data_db_ip
server_dns     = [ "${DNS01}","${DNS02}","${DNS03}"]

log_level         = "${MBOX_LOGLEVEL}"
log_to_file       = "${MBOX_LOG2FILE}"
log_filename      = "${MBOX_LOG2FILE_PATH}"

log_level_data    = "${MBOX_LOGLEVEL_LOAD}"
log_to_file_data  = "${MBOX_LOG2FILE_LOAD}"
log_filename_data = "${MBOX_LOG2FILE_LOAD_PATH}"

logging_level      = ""
logging_level_data = ""

# ---------------------------------

if rollout == "test": test  = True
else:                 test  = False

# ---------------------------------

import logging

log_level      = log_level.upper()
log_level_data = log_level_data.upper()

if   log_level_data == "DEBUG":    logging_level_data = logging.DEBUG
elif log_level_data == "INFO":     logging_level_data = logging.INFO
elif log_level_data == "WARNING":  logging_level_data = logging.WARNING
elif log_level_data == "ERROR":    logging_level_data = logging.ERROR
elif log_level_data == "CRITICAL": logging_level_data = logging.CRITICAL
    
if   log_level == "DEBUG":         logging_level = logging.DEBUG
elif log_level == "INFO":          logging_level = logging.INFO
elif log_level == "WARNING":       logging_level = logging.WARNING
elif log_level == "ERROR":         logging_level = logging.ERROR
elif log_level == "CRITICAL":      logging_level = logging.CRITICAL

