# ---------------------------------
# mbox Stage Configuration
# ---------------------------------
# ${THIS_IS_THE_PROJECT_TEMPLATE}
# ---------------------------------
# this script will be replace by
# the rollout script for PROD stage

rollout      = "${MBOX_CURRENT_STAGE}"

data_dir     = "${MBOX_DIR_DATA}"
data_backup  = "${MBOX_DIR_DATA}/couchdb_backup/"
data_db      = "http://${MBOX_DB_USER}:${MBOX_DB_PASSWORD}@localhost:${MBOX_DATABASE_PORT}/"

mount_system = "${MBOX_MOUNT_SYSTEM}"
mount_data   = "${MBOX_MOUNT_DATA}"

server_port = ${MBOX_SERVER_PORT}

if rollout == "test": test  = True
else:                 test  = False

#### -> add more dir data

