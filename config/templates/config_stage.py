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
log_filename     = "${MBOX_LOGFILENAME}"
logging_level    = ""
log_to_file      = "${MBOX_LOG2FILE}"

# ---------------------------------

if rollout == "test": test  = True
else:                 test  = False

