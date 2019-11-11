# ---------------------------------
# mbox Stage Configuration
# ---------------------------------
# Please edit not here, but the orginial configuration file. This files is created using a template.
# ---------------------------------
# this script will be replace by
# the rollout script for PROD stage

rollout      = "test"

data_dir     = "/projects_data/test"
data_backup  = "/projects_data/test/couchdb_backup/"
data_db      = "http://mbox:mbox@localhost:5106/"

mount_system = "/"
mount_data   = "/mnt/usb"

server_port = 5006

if rollout == "test": test  = True
else:                 test  = False

#### -> add more dir data

