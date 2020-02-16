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
speek_msg      = "${MBOX_SPEEK_MSG}"
speek_ask_whom = "ASK-${MBOX_SPEEK_ASK_WHOM}-FOR-HELP"

server_port    = ${MBOX_SERVER_PORT}
server_ip      = "${MBOX_DATABASE_SERVER}"
server_dns     = [ "${DNS01}","${DNS02}","${DNS03}"]

if rollout == "test": test  = True
else:                 test  = False

#### -> add more dir data

